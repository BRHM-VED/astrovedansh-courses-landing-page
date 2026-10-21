/* Static bilingual pages must update the same preference used by the hub. */
(() => {
  const lang = document.documentElement.lang;
  if (lang === 'hi' || lang === 'en') {
    try { localStorage.setItem('av-language', lang); } catch {}
  }
})();
