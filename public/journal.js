(() => {
  const en = document.documentElement.lang === 'en';
  const cards = [...document.querySelectorAll('.j-card')];
  const search = document.querySelector('#journal-search');
  const category = document.querySelector('#journal-category');
  const pagination = document.querySelector('.j-pagination');
  const previous = document.querySelector('#journal-prev');
  const next = document.querySelector('#journal-next');
  const savedOnly = document.querySelector('#journal-saved-only');
  let showSaved = false;
  function savedLinks() {
    try {
      const value = JSON.parse(localStorage.getItem('astrovedansh-saved-articles-v1') || '{}');
      return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
    } catch { return {}; }
  }
  let page = 1;
  const size = 12;
  const normalize = text => text.normalize('NFC').toLocaleLowerCase('hi').trim();
  const requested = new URLSearchParams(location.search).get('category');
  if ([...category.options].some(option => option.value === requested)) category.value = requested;
  function render() {
    const terms = normalize(search.value).split(/\s+/).filter(Boolean);
    const saved = savedLinks();
    const results = cards.filter(card => {
      const href = card.querySelector('h2 a')?.getAttribute('href');
      return (!showSaved || Boolean(saved[href])) && (!category.value || card.dataset.category === category.value) && terms.every(term => normalize(card.dataset.search).includes(term));
    });
    const pages = Math.max(1, Math.ceil(results.length / size));
    page = Math.min(page, pages);
    const visible = new Set(results.slice((page - 1) * size, page * size));
    cards.forEach(card => { card.hidden = !visible.has(card); });
    document.querySelector('#journal-empty').hidden = results.length > 0;
    document.querySelector('#journal-status').textContent = results.length ? `${results.length} ${en ? 'articles' : 'लेख'} · ${(page-1)*size+1}–${Math.min(page*size, results.length)} ${en ? 'shown' : 'दिखाए गए'}` : (en ? '0 articles' : '0 लेख');
    pagination.hidden = pages <= 1;
    document.querySelector('#journal-page').textContent = `${en ? 'Page' : 'पृष्ठ'} ${page} / ${pages}`;
    previous.disabled = page === 1;
    next.disabled = page === pages;
  }
  search.addEventListener('input', () => { page = 1; render(); });
  category.addEventListener('change', () => { page = 1; render(); });
  document.querySelector('.j-controls').addEventListener('submit', event => event.preventDefault());
  document.querySelector('.j-controls').addEventListener('reset', event => {
    event.preventDefault(); search.value = ''; category.value = ''; showSaved = false;
    if (savedOnly) savedOnly.setAttribute('aria-pressed', 'false');
    page = 1; render(); search.focus();
  });
  function turn(delta) {
    page += delta; render();
    document.querySelector('.j-results-heading').scrollIntoView({ block: 'start', behavior: 'auto' });
  }
  previous.addEventListener('click', () => turn(-1));
  next.addEventListener('click', () => turn(1));
  if (savedOnly) savedOnly.addEventListener('click', () => {
    showSaved = !showSaved; page = 1;
    savedOnly.setAttribute('aria-pressed', String(showSaved)); render();
  });
  addEventListener('storage', render);
  addEventListener('pageshow', render);
  render();
})();
