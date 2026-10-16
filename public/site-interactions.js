(() => {
  const button = document.querySelector('[data-intro-video]');
  if (!button) return;
  button.addEventListener('click', () => {
    const frame = document.createElement('iframe');
    frame.src = 'https://www.youtube-nocookie.com/embed/K9SzW0lHkr4?autoplay=1&rel=0&playsinline=1';
    frame.title = document.documentElement.lang === 'en' ? 'Introduction to Vedansh Vallabh' : 'वेदांश वल्लभ का परिचय';
    frame.allow = 'autoplay; encrypted-media; picture-in-picture';
    frame.allowFullscreen = true;
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    button.replaceWith(frame);
  }, { once: true });
})();
