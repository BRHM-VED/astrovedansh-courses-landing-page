(() => {
  'use strict';
  const viewer = document.getElementById('review-viewer');
  if (!viewer || typeof viewer.showModal !== 'function') return;
  const full = viewer.querySelector('.review-full');
  const title = document.getElementById('review-viewer-title');
  const viewport = viewer.querySelector('.review-image-scroll');
  const zoom = viewer.querySelector('.review-zoom');
  let opener;
  function setZoom(enlarged) {
    viewport.classList.toggle('is-zoomed', enlarged);
    zoom.setAttribute('aria-pressed', String(enlarged));
    const hi = document.documentElement.lang === 'hi';
    zoom.textContent = enlarged ? (hi ? 'छोटा करें' : 'Zoom out') : (hi ? 'बड़ा करें' : 'Zoom in');
    if (!enlarged) { viewport.scrollLeft = 0; viewport.scrollTop = 0; }
  }
  document.querySelectorAll('.review-open').forEach(link => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener = link;
    full.src = link.href;
    full.alt = link.querySelector('img').alt;
    title.textContent = link.dataset.reviewName;
    setZoom(false);
    viewer.showModal();
    viewer.scrollTop = 0;
  }));
  zoom.addEventListener('click', () => setZoom(!viewport.classList.contains('is-zoomed')));
  full.addEventListener('click', () => setZoom(!viewport.classList.contains('is-zoomed')));
  viewer.querySelector('.review-close').addEventListener('click', () => viewer.close());
  viewer.addEventListener('close', () => { setZoom(false); opener?.focus(); });
  viewer.addEventListener('click', event => {
    const r = viewer.getBoundingClientRect();
    if (event.target === viewer && (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)) viewer.close();
  });
})();
