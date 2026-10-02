const state = {
  agents: [],
  selected: new Set(),
  query: '',
  category: '',
  sort: 'stars'
};

const list = document.querySelector('#agents');
const search = document.querySelector('#search');
const category = document.querySelector('#category');
const sort = document.querySelector('#sort');
const empty = document.querySelector('#empty');
const count = document.querySelector('#count');
const categoryCount = document.querySelector('#category-count');
const versionPinned = document.querySelector('#version-pinned');
const updated = document.querySelector('#updated');
const failures = document.querySelector('#failures');
const compareBar = document.querySelector('#compare-bar');
const compareCount = document.querySelector('#compare-count');
const compareNow = document.querySelector('#compare-now');
const clearCompare = document.querySelector('#clear-compare');

function esc(value) {
  return String(value ?? '').replace(/[&<>'"]/g, ch => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  })[ch]);
}

function shortNumber(value) {
  const n = Number(value || 0);
  if (n >= 1000000) return (n / 1000000).toFixed(n >= 10000000 ? 0 : 1) + 'm';
  if (n >= 1000) return (n / 1000).toFixed(n >= 10000 ? 0 : 1) + 'k';
  return String(n);
}

function formatDate(value) {
  if (!value) return 'unknown';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'unknown';
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

function getFiltered() {
  const q = state.query.toLowerCase();
  let items = state.agents.filter(agent => {
    const m = agent.metadata || {};
    const matchesQuery = !q || [
      m.repository,
      m.description,
      m.category,
      m.language,
      ...(m.topics || [])
    ].join(' ').toLowerCase().includes(q);
    const matchesCategory = !state.category || m.category === state.category;
    return matchesQuery && matchesCategory;
  });

  items = [...items].sort((a, b) => {
    const am = a.metadata || {};
    const bm = b.metadata || {};
    if (state.sort === 'name') {
      return String(am.repository || '').localeCompare(String(bm.repository || ''));
    }
    if (state.sort === 'fresh') {
      return String(bm.pushed_at || '').localeCompare(String(am.pushed_at || ''));
    }
    return Number(bm.stars || 0) - Number(am.stars || 0);
  });

  return items;
}

function updateCompareBar() {
  compareCount.textContent = state.selected.size;
  compareBar.hidden = state.selected.size === 0;
  compareNow.disabled = state.selected.size < 2;

  document.querySelectorAll('[data-compare-slug]').forEach(input => {
    input.checked = state.selected.has(input.dataset.compareSlug);
  });
}

function render() {
  const items = getFiltered();
  empty.hidden = items.length > 0;

  list.innerHTML = items.map(agent => {
    const m = agent.metadata || {};
    const slug = m.slug || '';
    const commit = agent.version?.commit_sha || 'unresolved';
    const selected = state.selected.has(slug);
    const provenance = commit === 'unresolved' ? 'unknown' : 'partial';

    return '<article class="agent-card">' +
      '<div class="card-top">' +
        '<span class="category-pill">' + esc(m.category || 'Agent / Framework') + '</span>' +
        '<label class="compare-check">' +
          '<input type="checkbox" data-compare-slug="' + esc(slug) + '" ' + (selected ? 'checked' : '') + '>' +
          '<span>Compare</span>' +
        '</label>' +
      '</div>' +
      '<a class="agent-link" href="./agents/' + esc(slug) + '/">' +
        '<h3>' + esc(m.repository || agent.agent_id) + '</h3>' +
        '<p>' + esc(m.description || 'No repository description.') + '</p>' +
      '</a>' +
      '<div class="signal-row">' +
        '<span>★ ' + esc(shortNumber(m.stars)) + '</span>' +
        '<span>forks ' + esc(shortNumber(m.forks)) + '</span>' +
        '<span>' + esc(m.language || 'language unknown') + '</span>' +
      '</div>' +
      '<div class="evidence-strip">' +
        '<span class="evidence-state partial">identity partial</span>' +
        '<span class="evidence-state partial">provenance ' + provenance + '</span>' +
        '<span class="evidence-state neutral">security not evaluated</span>' +
      '</div>' +
      '<div class="card-footer">' +
        '<span>head <code>' + esc(commit.slice(0, 8)) + '</code></span>' +
        '<span>pushed ' + esc(formatDate(m.pushed_at)) + '</span>' +
        '<a href="./agents/' + esc(slug) + '/">Trust Card →</a>' +
      '</div>' +
    '</article>';
  }).join('');

  document.querySelectorAll('[data-compare-slug]').forEach(input => {
    input.addEventListener('change', event => {
      const slug = event.currentTarget.dataset.compareSlug;
      if (event.currentTarget.checked) {
        if (state.selected.size >= 4) {
          event.currentTarget.checked = false;
          return;
        }
        state.selected.add(slug);
        if (window.AUNAnalytics) window.AUNAnalytics.track('COMPARE_ADD', { agent_id: 'github:' + slug.replace('-', '/') });
      } else {
        state.selected.delete(slug);
      }
      updateCompareBar();
    });
  });

  updateCompareBar();
}

function populateCategories(categories) {
  Object.keys(categories || {})
    .sort((a, b) => a.localeCompare(b))
    .forEach(name => {
      const option = document.createElement('option');
      option.value = name;
      option.textContent = name + ' (' + categories[name] + ')';
      category.appendChild(option);
    });
}

fetch('./data/agents.json')
  .then(response => {
    if (!response.ok) throw new Error('index HTTP ' + response.status);
    return response.json();
  })
  .then(data => {
    state.agents = data.agents || [];
    count.textContent = data.profile_count ?? state.agents.length;
    categoryCount.textContent = Object.keys(data.categories || {}).length;
    versionPinned.textContent = state.agents.filter(agent => Boolean(agent.version?.commit_sha)).length;
    updated.textContent = data.generated_at
      ? 'Generated ' + new Date(data.generated_at).toLocaleString()
      : 'Bootstrap index';

    populateCategories(data.categories || {});

    if ((data.failures || []).length) {
      failures.hidden = false;
      failures.textContent = data.failures.length + ' seed projects could not be refreshed in this build. They are not shown as verified.';
    }

    render();
  })
  .catch(error => {
    updated.textContent = 'Index unavailable';
    failures.hidden = false;
    failures.textContent = 'Could not load the public index: ' + error.message;
    render();
  });

let searchTimer;
search.addEventListener('input', () => {
  state.query = search.value.trim();
  render();
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    if (state.query.length >= 2 && window.AUNAnalytics) {
      window.AUNAnalytics.track('SEARCH', { query_length: state.query.length });
    }
  }, 700);
});

category.addEventListener('change', () => {
  state.category = category.value;
  render();
});

sort.addEventListener('change', () => {
  state.sort = sort.value;
  render();
});

clearCompare.addEventListener('click', () => {
  state.selected.clear();
  updateCompareBar();
});

compareNow.addEventListener('click', () => {
  if (state.selected.size < 2) return;
  const params = new URLSearchParams();
  params.set('agents', [...state.selected].join(','));
  if (window.AUNAnalytics) window.AUNAnalytics.track('COMPARE_RUN', { count: state.selected.size });
  window.location.href = './compare.html?' + params.toString();
});
