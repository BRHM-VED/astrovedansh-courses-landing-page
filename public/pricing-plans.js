(() => {
  'use strict';
  const buttons = [...document.querySelectorAll('[data-guidance]')];
  const cards = [...document.querySelectorAll('[data-plan-group]')];
  const valid = new Set(buttons.map(button => button.dataset.guidance));
  function filter(group, updateUrl = false) {
    if (!valid.has(group)) group = 'all';
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.guidance === group)));
    cards.forEach(card => card.hidden = group !== 'all' && card.dataset.planGroup !== group);
    document.querySelector('.combo-grid').hidden = !cards.some(card => card.classList.contains('combo-card') && !card.hidden);
    if (updateUrl) {
      const url = new URL(location.href);
      if (group === 'all') url.searchParams.delete('guidance'); else url.searchParams.set('guidance', group);
      history.replaceState(null, '', url.pathname + url.search + url.hash);
      document.dispatchEvent(new CustomEvent('astrovedansh:plan-filter', {detail:{group}}));
    }
  }
  buttons.forEach(button => button.addEventListener('click', () => filter(button.dataset.guidance, true)));
  filter(new URLSearchParams(location.search).get('guidance') || 'all');
})();
