// Preserve existing course/enrolment links after the homepage became a hub.
(() => {
  const courseSections = new Set(['enrol', 'courses', 'about', 'curriculum', 'software-bonus', 'faqs']);
  const fragment = location.hash.slice(1);
  if (!courseSections.has(fragment)) return;
  const english = location.pathname.endsWith('/english.html');
  location.replace(new URL(`${english ? 'courses-english.html' : 'courses.html'}#${fragment}`, location.href).href);
})();
