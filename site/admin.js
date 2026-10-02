(() => {
  const config = window.AUN_CONFIG || {};
  const status = document.querySelector('#admin-status');
  const dashboard = document.querySelector('#admin-dashboard');
  const topAgents = document.querySelector('#top-agents');
  const adminClaims = document.querySelector('#admin-claims');

  document.querySelector('#product-analytics-state').textContent =
    config.productAnalyticsEnabled ? 'configured' : 'not configured';
  document.querySelector('#cloudflare-state').textContent =
    config.cloudflareWebAnalyticsToken ? 'configured' : 'not configured';

  if (!config.authEnabled || !window.supabase) {
    status.textContent = 'Auth/backend is not configured yet. Public site remains operational.';
    return;
  }

  const client = window.supabase.createClient(
    config.supabaseUrl,
    config.supabasePublishableKey
  );

  function setMetric(id, value) {
    document.querySelector(id).textContent = Number(value || 0).toLocaleString();
  }

  function esc(value) {
    return String(value ?? '').replace(/[&<>'"]/g, ch => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    })[ch]);
  }

  async function loadClaims() {
    const result = await client
      .from('agent_claims')
      .select(
        'id,agent_id,repository,github_login,status,verification_method,created_at,verified_at,verification_notes'
      )
      .order('created_at', { ascending: false })
      .limit(50);

    if (result.error) {
      adminClaims.innerHTML =
        '<p class="empty">Claim queue unavailable: ' +
        esc(result.error.message) + '</p>';
      return;
    }

    const rows = result.data || [];
    adminClaims.innerHTML = rows.length
      ? rows.map(row => {
          const actions = [];
          if (row.status === 'PENDING_GITHUB_VERIFICATION') {
            actions.push(
              '<button class="text-button" data-claim-action="verify" data-claim-id="' +
              esc(row.id) + '" type="button">Manual verify</button>'
            );
            actions.push(
              '<button class="text-button danger-link" data-claim-action="reject" data-claim-id="' +
              esc(row.id) + '" type="button">Reject</button>'
            );
          } else if (row.status === 'VERIFIED_MAINTAINER') {
            actions.push(
              '<button class="text-button danger-link" data-claim-action="revoke" data-claim-id="' +
              esc(row.id) + '" type="button">Revoke</button>'
            );
          }

          return '<article class="panel claim-review-row">' +
            '<div><span class="panel-label">' + esc(row.status) + '</span>' +
            '<strong>' + esc(row.agent_id) + '</strong>' +
            '<span>' + esc(row.repository || '') + '</span>' +
            '<span>GitHub: ' + esc(row.github_login || 'unknown') + '</span></div>' +
            '<div class="claim-review-actions">' + actions.join('') + '</div>' +
          '</article>';
        }).join('')
      : '<p class="empty">No maintainer claims yet.</p>';

    document.querySelectorAll('[data-claim-action]').forEach(button => {
      button.addEventListener('click', async () => {
        const action = button.dataset.claimAction;
        const claimId = button.dataset.claimId;
        const note = prompt('Review note (optional):') || '';
        const now = new Date().toISOString();

        let patch;
        if (action === 'verify') {
          patch = {
            status: 'VERIFIED_MAINTAINER',
            verification_method: 'manual_review',
            verified_at: now,
            verification_notes: {
              proof: 'manual_admin_review',
              note,
              reviewed_at: now
            }
          };
        } else if (action === 'reject') {
          patch = {
            status: 'REJECTED',
            verification_method: 'manual_review',
            verification_notes: {
              proof: 'manual_admin_reject',
              note,
              reviewed_at: now
            }
          };
        } else if (action === 'revoke') {
          patch = {
            status: 'REVOKED',
            verification_method: 'manual_review',
            verification_notes: {
              proof: 'manual_admin_revoke',
              note,
              reviewed_at: now
            }
          };
        } else {
          return;
        }

        const update = await client
          .from('agent_claims')
          .update(patch)
          .eq('id', claimId);

        if (update.error) {
          alert('Claim update failed: ' + update.error.message);
          return;
        }

        await loadClaims();
        await load();
      });
    });
  }

  async function load() {
    status.textContent = 'Checking admin authorization…';

    const { data: sessionData } = await client.auth.getSession();
    if (!sessionData.session) {
      status.innerHTML = 'Admin sign-in required. <a href="./account.html">Open account page</a>.';
      dashboard.hidden = true;
      return;
    }

    const metrics = await client.rpc('admin_dashboard_metrics');
    if (metrics.error) {
      status.textContent = 'Access denied or admin metrics unavailable: ' + metrics.error.message;
      dashboard.hidden = true;
      return;
    }

    const m = metrics.data || {};
    setMetric('#m-live', m.live_sessions);
    setMetric('#m-views', m.today_page_views);
    setMetric('#m-users', m.registered_users);
    setMetric('#m-signups', m.today_signups);
    setMetric('#m-claims', m.today_claim_starts);
    setMetric('#m-verified', m.verified_maintainer_claims);
    setMetric('#m-compares', m.today_comparisons);
    setMetric('#m-events', m.today_events);

    const top = await client.rpc('admin_top_agents', { hours_back: 24 });
    if (top.error) {
      topAgents.textContent = top.error.message;
    } else {
      topAgents.innerHTML = (top.data || []).length
        ? top.data.map((row, index) =>
            '<div><b>' + (index + 1) + '</b><span>' +
            String(row.agent_id || 'unknown') +
            '</span><strong>' + Number(row.event_count || 0).toLocaleString() +
            '</strong></div>'
          ).join('')
        : '<p class="empty">No agent events yet.</p>';
    }

    await loadClaims();

    status.textContent = 'Admin authorization verified.';
    dashboard.hidden = false;
  }

  document.querySelector('#refresh-admin').addEventListener('click', load);
  load();
})();
