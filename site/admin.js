(() => {
  const config = window.AUN_CONFIG || {};
  const status = document.querySelector('#admin-status');
  const dashboard = document.querySelector('#admin-dashboard');
  const topAgents = document.querySelector('#top-agents');

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
    config.supabaseAnonKey
  );

  function setMetric(id, value) {
    document.querySelector(id).textContent = Number(value || 0).toLocaleString();
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

    status.textContent = 'Admin authorization verified.';
    dashboard.hidden = false;
  }

  document.querySelector('#refresh-admin').addEventListener('click', load);
  load();
})();
