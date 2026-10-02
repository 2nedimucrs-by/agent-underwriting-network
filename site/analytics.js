(() => {
  const config = window.AUN_CONFIG || {};
  const CONSENT_KEY = 'aun_product_analytics_consent';
  const SESSION_KEY = 'aun_session_id';

  function sessionId() {
    let value = sessionStorage.getItem(SESSION_KEY);
    if (!value) {
      value = crypto.randomUUID ? crypto.randomUUID() :
        'sess-' + Date.now() + '-' + Math.random().toString(36).slice(2);
      sessionStorage.setItem(SESSION_KEY, value);
    }
    return value;
  }

  function cloudflare() {
    if (!config.cloudflareWebAnalyticsToken) return;
    const script = document.createElement('script');
    script.defer = true;
    script.src = 'https://static.cloudflareinsights.com/beacon.min.js';
    script.dataset.cfBeacon = JSON.stringify({
      token: config.cloudflareWebAnalyticsToken
    });
    document.head.appendChild(script);
  }

  async function send(eventType, metadata = {}) {
    if (!config.productAnalyticsEnabled) return false;
    if (localStorage.getItem(CONSENT_KEY) !== 'accepted') return false;
    if (!config.supabaseUrl || !config.supabaseAnonKey) return false;

    const payload = {
      session_id: sessionId(),
      user_id: null,
      event_type: eventType,
      agent_id: metadata.agent_id || null,
      page_path: location.pathname,
      referrer: document.referrer || null,
      metadata: Object.fromEntries(
        Object.entries(metadata).filter(([key]) => key !== 'agent_id')
      )
    };

    try {
      const response = await fetch(
        config.supabaseUrl + '/rest/v1/analytics_events',
        {
          method: 'POST',
          headers: {
            apikey: config.supabaseAnonKey,
            Authorization: 'Bearer ' + config.supabaseAnonKey,
            'Content-Type': 'application/json',
            Prefer: 'return=minimal'
          },
          body: JSON.stringify(payload),
          keepalive: true
        }
      );
      return response.ok;
    } catch (_) {
      return false;
    }
  }

  function showConsent() {
    if (!config.productAnalyticsEnabled) return;
    if (localStorage.getItem(CONSENT_KEY)) return;

    const banner = document.createElement('div');
    banner.className = 'consent-banner';
    banner.innerHTML =
      '<div><strong>Optional product analytics</strong>' +
      '<span>Help us understand searches, Trust Card views and comparisons. No raw IP is stored in our product-event table.</span></div>' +
      '<div><button type="button" class="text-button" data-consent="decline">Decline</button>' +
      '<button type="button" class="button" data-consent="accept">Allow</button></div>';

    document.body.appendChild(banner);

    banner.querySelector('[data-consent="accept"]').addEventListener('click', () => {
      localStorage.setItem(CONSENT_KEY, 'accepted');
      banner.remove();
      send('PAGE_VIEW');
    });

    banner.querySelector('[data-consent="decline"]').addEventListener('click', () => {
      localStorage.setItem(CONSENT_KEY, 'declined');
      banner.remove();
    });
  }

  window.AUNAnalytics = Object.freeze({
    track: send,
    consent: () => localStorage.getItem(CONSENT_KEY) || 'unset'
  });

  cloudflare();
  showConsent();

  if (localStorage.getItem(CONSENT_KEY) === 'accepted') {
    send('PAGE_VIEW');
  }
})();
