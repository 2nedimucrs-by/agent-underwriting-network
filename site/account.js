(() => {
  const config = window.AUN_CONFIG || {};
  const disabled = document.querySelector('#auth-disabled');
  const signedOut = document.querySelector('#signed-out');
  const signedIn = document.querySelector('#signed-in');
  const githubLogin = document.querySelector('#github-login');
  const magicForm = document.querySelector('#magic-form');
  const magicStatus = document.querySelector('#magic-status');
  const userName = document.querySelector('#user-name');
  const userEmail = document.querySelector('#user-email');
  const signOut = document.querySelector('#sign-out');
  const claimPanel = document.querySelector('#claim-panel');
  const claimAgent = document.querySelector('#claim-agent');
  const submitClaim = document.querySelector('#submit-claim');
  const claimStatus = document.querySelector('#claim-status');
  const deleteRequest = document.querySelector('#delete-request');
  const deleteStatus = document.querySelector('#delete-status');
  const savedAgents = document.querySelector('#saved-agents');
  const agentAlerts = document.querySelector('#agent-alerts');
  const workspaceStatus = document.querySelector('#workspace-status');

  if (!config.authEnabled || !config.supabaseUrl || !config.supabasePublishableKey || !window.supabase) {
    disabled.hidden = false;
    disabled.style.display = '';
    signedOut.hidden = false;
    signedOut.style.display = '';
    signedIn.hidden = true;
    signedIn.style.display = 'none';
    signedOut.querySelectorAll('button,input').forEach(el => el.disabled = true);
    return;
  }

  disabled.hidden = true;
  disabled.style.display = 'none';

  const client = window.supabase.createClient(
    config.supabaseUrl,
    config.supabasePublishableKey
  );

  const params = new URLSearchParams(location.search);
  const incomingClaimId = params.get('claim');
  const incomingWatchId = params.get('watch');
  if (incomingClaimId) {
    sessionStorage.setItem('aun_pending_claim', incomingClaimId);
  }
  if (incomingWatchId) {
    sessionStorage.setItem('aun_pending_watch', incomingWatchId);
  }
  const claimId = incomingClaimId || sessionStorage.getItem('aun_pending_claim');
  const watchId = incomingWatchId || sessionStorage.getItem('aun_pending_watch');

  function githubLoginFromUser(user) {
    return user?.user_metadata?.user_name ||
      user?.user_metadata?.preferred_username ||
      null;
  }

  async function render(session) {
    const user = session?.user || null;
    signedOut.hidden = Boolean(user);
    signedOut.style.display = user ? 'none' : '';
    signedIn.hidden = !user;
    signedIn.style.display = user ? '' : 'none';

    if (!user) {
      claimPanel.hidden = true;
      claimPanel.style.display = 'none';
      return;
    }

    userName.textContent = githubLoginFromUser(user) || 'Signed-in user';
    userEmail.textContent = user.email || 'No email exposed by provider';

    if (claimId) {
      claimPanel.hidden = false;
      claimPanel.style.display = '';
      claimAgent.textContent = claimId;
    }

    await applyPendingWatch(user);
    await loadWorkspace(user);
  }

  async function applyPendingWatch(user) {
    if (!watchId) return;

    workspaceStatus.textContent = 'Saving watch…';

    const saved = await client
      .from('saved_agents')
      .upsert(
        { user_id: user.id, agent_id: watchId },
        { onConflict: 'user_id,agent_id' }
      );

    if (saved.error) {
      workspaceStatus.textContent = saved.error.message;
      return;
    }

    const existing = await client
      .from('agent_alerts')
      .select('id')
      .eq('user_id', user.id)
      .eq('agent_id', watchId)
      .eq('alert_type', 'VERSION_DRIFT')
      .limit(1);

    if (!existing.error && !(existing.data || []).length) {
      await client
        .from('agent_alerts')
        .insert({
          user_id: user.id,
          agent_id: watchId,
          alert_type: 'VERSION_DRIFT',
          enabled: true
        });
    }

    sessionStorage.removeItem('aun_pending_watch');
    workspaceStatus.textContent = 'Agent saved and version-drift alert enabled.';

    if (window.AUNAnalytics) {
      window.AUNAnalytics.track('SAVE_AGENT', { agent_id: watchId });
      window.AUNAnalytics.track('ALERT_CREATE', { agent_id: watchId });
    }
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, ch => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    })[ch]);
  }

  async function loadWorkspace(user) {
    const saved = await client
      .from('saved_agents')
      .select('agent_id,created_at')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false });

    const alerts = await client
      .from('agent_alerts')
      .select('id,agent_id,alert_type,enabled,created_at')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false });

    if (saved.error || alerts.error) {
      workspaceStatus.textContent =
        saved.error?.message || alerts.error?.message || 'Workspace unavailable.';
      return;
    }

    const savedRows = saved.data || [];
    const alertRows = alerts.data || [];

    savedAgents.innerHTML = savedRows.length
      ? savedRows.map(row =>
          '<div class="workspace-row">' +
            '<span>' + escapeHtml(row.agent_id) + '</span>' +
            '<button class="text-button danger-link" data-unsave="' +
              escapeHtml(row.agent_id) + '" type="button">Remove</button>' +
          '</div>'
        ).join('')
      : '<p class="empty">No saved agents yet.</p>';

    agentAlerts.innerHTML = alertRows.length
      ? alertRows.map(row =>
          '<div class="workspace-row">' +
            '<span><strong>' + escapeHtml(row.alert_type) + '</strong><br>' +
              escapeHtml(row.agent_id) + '</span>' +
            '<button class="text-button" data-alert-id="' +
              escapeHtml(row.id) + '" data-alert-enabled="' +
              String(Boolean(row.enabled)) + '" type="button">' +
              (row.enabled ? 'Pause' : 'Enable') +
            '</button>' +
          '</div>'
        ).join('')
      : '<p class="empty">No alerts yet.</p>';

    workspaceStatus.textContent =
      savedRows.length + ' saved · ' +
      alertRows.filter(row => row.enabled).length + ' active alerts';

    document.querySelectorAll('[data-unsave]').forEach(button => {
      button.addEventListener('click', async () => {
        const agentId = button.dataset.unsave;
        await client
          .from('saved_agents')
          .delete()
          .eq('user_id', user.id)
          .eq('agent_id', agentId);
        await loadWorkspace(user);
      });
    });

    document.querySelectorAll('[data-alert-id]').forEach(button => {
      button.addEventListener('click', async () => {
        const enabled = button.dataset.alertEnabled === 'true';
        await client
          .from('agent_alerts')
          .update({ enabled: !enabled })
          .eq('user_id', user.id)
          .eq('id', button.dataset.alertId);
        await loadWorkspace(user);
      });
    });
  }

  async function currentSession() {
    const { data } = await client.auth.getSession();
    await render(data.session);
  }

  githubLogin.addEventListener('click', async () => {
    const redirectTo = location.origin + location.pathname;
    const { error } = await client.auth.signInWithOAuth({
      provider: 'github',
      options: { redirectTo }
    });
    if (error) magicStatus.textContent = error.message;
  });

  magicForm.addEventListener('submit', async event => {
    event.preventDefault();
    magicStatus.textContent = 'Sending…';
    const email = document.querySelector('#email').value.trim();
    const redirectTo = location.origin + location.pathname;
    const { error } = await client.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: redirectTo }
    });
    magicStatus.textContent = error
      ? error.message
      : 'Check your inbox for the secure sign-in link.';
  });

  signOut.addEventListener('click', async () => {
    await client.auth.signOut();
    await render(null);
  });

  submitClaim.addEventListener('click', async () => {
    claimStatus.textContent = 'Submitting…';
    const { data: sessionData } = await client.auth.getSession();
    const user = sessionData.session?.user;
    if (!user || !claimId) {
      claimStatus.textContent = 'Sign in before submitting a claim.';
      return;
    }

    const repository = claimId.startsWith('github:')
      ? claimId.slice('github:'.length)
      : null;

    if (window.AUNAnalytics) {
      window.AUNAnalytics.track('CLAIM_START', { agent_id: claimId });
    }

    const { data: claim, error } = await client
      .from('agent_claims')
      .upsert({
        user_id: user.id,
        agent_id: claimId,
        repository,
        github_login: githubLoginFromUser(user),
        status: 'PENDING_GITHUB_VERIFICATION',
        verification_method: 'github_oauth'
      }, { onConflict: 'user_id,agent_id' })
      .select('id,status')
      .single();

    if (error) {
      claimStatus.textContent = error.message;
      return;
    }

    claimStatus.textContent = 'Claim recorded. Checking maintainer proof…';

    const verification = await client.functions.invoke('verify-github-claim', {
      body: { claim_id: claim.id }
    });

    if (verification.error) {
      claimStatus.textContent =
        'Claim recorded as pending. Automatic verification is not available yet.';
      return;
    }

    if (verification.data?.status === 'VERIFIED_MAINTAINER') {
      claimStatus.textContent =
        'Maintainer identity verified. This does not verify the agent security or capability.';
      sessionStorage.removeItem('aun_pending_claim');
      if (window.AUNAnalytics) {
        window.AUNAnalytics.track('CLAIM_COMPLETE', { agent_id: claimId });
      }
      return;
    }

    claimStatus.textContent =
      verification.data?.reason ||
      'Claim remains pending for organization/collaborator verification.';
  });

  deleteRequest.addEventListener('click', async () => {
    if (!confirm('Create an account deletion request?')) return;

    deleteStatus.textContent = 'Submitting…';
    const { data: sessionData } = await client.auth.getSession();
    const user = sessionData.session?.user;
    if (!user) {
      deleteStatus.textContent = 'You are not signed in.';
      return;
    }

    const { error } = await client
      .from('account_deletion_requests')
      .insert({ user_id: user.id, status: 'PENDING' });

    deleteStatus.textContent = error
      ? error.message
      : 'Deletion request submitted.';
  });

  client.auth.onAuthStateChange((_event, session) => render(session));
  currentSession();
})();
