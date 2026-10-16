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

// Animate only while visible; content remains readable without JavaScript.
(() => {
  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const dial = document.querySelector('.celestial-engraving');
  if (dial) new IntersectionObserver(entries => {
    entries.forEach(entry => { dial.style.animationPlayState = entry.isIntersecting ? 'running' : 'paused'; });
  }).observe(dial);
  const reveals = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('heritage-arrive');
        reveals.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.learning-hook, .section>.container>h2, .about-portrait, .masterclass-card').forEach(el => reveals.observe(el));
})();
