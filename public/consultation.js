(() => {
  'use strict';
  const plans = {
    audio: { name: 'Personal Audio Analysis (10–15 minute voice note)', fee: 999, route: '/consultation-audio.html' },
    expert: { name: 'Expert Consultation (20–25 minutes)', fee: 1100, route: '/consultation-expert.html' },
    '30': { name: 'Personal Consultation (30 minutes)', fee: 2100, route: '/consultation-personal.html' },
    '60': { name: 'Detailed Consultation (60 minutes)', fee: 4200, route: '/consultation-detailed.html' }
  };
  const form = document.querySelector('#consult-form');
  if (!form) {
    const legacyPlan = new URLSearchParams(location.search).get('plan');
    if (Object.hasOwn(plans, legacyPlan)) location.replace(plans[legacyPlan].route);
    return;
  }
  const plan = document.body.dataset.bookingPlan;
  if (!Object.hasOwn(plans, plan)) return;
  form.elements.plan.value = plan;
  const hi = () => document.documentElement.lang === 'hi';
  function dates(now = new Date()) {
    const parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(now);
    const v = Object.fromEntries(parts.map(x => [x.type, x.value]));
    const today = `${v.year}-${v.month}-${v.day}`;
    const d = new Date(today + 'T00:00:00Z');
    d.setUTCDate(d.getUTCDate() + 2);
    return { today, min: d.toISOString().slice(0, 10) };
  }
  function refresh() {
    const d = dates();
    form.elements.birthDate.max = d.today;
    form.elements.sessionDate.min = d.min;
    const formatted = new Intl.DateTimeFormat(hi() ? 'hi-IN' : 'en-IN', { dateStyle: 'long', timeZone: 'UTC' }).format(new Date(d.min + 'T00:00:00Z'));
    document.querySelector('#date-note').textContent = hi()
      ? `सबसे पहले ${formatted} की तारीख चुन सकते हैं। ${plan === 'audio' ? 'ऑडियो डिलीवरी की पुष्टि टीम करेगी।' : 'लाइव सेशन के समय की पुष्टि टीम करेगी।'}`
      : `Earliest request date: ${formatted}. ${plan === 'audio' ? 'Our team will confirm audio delivery.' : 'Our team will confirm the live session time.'}`;
    return d;
  }
  document.addEventListener('av-language-change', refresh);
  refresh();
  form.addEventListener('submit', e => {
    e.preventDefault();
    const d = refresh();
    if (!form.reportValidity()) return;
    if (form.elements.sessionDate.value < d.min) { form.elements.sessionDate.focus(); return; }
    const f = Object.fromEntries(new FormData(form));
    const chosen = plans[plan];
    const text = [
      'Radhe Radhe AstroVedansh, I would like to request a booking.', '',
      `Option: ${chosen.name}`, `Displayed fee: ₹${chosen.fee}`,
      `Name: ${f.name.trim()}`, `Gender: ${f.gender}`, `Date of birth: ${f.birthDate}`,
      `Time of birth: ${f.birthTime}`, `Place of birth: ${f.birthPlace.trim()}`,
      `WhatsApp: ${f.phone}`, `Email: ${f.email}`, `Main question: ${f.question.trim()}`,
      `${plan === 'audio' ? 'Preferred audio delivery date' : 'Preferred session date'} (India): ${f.sessionDate}`, '',
      plan === 'audio' ? 'I understand this is a recorded voice note on WhatsApp, not a live call.' : 'Please confirm the session time on WhatsApp.',
      'Please confirm availability and share payment instructions.'
    ].join('\n');
    document.querySelector('#status').textContent = hi()
      ? 'WhatsApp में जानकारी जाँचकर Send दबाएँ। टीम की पुष्टि के बाद बुकिंग होगी।'
      : 'Review your details in WhatsApp and press Send. Your booking is confirmed by our team.';
    // Same-tab handoff also works in Instagram's in-app browser without a popup.
    window.location.assign('https://wa.me/919045432034?text=' + encodeURIComponent(text));
  });
})();
