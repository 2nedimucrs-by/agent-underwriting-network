const picker = document.querySelector('#agent-picker');
const addAgent = document.querySelector('#add-agent');
const empty = document.querySelector('#compare-empty');
const wrap = document.querySelector('#compare-wrap');
const table = document.querySelector('#compare-table');

const state = {
  agents: [],
  selected: []
};

function esc(value) {
  return String(value ?? '').replace(/[&<>'"]/g, ch => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  })[ch]);
}

function bySlug(slug) {
  return state.agents.find(agent => agent.metadata?.slug === slug);
}

function readQuery() {
  const params = new URLSearchParams(window.location.search);
  return (params.get('agents') || '')
    .split(',')
    .map(value => value.trim())
    .filter(Boolean)
    .slice(0, 4);
}

function writeQuery() {
  const params = new URLSearchParams();
  if (state.selected.length) params.set('agents', state.selected.join(','));
  const next = params.toString() ? './compare.html?' + params.toString() : './compare.html';
  window.history.replaceState({}, '', next);
}

function cell(value, fallback = '—') {
  if (value === null || value === undefined || value === '') return fallback;
  return esc(value);
}

function stateClass(value) {
  if (value === 'VERIFIED') return 'partial';
  if (value === 'EVIDENCE_PARTIAL') return 'partial';
  return 'neutral';
}

function render() {
  state.selected = state.selected
    .filter(slug => Boolean(bySlug(slug)))
    .slice(0, 4);

  writeQuery();

  const selectedAgents = state.selected.map(bySlug).filter(Boolean);
  empty.hidden = selectedAgents.length > 0;
  wrap.hidden = selectedAgents.length === 0;

  if (!selectedAgents.length) {
    table.innerHTML = '';
    return;
  }

  const dimensions = [
    'identity',
    'provenance',
    'security',
    'permissions',
    'capability',
    'reliability',
    'economics',
    'freshness'
  ];

  const header = '<tr><th>Evidence</th>' + selectedAgents.map(agent => {
    const m = agent.metadata || {};
    return '<th>' +
      '<a href="./agents/' + esc(m.slug) + '/">' + esc(m.repository) + '</a>' +
      '<div class="signal-row"><span>★ ' + cell(m.stars, '0') + '</span><span>' + cell(m.category) + '</span></div>' +
      '<button class="text-button remove-agent" type="button" data-remove="' + esc(m.slug) + '">Remove</button>' +
    '</th>';
  }).join('') + '</tr>';

  const rows = [];

  rows.push('<tr><td>Version head</td>' + selectedAgents.map(agent => {
    const commit = agent.version?.commit_sha || 'unresolved';
    return '<td><code>' + esc(commit) + '</code></td>';
  }).join('') + '</tr>');

  rows.push('<tr><td>License</td>' + selectedAgents.map(agent =>
    '<td>' + cell(agent.metadata?.license, 'unknown') + '</td>'
  ).join('') + '</tr>');

  rows.push('<tr><td>Primary language</td>' + selectedAgents.map(agent =>
    '<td>' + cell(agent.metadata?.language, 'unknown') + '</td>'
  ).join('') + '</tr>');

  dimensions.forEach(dimension => {
    rows.push('<tr><td>' + esc(dimension[0].toUpperCase() + dimension.slice(1)) + '</td>' +
      selectedAgents.map(agent => {
        const value = agent.evidence_dimensions?.[dimension] || 'NOT_EVALUATED';
        return '<td><span class="evidence-state ' + stateClass(value) + '">' + esc(value) + '</span></td>';
      }).join('') +
    '</tr>');
  });

  rows.push('<tr><td>Current status</td>' + selectedAgents.map(agent =>
    '<td>' + esc(agent.status || 'UNKNOWN') + '</td>'
  ).join('') + '</tr>');

  table.innerHTML = header + rows.join('');

  document.querySelectorAll('[data-remove]').forEach(button => {
    button.addEventListener('click', () => {
      state.selected = state.selected.filter(slug => slug !== button.dataset.remove);
      render();
    });
  });
}

function populatePicker() {
  picker.innerHTML = '<option value="">Add another project…</option>' +
    state.agents
      .filter(agent => !state.selected.includes(agent.metadata?.slug))
      .sort((a, b) => String(a.metadata?.repository || '').localeCompare(String(b.metadata?.repository || '')))
      .map(agent => '<option value="' + esc(agent.metadata?.slug) + '">' + esc(agent.metadata?.repository) + '</option>')
      .join('');
}

fetch('./data/agents.json')
  .then(response => response.json())
  .then(data => {
    state.agents = data.agents || [];
    state.selected = readQuery();
    populatePicker();
    render();
  })
  .catch(error => {
    empty.textContent = 'Comparison data could not be loaded: ' + error.message;
  });

addAgent.addEventListener('click', () => {
  const slug = picker.value;
  if (!slug || state.selected.includes(slug) || state.selected.length >= 4) return;
  state.selected.push(slug);
  populatePicker();
  render();
});

window.addEventListener('load', () => {
  if (window.AUNAnalytics && new URLSearchParams(location.search).get('agents')) {
    window.AUNAnalytics.track('COMPARE_RUN', { count: state.selected.length });
  }
});
