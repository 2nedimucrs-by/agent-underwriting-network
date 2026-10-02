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

  if (!config.authEnabled || !config.supabaseUrl || !config.supabaseAnonKey || !window.supabase) {
    disabled.hidden = false;
    signedOut.querySelectorAll('button,input').forEach(el => el.disabled = true);
    return;
  }

  const client = window.supabase.createClient(
    config.supabaseUrl,
    config.supabaseAnonKey
  );

  const params = new URLSearchParams(location.search);
  const claimId = params.get('claim');

  function githubLoginFromUser(user) {
    return user?.user_metadata?.user_name ||
      user?.user_metadata?.preferred_username ||
      null;
  }

  async function render(session) {
    const user = session?.user || null;
    signedOut.hidden = Boolean(user);
    signedIn.hidden = !user;

    if (!user) return;

    userName.textContent = githubLoginFromUser(user) || 'Signed-in user';
    userEmail.textContent = user.email || 'No email exposed by provider';

    if (claimId) {
      claimPanel.hidden = false;
      claimAgent.textContent = claimId;
    }
  }

  async function currentSession() {
    const { data } = await client.auth.getSession();
    await render(data.session);
  }

  githubLogin.addEventListener('click', async () => {
    const redirectTo = location.origin + location.pathname + location.search;
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
    const redirectTo = location.origin + location.pathname + location.search;
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

    const { error } = await client
      .from('agent_claims')
      .upsert({
        user_id: user.id,
        agent_id: claimId,
        repository,
        github_login: githubLoginFromUser(user),
        status: 'PENDING_GITHUB_VERIFICATION',
        verification_method: 'github_oauth'
      }, { onConflict: 'user_id,agent_id' });

    claimStatus.textContent = error
      ? error.message
      : 'Claim recorded. Maintainer relationship still requires verification.';
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
