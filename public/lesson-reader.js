(() => {
  const article = document.querySelector('[data-lesson-url]');
  if (!article) return;
  const copy = document.querySelector('#copy-notes');
  const save = document.querySelector('#save-article');
  const status = document.querySelector('#lesson-action-status');
  const fallback = document.querySelector('#notes-copy-fallback');
  const text = document.querySelector('#lesson-notes').innerText.trim();
  const key = 'astrovedansh-saved-articles-v1';
  const url = article.dataset.lessonUrl;
  const title = document.querySelector('h1').textContent.trim();
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || '{}'); } catch { /* Storage may be disabled. */ }
  if (!saved || typeof saved !== 'object' || Array.isArray(saved)) saved = {};
  const update = () => {
    save.setAttribute('aria-pressed', String(Boolean(saved[url])));
    save.textContent = saved[url] ? 'सहेजा गया · हटाएँ' : 'लेख सहेजें';
  };
  update();
  copy.addEventListener('click', async () => {
    const notes = `${title}\n${location.origin}/${url}\n\n${text}`;
    try {
      await navigator.clipboard.writeText(notes);
      status.textContent = 'अध्ययन सूत्र कॉपी हो गए हैं।';
      fallback.hidden = true;
    } catch {
      fallback.hidden = false;
      fallback.value = notes;
      fallback.focus();
      fallback.select();
      status.textContent = 'अपने उपकरण के कॉपी विकल्प से चुना हुआ पाठ कॉपी करें।';
    }
  });
  save.addEventListener('click', () => {
    try {
      const next = { ...saved };
      if (next[url]) delete next[url];
      else next[url] = { title, url, notes: text, savedAt: new Date().toISOString() };
      localStorage.setItem(key, JSON.stringify(next));
      saved = next;
      update();
      status.textContent = saved[url]
        ? 'लेख का लिंक और सूत्र इसी ब्राउज़र में सहेज दिए हैं। पत्रिका में “सहेजे हुए” से मिलेंगे। पूरा लेख ऑफ़लाइन डाउनलोड नहीं हुआ है।'
        : 'यह लेख सहेजी हुई सूची से हटा दिया है।';
    } catch {
      status.textContent = 'इस ब्राउज़र में सहेजना बंद है। लेख का लिंक अपने बुकमार्क में रख सकते हैं।';
    }
  });
})();
