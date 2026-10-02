const state = { agents: [] };

const list = document.querySelector('#agents');
const search = document.querySelector('#search');
const empty = document.querySelector('#empty');
const count = document.querySelector('#count');
const updated = document.querySelector('#updated');

function esc(value) {
  return String(value ?? '').replace(/[&<>'"]/g, ch => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  })[ch]);
}

function render(items) {
  count.textContent = state.agents.length;
  empty.hidden = items.length > 0;
  list.innerHTML = items.map(agent => {
    const m = agent.metadata || {};
    const commit = agent.version?.commit_sha || 'unresolved';
    return `<a class="card" href="${esc(agent.source?.url)}" target="_blank" rel="noreferrer">
      <div class="card-top">
        <span class="repo">${esc(m.repository || agent.agent_id)}</span>
        <span class="status">${esc(agent.status)}</span>
      </div>
      <p class="desc">${esc(m.description || 'No repository description.')}</p>
      <div class="meta">
        <span>★ ${esc(m.stars || 0)}</span>
        <span>forks ${esc(m.forks || 0)}</span>
        <span>license ${esc(m.license || 'unknown')}</span>
        <span>head ${esc(commit.slice(0, 8))}</span>
      </div>
    </a>`;
  }).join('');
}

fetch('./data/agents.json')
  .then(response => response.json())
  .then(data => {
    state.agents = data.agents || [];
    updated.textContent = data.generated_at
      ? `Generated ${new Date(data.generated_at).toLocaleString()}`
      : 'Bootstrap index';
    render(state.agents);
  })
  .catch(() => {
    updated.textContent = 'Index unavailable';
    render([]);
  });

search.addEventListener('input', () => {
  const q = search.value.trim().toLowerCase();
  const items = !q
    ? state.agents
    : state.agents.filter(agent => JSON.stringify(agent).toLowerCase().includes(q));
  render(items);
});
