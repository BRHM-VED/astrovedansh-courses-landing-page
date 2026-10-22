(() => {
  'use strict';
  const model = window.AVBookingModel;
  const catalog = window.AV_BOOKING;
  if (!model || !catalog) return;
  const form = document.querySelector('#consult-form');
  const query = new URLSearchParams(location.search).get('plan');
  if (!form) {
    const legacy = model.resolve(query);
    if (legacy) location.replace(legacy.url);
    return;
  }
  const original = model.resolve(query || document.body.dataset.bookingPlan);
  const booking = document.querySelector('#booking');
  const summary = document.querySelector('.booking-summary');
  if (!original) {
    booking.hidden = true;
    summary.hidden = true;
    document.querySelector('#booking-error').hidden = false;
    return;
  }
  let selected = original;
  let handingOff = false;
  const lang = () => document.documentElement.lang === 'hi' ? 'hi' : 'en';
  const money = amount => '₹' + amount.toLocaleString('en-IN');
  const node = (tag, text, className) => {
    const e = document.createElement(tag);
    e.textContent = text;
    if (className) e.className = className;
    return e;
  };
  function field(name, visible, required = false) {
    const input = form.elements[name];
    if (!input) return;
    input.closest('label').hidden = !visible;
    input.disabled = !visible;
    input.required = visible && required;
  }
  function dateNote() {
    const d = model.dates();
    form.elements.birthDate.max = d.today;
    form.elements.sessionDate.min = d.min;
    const date = new Intl.DateTimeFormat(lang() === 'hi' ? 'hi-IN' : 'en-IN', {dateStyle:'long',timeZone:'UTC'}).format(new Date(d.min + 'T00:00:00Z'));
    document.querySelector('#date-note').textContent = lang() === 'hi'
      ? `सबसे पहले ${date} की तारीख चुन सकते हैं। समय और डिलीवरी की पुष्टि टीम करेगी।`
      : `Earliest request date: ${date}. Our team will confirm timing and delivery.`;
    return d;
  }
  function render() {
    const hi = lang() === 'hi', p = selected;
    form.elements.plan.value = p.id;
    summary.replaceChildren();
    summary.append(node('p', hi ? 'चरण 3 · विवरण भरें' : 'STEP 3 · YOUR DETAILS', 'eyebrow'));
    const h1 = node('h1', p.title[lang()]); h1.tabIndex = -1; summary.append(h1);
    const mode = p.mode === 'audio' ? (hi ? 'रिकॉर्डेड वॉइस नोट · लाइव कॉल नहीं' : 'Recorded voice note · not a live call') : p.mode === 'live' ? (hi ? 'लाइव बातचीत' : 'Live conversation') : (hi ? 'व्यक्तिगत लिखित विश्लेषण' : 'Personalized written analysis');
    summary.append(node('p', mode + (p.minutes ? ` · ${p.minutes} ${hi ? 'मिनट' : 'min'}` : ''), 'booking-meta'));
    const back = document.querySelector('.booking-back');
    if (back) {
      back.href = '/pricing.html?guidance=' + (p.items.length > 1 ? 'combos' : p.mode === 'written' ? 'reports' : 'consultation') + '#premium';
      back.textContent = hi ? '← प्लान बदलें' : '← Change plan';
      back.dataset.en = '← Change plan'; back.dataset.hi = '← प्लान बदलें';
    }
    const prices = node('div', '', 'plan-price');
    prices.append(node('strong', money(p.amount)));
    if (p.saving) {
      const old = node('span', ''); old.append(node('s', money(p.individualTotal)), node('small', hi ? 'अलग-अलग लेने पर' : 'Bought separately'));
      prices.append(old);
    }
    summary.append(prices);
    if (p.saving) summary.append(node('p', `${money(p.saving)} ${hi ? 'की बचत' : 'saved'}`, 'plan-saving'));
    const list = node('ul', '', 'plan-inclusions');
    p.lineItems.forEach(item => list.append(node('li', item.title[lang()])));
    if (p.minutes) list.append(node('li', `${p.minutes} ${hi ? 'मिनट' : 'min'} · ${p.astrologer[lang()]}`));
    if (p.mode === 'audio') list.append(node('li', hi ? 'WhatsApp पर रिकॉर्डेड वॉइस नोट · लाइव कॉल नहीं' : 'Recorded voice note on WhatsApp · not a live call'));
    if (p.mode === 'live') list.append(node('li', hi ? 'लाइव सेशन के समय में फॉलो-अप सवाल पूछें' : 'Follow-up questions within the live session'));
    if (p.items.some(id => ['name','astrology_report'].includes(id))) list.append(node('li', catalog.booking.reportDelivery[lang()]));
    const inclusions = node('details', '', 'booking-inclusions');
    inclusions.append(node('summary', hi ? 'इस प्लान में क्या मिलेगा?' : 'What is included?'), list);
    summary.append(inclusions);
    const upgradeBox = document.querySelector('#plan-upgrade');
    upgradeBox.replaceChildren();
    upgradeBox.hidden = !p.upgrade;
    if (p.upgrade) {
      const upgrade = model.resolve(p.upgrade), extra = upgrade.amount - p.amount;
      const added = upgrade.lineItems.filter(item => !p.items.includes(item.id));
      const optional = node('details');
      optional.append(node('summary', hi ? `कॉम्बो का विकल्प देखें · +${money(extra)} (वैकल्पिक)` : `See combo upgrade · +${money(extra)} (optional)`));
      optional.append(node('p', added.map(item => item.title[lang()]).join(' + ') + (hi ? ` · नई कुल कीमत ${money(upgrade.amount)}` : ` · New total ${money(upgrade.amount)}`)));
      const button = node('button', hi ? `${added.length > 1 ? 'दोनों रिपोर्ट जोड़ें' : 'रिपोर्ट जोड़ें'} · +${money(extra)} →` : `Add ${added.length > 1 ? 'both reports' : 'report'} · +${money(extra)} →`, 'plan-cta secondary');
      button.type = 'button';
      button.addEventListener('click', () => {
        selected = upgrade;
        document.dispatchEvent(new CustomEvent('astrovedansh:plan-upgrade', {detail:{from:p.id,to:upgrade.id}}));
        render(); summary.querySelector('h1').focus({preventScroll:true});
      });
      optional.append(button, node('p', hi ? 'इसे चुनना ज़रूरी नहीं है। नीचे मौजूदा प्लान के साथ आगे बढ़ें।' : 'This is optional. Continue below with your current plan.', 'plans-note'));
      upgradeBox.append(optional);
    }
    if (p.id !== original.id) {
      const undo = node('button', hi ? `${original.title.hi} — ${money(original.amount)} पर वापस जाएँ` : `Keep ${original.title.en} — ${money(original.amount)}`, 'back-to-original');
      undo.type = 'button'; undo.addEventListener('click', () => { selected = original; render(); }); summary.append(undo);
    }
    field('birthTime', p.needsBirthTime, true);
    field('birthPlace', p.needsBirthTime, true);
    field('gender', p.needsBirthTime, false);
    field('sessionDate', p.needsAvailability, true);
    field('preferredTime', p.mode === 'live', false);
    field('preferredName', p.includesNameReport, false);
    field('question', true, p.id !== 'name');
    document.querySelector('#availability-label').textContent = p.mode === 'audio' ? (hi ? 'ऑडियो प्राप्त करने की पसंदीदा तारीख' : 'Preferred audio delivery date') : (hi ? 'पसंदीदा सेशन तारीख' : 'Preferred session date');
    document.querySelector('#selected-plan-note').textContent = hi ? `चुना हुआ प्लान: ${p.title.hi} · ${money(p.amount)}` : `Selected plan: ${p.title.en} · ${money(p.amount)}`;
    booking.hidden = false;
    dateNote();
  }
  document.addEventListener('av-language-change', render);
  render();
  const reset = () => {handingOff = false; form.querySelector('[type=submit]').disabled = false;};
  window.addEventListener('pageshow', reset);
  window.addEventListener('focus', reset);
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (handingOff) return;
    const d = dateNote();
    if (!form.reportValidity()) return;
    if (form.elements.birthDate.value > d.today) {form.elements.birthDate.focus(); return;}
    if (selected.needsAvailability && form.elements.sessionDate.value < d.min) {form.elements.sessionDate.focus(); return;}
    const fields = Object.fromEntries(new FormData(form));
    const text = model.message(selected.id, fields);
    const status = document.querySelector('#status');
    status.textContent = lang() === 'hi' ? 'WhatsApp में विवरण जाँचकर Send दबाएँ। टीम की पुष्टि के बाद ही बुकिंग होगी।' : 'Review your details in WhatsApp and press Send. Our team will confirm the booking.';
    handingOff = true;
    form.querySelector('[type=submit]').disabled = true;
    document.dispatchEvent(new CustomEvent('astrovedansh:booking-request', {detail:{plan_id:selected.id,amount:selected.amount}}));
    try {window.location.assign('https://wa.me/' + catalog.booking.whatsapp + '?text=' + encodeURIComponent(text));}
    catch {reset();status.textContent = lang() === 'hi' ? 'WhatsApp नहीं खुला। दोबारा प्रयास करें या +91 90454 32034 पर संपर्क करें।' : 'WhatsApp could not open. Try again or contact +91 90454 32034.';}
  });
})();
