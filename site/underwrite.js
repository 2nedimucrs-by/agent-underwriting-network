const policies = {
  browser_read: {
    required: ['identity', 'provenance', 'security', 'permissions', 'capability', 'reliability', 'freshness'],
    allowsWrite: false,
    maxSpendUsd: 0
  },
  repository_read: {
    required: ['identity', 'provenance', 'security', 'permissions', 'capability', 'reliability', 'freshness'],
    allowsWrite: false,
    maxSpendUsd: 0
  },
  structured_extraction: {
    required: ['identity', 'provenance', 'capability', 'reliability', 'freshness'],
    allowsWrite: false,
    maxSpendUsd: 0
  },
  mcp_tool_invocation: {
    required: ['identity', 'provenance', 'security', 'permissions', 'capability', 'reliability', 'freshness'],
    allowsWrite: false,
    maxSpendUsd: 0
  },
  code_change: {
    required: ['identity', 'provenance', 'security', 'permissions', 'capability', 'reliability', 'freshness'],
    allowsWrite: true,
    maxSpendUsd: 5
  },
  crm_write: {
    required: ['identity', 'provenance', 'security', 'permissions', 'capability', 'reliability', 'economics', 'freshness'],
    allowsWrite: true,
    maxSpendUsd: 2
  }
};

const agentSelect = document.querySelector('#uw-agent');
const taskSelect = document.querySelector('#uw-task');
const writeInput = document.querySelector('#uw-write');
const spendInput = document.querySelector('#uw-spend');
const runButton = document.querySelector('#uw-run');
const result = document.querySelector('#uw-result');
const decisionValue = document.querySelector('#uw-decision');
const versionValue = document.querySelector('#uw-version');
const reasons = document.querySelector('#uw-reasons');
const limits = document.querySelector('#uw-limits');
const dimensions = document.querySelector('#uw-dimensions');
const cardLink = document.querySelector('#uw-card-link');
const modeStatus = document.querySelector('#uw-mode');

let agents = [];
let apiClient = null;
let apiSession = null;

