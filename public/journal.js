(() => {
  const cards = [...document.querySelectorAll('.j-card')];
  const search = document.querySelector('#journal-search');
  const category = document.querySelector('#journal-category');
  const pagination = document.querySelector('.j-pagination');
  const previous = document.querySelector('#journal-prev');
  const next = document.querySelector('#journal-next');
  let page = 1;
  const size = 12;
  const normalize = text => text.normalize('NFC').toLocaleLowerCase('hi').trim();
  const requested = new URLSearchParams(location.search).get('category');
  if ([...category.options].some(option => option.value === requested)) category.value = requested;
  function render() {
    const terms = normalize(search.value).split(/\s+/).filter(Boolean);
    const results = cards.filter(card => (!category.value || card.dataset.category === category.value) && terms.every(term => normalize(card.dataset.search).includes(term)));
    const pages = Math.max(1, Math.ceil(results.length / size));
    page = Math.min(page, pages);
    const visible = new Set(results.slice((page - 1) * size, page * size));
    cards.forEach(card => { card.hidden = !visible.has(card); });
    document.querySelector('#journal-empty').hidden = results.length > 0;
    document.querySelector('#journal-status').textContent = results.length ? `${results.length} लेख · ${(page-1)*size+1}–${Math.min(page*size, results.length)} दिखाए गए` : '0 लेख';
    pagination.hidden = pages <= 1;
    document.querySelector('#journal-page').textContent = `पृष्ठ ${page} / ${pages}`;
    previous.disabled = page === 1;
    next.disabled = page === pages;
  }
  search.addEventListener('input', () => { page = 1; render(); });
  category.addEventListener('change', () => { page = 1; render(); });
  document.querySelector('.j-controls').addEventListener('submit', event => event.preventDefault());
  document.querySelector('.j-controls').addEventListener('reset', event => {
    event.preventDefault(); search.value = ''; category.value = ''; page = 1; render(); search.focus();
  });
  function turn(delta) {
    page += delta; render();
    document.querySelector('.j-results-heading').scrollIntoView({ block: 'start', behavior: 'auto' });
  }
  previous.addEventListener('click', () => turn(-1));
  next.addEventListener('click', () => turn(1));
  render();
})();
