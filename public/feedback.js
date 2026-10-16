(() => {
  const form = document.querySelector('#feedback-form');
  if (!form) return;
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const body = `Name: ${data.get('name')}\nCourse: ${data.get('course')}\nRating: ${data.get('rating') || 'Not specified'}\n\n${data.get('review')}`;
    window.location.href = `mailto:vedanshvallabh@gmail.com?subject=${encodeURIComponent('AstroVedansh Course Feedback')}&body=${encodeURIComponent(body)}`;
    document.querySelector('#review-status').textContent = document.documentElement.lang === 'en'
      ? 'Please send your review from your email app. If it did not open, email vedanshvallabh@gmail.com.'
      : 'अपने ईमेल ऐप से समीक्षा भेजें। ऐप नहीं खुला तो vedanshvallabh@gmail.com पर भेज सकते हैं।';
  });
})();
