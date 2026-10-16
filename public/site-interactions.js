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
  const motion = new IntersectionObserver(entries => {
    entries.forEach(entry => entry.target.classList.toggle('motion-active', entry.isIntersecting));
  }, { threshold: 0.08 });
  document.querySelectorAll('.intro-play, .numerology-art, .masterclass-card, .software-bonus-art').forEach(el => motion.observe(el));
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

// Scroll-linked depth without taking over scrolling or running a perpetual frame loop.
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)');
  const hero = document.querySelector('.heritage-art');
  const portraits = [...document.querySelectorAll('.about-portrait')];
  const cards = [...document.querySelectorAll('.masterclass-card')];
  const tilts = [...document.querySelectorAll('.heritage-art, .numerology-art')];
  const tracked = [hero, ...portraits, ...cards].filter(Boolean);
  if (!tracked.length || !('IntersectionObserver' in window)) return;
  const visible = new Set();
  let frame = 0;
  const clamp = (v, min, max) => Math.min(max, Math.max(min, v));
  function render() {
    frame = 0;
    if (reduced.matches || document.hidden) return;
    const height = window.innerHeight;
    const desktop = window.innerWidth > 680;
    // Read all positions before writing styles, avoiding repeated layouts.
    const positions = [...visible].map(el => [el, el.getBoundingClientRect()]);
    for (const [el, rect] of positions) {
      const progress = clamp((height - rect.top) / (height + rect.height), 0, 1);
      if (el === hero) {
        el.style.setProperty('--scroll-depth', `${clamp(-rect.top * .07, -18, 28)}px`);
      } else if (portraits.includes(el)) {
        el.style.setProperty('--scroll-depth', `${(progress - .5) * (desktop ? -38 : -14)}px`);
      } else {
        const entrance = clamp((rect.top - height * .68) / (height * .32), 0, 1);
        el.style.setProperty('--card-rise', `${entrance * (desktop ? 34 : 16)}px`);
        el.style.setProperty('--card-angle', `${entrance * (desktop ? 6 : 0)}deg`);
      }
    }
    const travel = document.documentElement.scrollHeight - height;
    document.documentElement.style.setProperty('--reading-progress', String(travel > 0 ? clamp(window.scrollY / travel, 0, 1) : 0));
  }
  function schedule() {
    if (!frame && !reduced.matches && !document.hidden) frame = requestAnimationFrame(render);
  }
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => entry.isIntersecting ? visible.add(entry.target) : visible.delete(entry.target));
    schedule();
  }, { rootMargin: '80px 0px' });
  tracked.forEach(el => observer.observe(el));
  tilts.forEach(el => {
    el.classList.add('depth-surface');
    el.addEventListener('pointermove', event => {
      if (reduced.matches || !finePointer.matches || event.pointerType === 'touch') return;
      const rect = el.getBoundingClientRect();
      const x = clamp((event.clientX - rect.left) / rect.width, 0, 1);
      const y = clamp((event.clientY - rect.top) / rect.height, 0, 1);
      el.style.setProperty('--tilt-x', `${(0.5 - y) * 7}deg`);
      el.style.setProperty('--tilt-y', `${(x - 0.5) * 9}deg`);
    }, { passive: true });
    el.addEventListener('pointerleave', () => {
      el.style.setProperty('--tilt-x', '0deg');
      el.style.setProperty('--tilt-y', '0deg');
    });
  });
  portraits.forEach(el => el.classList.add('scroll-portrait'));
  cards.forEach(el => el.classList.add('scroll-depth-card'));
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  document.addEventListener('visibilitychange', schedule);
  reduced.addEventListener('change', schedule);
  schedule();
})();
