/* Load the supplied YouTube embed only after an explicit Play action. */
(() => {
  'use strict';
  const shell = document.querySelector('[data-about-video]');
  const play = shell?.querySelector('button');
  if (!play) return;
  play.addEventListener('click', () => {
    const frame = document.createElement('iframe');
    frame.title = 'About AstroVedansh — video';
    frame.src = 'https://www.youtube-nocookie.com/embed/K9SzW0lHkr4?autoplay=1&playsinline=1&rel=0&hl=' + (document.documentElement.lang === 'hi' ? 'hi' : 'en');
    frame.allow = "autoplay; encrypted-media; fullscreen; clipboard-write 'none'; web-share 'none'";
    frame.allowFullscreen = true;
    // Keep playback in this frame. Do not grant popup, top-navigation or download permissions.
    // This is a navigation restriction, not copy protection or DRM.
    frame.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-presentation');
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    shell.replaceChildren(frame);
    frame.focus({preventScroll:true});
  }, {once:true});
})();
