/* Local event queue only. No third-party collector, cookies, birth data or form values. */
(() => {
  'use strict';
  const emit = (event, params = {}) => {
    const detail = {event, page: location.pathname, language: document.documentElement.lang === 'hi' ? 'hi' : 'en', ...params};
    window.astrovedanshEvents = window.astrovedanshEvents || [];
    window.astrovedanshEvents.push(detail);
    document.dispatchEvent(new CustomEvent('astrovedansh:analytics', {detail}));
  };
  emit('page_view');
  document.addEventListener('av-language-change', () => emit('language_selection'));
  document.addEventListener('click', event => {
    const a = event.target.closest('a[href]');
    if (!a) return;
    const url = new URL(a.href, location.href);
    const route = url.pathname;
    if (a.dataset.timingPackage) emit('timing_package_selection', {package_id: a.dataset.timingPackage});
    const option = /^\/consultation-(audio|expert|personal|detailed)\.html$/.exec(route);
    if (option) emit('consultation_option_selection', {option_id: option[1]});
    const category = {'/reports.html':'reports','/consultation.html':'consultation','/courses.html':'courses','/courses-english.html':'courses'}[route];
    if (category) emit('service_category_click', {category});
    if (url.hostname === 'gemostone.com') emit('service_category_click', {category:'gemostone'});
    if (['perfect-timing.astrovedansh.com','perfect-career.astrovedansh.com'].includes(url.hostname) && !route.endsWith('.pdf')) emit('outbound_product_click', {product_id:url.hostname.startsWith('perfect-timing')?'timing':'career'});
  });
  // begin_checkout, purchase, booking and revenue need verified backend/provider events.
  // A link click or WhatsApp redirect is never emitted as a purchase or confirmed booking.
})();
