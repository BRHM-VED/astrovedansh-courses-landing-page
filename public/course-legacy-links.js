// Preserve existing course/enrolment links after the homepage became a hub.
(() => {
  const courseSections = new Set(['enrol', 'courses', 'about', 'curriculum', 'software-bonus', 'faqs', 'scope', 'masterclasses', 'our-promise', 'who-can-learn', 'learning-journey', 'meet-your-teacher', 'why-us']);
  const fragment = location.hash.slice(1);
  if (!courseSections.has(fragment)) return;
  const english = location.pathname.endsWith('/english.html');
  location.replace(new URL(`${english ? 'courses-english.html' : 'courses.html'}${location.search}#${fragment}`, location.href).href);
})();