const runtimeConfig = window.AUN_CONFIG || {};
if (
  runtimeConfig.authEnabled &&
  runtimeConfig.supabaseUrl &&
  runtimeConfig.supabasePublishableKey &&
  window.supabase
) {
  apiClient = window.supabase.createClient(
    runtimeConfig.supabaseUrl,
    runtimeConfig.supabasePublishableKey
  );
  apiClient.auth.getSession().then(({ data }) => {
    apiSession = data.session || null;
    modeStatus.textContent = apiSession
      ? 'Authenticated API mode: server-side policy enforcement is active.'
      : 'Public preview mode: sign in to run the deployed can-hire API.';
  });
} else {
  modeStatus.textContent =
    'Public preview mode: backend auth is not configured.';
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

function evaluate(card, taskType, requested) {
  const policy = policies[taskType];
  const evidence = card.evidence_dimensions || {};
  const evidenceIds = card.evidence_ids || [];

  if (card.status === 'BLOCKED') {
    return {
      decision: 'DENY',
      reasons: ['Agent status is BLOCKED.'],
      limits: {},
      missing: [],
      evidenceIds
    };
  }

  if (requested.write_access && !policy.allowsWrite) {
    return {
      decision: 'DENY',
      reasons: ['Task policy forbids write access.'],
      limits: { write_access: false, max_spend_usd: policy.maxSpendUsd },
      missing: [],
      evidenceIds
    };
  }

  const missing = policy.required.filter(name => evidence[name] !== 'VERIFIED');
  const enforced = {
    write_access: requested.write_access && policy.allowsWrite,
    max_spend_usd: Math.min(requested.max_spend_usd, policy.maxSpendUsd)
  };

  if (missing.length) {
    return {
      decision: 'INSUFFICIENT_EVIDENCE',
      reasons: ['Required VERIFIED evidence is missing for: ' + missing.join(', ')],
      limits: enforced,
      missing,
      evidenceIds
    };
  }

  if (card.status !== 'VERIFIED_FOR_TASK') {
    return {
      decision: 'REVIEW_REQUIRED',
      reasons: ['Evidence dimensions are VERIFIED, but this Trust Card is not VERIFIED_FOR_TASK.'],
      limits: enforced,
      missing: [],
      evidenceIds
    };
  }

  if (requested.max_spend_usd > policy.maxSpendUsd) {
    return {
      decision: 'ALLOW_WITH_LIMITS',
      reasons: ['Requested spend exceeds policy maximum.'],
      limits: enforced,
      missing: [],
      evidenceIds
    };
  }

  return {
    decision: 'ALLOW',
    reasons: ['Task-specific evidence and requested limits satisfy policy.'],
    limits: enforced,
    missing: [],
    evidenceIds
  };
}

function renderDecision(card, taskType, output) {
  result.hidden = false;
  decisionValue.textContent = output.decision;
  decisionValue.dataset.decision = output.decision;
  versionValue.textContent = card.version?.commit_sha || card.version?.identifier || 'unresolved';

  reasons.innerHTML = output.reasons
    .map(reason => '<li>' + esc(reason) + '</li>')
    .join('');

  limits.innerHTML =
    '<div class="workspace-row"><span>Write access</span><strong>' +
      esc(String(Boolean(output.limits.write_access))) + '</strong></div>' +
    '<div class="workspace-row"><span>Max spend</span><strong>$' +
      esc(Number(output.limits.max_spend_usd || 0).toFixed(2)) + '</strong></div>';

  const policy = policies[taskType];
  dimensions.innerHTML = policy.required.map(name => {
    const state = card.evidence_dimensions?.[name] || 'NOT_EVALUATED';
    const requiredClass = state === 'VERIFIED' ? 'partial' : 'neutral';

    return '<article class="dimension">' +
      '<span>' + esc(name) + '</span>' +
      '<strong class="evidence-state ' + requiredClass + '">' + esc(state) + '</strong>' +
    '</article>';
  }).join('');

  const slug = card.metadata?.slug;
  cardLink.href = slug ? './agents/' + encodeURIComponent(slug) + '/' : '#';

  if (window.AUNAnalytics) {
    window.AUNAnalytics.track('COMPARE_RUN', {
      agent_id: card.agent_id,
      underwriting_task: taskType,
      decision: output.decision
    });
  }
}

fetch('./data/agents.json')
  .then(response => response.json())
  .then(data => {
    agents = data.agents || [];
    agentSelect.innerHTML = agents
      .slice()
      .sort((a, b) =>
        String(a.metadata?.repository || '').localeCompare(
          String(b.metadata?.repository || '')
        )
      )
      .map(agent =>
        '<option value="' + esc(agent.metadata?.slug) + '">' +
          esc(agent.metadata?.repository || agent.agent_id) +
        '</option>'
      )
      .join('');
  });

runButton.addEventListener('click', async () => {
  const slug = agentSelect.value;
  const agent = agents.find(item => item.metadata?.slug === slug);
  if (!agent) return;

  runButton.disabled = true;
  runButton.textContent = 'Evaluating…';

  try {
    const response = await fetch('./trust-cards/' + encodeURIComponent(slug) + '.json', {
      cache: 'no-store'
    });
    if (!response.ok) throw new Error('Trust Card unavailable');
    const card = await response.json();

    const requested = {
      write_access: writeInput.checked,
      max_spend_usd: Math.max(0, Number(spendInput.value || 0))
    };

    let output;
    if (apiClient && apiSession) {
      const invocation = await apiClient.functions.invoke('can-hire', {
        body: {
          agent_id: card.agent_id,
          task_type: taskSelect.value,
          limits: requested
        }
      });

      if (invocation.error) {
        throw new Error('Underwriting API error: ' + invocation.error.message);
      }

      output = {
        decision: invocation.data.decision,
        reasons: invocation.data.reasons || [],
        limits: invocation.data.limits || {},
        missing: invocation.data.missing_dimensions || [],
        evidenceIds: invocation.data.evidence_ids || []
      };
      modeStatus.textContent =
        'Authenticated API mode: decision returned by deployed can-hire.';
    } else {
      output = evaluate(card, taskSelect.value, requested);
      modeStatus.textContent =
        'Public preview mode: local fail-closed policy simulation.';
    }

    renderDecision(card, taskSelect.value, output);
  } catch (error) {
    result.hidden = false;
    decisionValue.textContent = 'ERROR';
    reasons.innerHTML = '<li>' + esc(error.message) + '</li>';
  } finally {
    runButton.disabled = false;
    runButton.textContent = 'Evaluate task fitness';
  }
});
