/* Pure booking request model. No payments, storage or external calls. */
(() => {
  'use strict';
  const catalog = window.AV_BOOKING;
  function resolve(id) {
    const key = Object.hasOwn(catalog.aliases, id) ? catalog.aliases[id] : id;
    return Object.hasOwn(catalog.plans, key) ? catalog.plans[key] : null;
  }
  function dates(now = new Date()) {
    const parts = new Intl.DateTimeFormat('en-CA', {timeZone:'Asia/Kolkata',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now);
    const v = Object.fromEntries(parts.map(x => [x.type, x.value]));
    const today = `${v.year}-${v.month}-${v.day}`;
    const d = new Date(today + 'T00:00:00Z');
    d.setUTCDate(d.getUTCDate() + 2);
    return {today, min:d.toISOString().slice(0,10)};
  }
  function message(id, fields) {
    const p = resolve(id);
    if (!p) throw new Error('Unknown plan');
    const get = key => String(fields[key] || '').trim();
    const lines = ['Radhe Radhe AstroVedansh, I would like to request a booking.', '',
      `Plan ID: ${p.id}`, `Plan: ${p.title.en}`, `Package fee: ₹${p.amount}`];
    if (p.items.length > 1) lines.push(`Individual total: ₹${p.individualTotal}`, `Combo saving: ₹${p.saving}`, 'Included services (one package; do not bill these items separately):');
    else lines.push('Included service:');
    for (const item of p.lineItems) lines.push(`- ${item.title.en} [${item.id}] × ${item.quantity}`);
    if (p.minutes) lines.push(`Duration: ${p.minutes} minutes`, `Astrologer: ${p.astrologer.en}`);
    lines.push(`Format: ${p.mode === 'audio' ? 'Recorded voice note on WhatsApp; not a live call' : p.mode === 'live' ? 'One-to-one live consultation' : 'Personalized written report'}`);
    lines.push('', `Name (exact spelling): ${get('name')}`, `Date of birth: ${get('birthDate')}`);
    if (p.needsBirthTime) lines.push(`Time of birth: ${get('birthTime')}`, `Place of birth: ${get('birthPlace')}`);
    if (get('gender')) lines.push(`Gender: ${get('gender')}`);
    lines.push(`WhatsApp: ${get('phone')}`);
    if (get('email')) lines.push(`Email: ${get('email')}`);
    if (get('question')) lines.push(`Main question: ${get('question')}`);
    if (p.includesNameReport && get('preferredName')) lines.push(`Preferred name / spelling: ${get('preferredName')}`);
    if (p.needsAvailability) {
      lines.push(`${p.mode === 'audio' ? 'Preferred audio delivery date' : 'Preferred session date'} (India): ${get('sessionDate')}`);
      if (p.mode === 'live' && get('preferredTime')) lines.push(`Preferred time (IST): ${get('preferredTime')}`);
    }
    lines.push('', 'I consent to sharing these details for the selected plan.', 'Please confirm availability, report delivery terms, final payable amount and any applicable taxes before payment. This is a booking request, not a payment confirmation.');
    return lines.join('\n');
  }
  window.AVBookingModel = Object.freeze({resolve,dates,message});
})();
