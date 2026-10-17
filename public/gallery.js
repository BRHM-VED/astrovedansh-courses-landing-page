(() => {
  const dialog = document.querySelector('.photo-dialog');
  if (!dialog || !dialog.showModal) return;
  const image = dialog.querySelector('img');
  const caption = dialog.querySelector('.photo-dialog-caption');
  let trigger;
  document.querySelectorAll('.gallery-open').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault(); trigger = link;
      image.src = link.getAttribute('href');
      image.alt = link.querySelector('img').alt;
      caption.textContent = image.alt;
      dialog.classList.toggle('certificate-view', link.dataset.certificate === 'true');
      dialog.showModal();
    });
  });
  dialog.querySelector('.photo-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => { image.removeAttribute('src'); trigger?.focus(); });
})();
