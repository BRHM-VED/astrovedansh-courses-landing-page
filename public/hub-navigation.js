/* Native details works without JS; add keyboard/outside-click dismissal. */
(() => {
  const menus = [...document.querySelectorAll('.hub-menu')];
  for (const menu of menus) {
    menu.addEventListener('click', event => {
      if (event.target.closest('a')) menu.open = false;
    });
    menu.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.open) {
        menu.open = false;
        menu.querySelector('summary').focus();
      }
    });
  }
  document.addEventListener('click', event => {
    for (const menu of menus) if (!menu.contains(event.target)) menu.open = false;
  });
  function updateLinks() {
    const hi = document.documentElement.lang === 'hi';
    document.querySelectorAll('a[href="/courses.html#about"],a[href="/courses-english.html#about"]').forEach(a => {
      a.href = hi ? '/courses.html#about' : '/courses-english.html#about';
    });
  }
  document.addEventListener('av-language-change', updateLinks);
  updateLinks();
})();
