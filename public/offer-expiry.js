if(Date.now() >= Date.parse('2027-01-01T00:00:00+05:30')) {
 document.querySelectorAll('.numerology-price del,.numerology-deadline').forEach(n=>n.hidden=true);
 document.querySelectorAll('.numerology-price strong').forEach(n=>n.textContent='₹999');
 document.querySelectorAll('.numerology-pay').forEach(n=>n.textContent=document.documentElement.lang==='en'?'Enrol for ₹999':'₹999 में प्रवेश लें');
}
