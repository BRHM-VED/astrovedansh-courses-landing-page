(() => {
  const buttons = [...document.querySelectorAll('[data-lesson]')];
  const frame = document.getElementById('numerology-player');
  if (!frame || !buttons.length) return;
  const en = document.documentElement.lang === 'en';
  const status = document.getElementById('lesson-status');
  let player, ready = false, pending = 0, timer;
  const source = new URL(frame.src);
  source.searchParams.set('origin', location.origin);
  frame.src = source.toString();
  const message = (english, hindi) => { status.textContent = en ? english : hindi; };
  function select(index) {
    buttons.forEach((b, i) => b.setAttribute('aria-pressed', String(i === index)));
    document.getElementById('lesson-heading').textContent = buttons[index].textContent;
  }
  function load() {
    if (!ready) return;
    message('Loading selected class…', 'चुनी गई कक्षा खुल रही है…');
    player.loadPlaylist({list: 'PLN80wspGZ5mw', listType: 'playlist', index: pending, startSeconds: 0});
  }
  buttons.forEach((button, index) => button.addEventListener('click', () => {
    pending = index;
    select(index);
    if (ready) load();
    else message('Connecting to the video player. If it does not load, contact our team below.', 'वीडियो से जुड़ रहे हैं। न खुलने पर नीचे दिए सम्पर्क विकल्प से टीम को बताएँ।');
    document.querySelector('.lesson-player-panel').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start'});
  }));
  window.onYouTubeIframeAPIReady = () => {
    player = new YT.Player(frame, {events: {
      onReady: () => { ready = true; if (pending > 0) load(); },
      onStateChange: event => {
        if (event.data === 1 || event.data === 5) {
          const index = player.getPlaylistIndex();
          if (index >= 0 && index < buttons.length) select(index);
          message('Use the player controls to watch this class.', 'यह कक्षा देखने के लिए वीडियो के नियंत्रणों का उपयोग करें।');
        }
      },
      onError: () => message('This class could not be loaded. Please contact our team using “Ask a question”.', 'यह कक्षा नहीं खुल सकी। कृपया “प्रश्न पूछें” से हमारी टीम को बताएँ।')
    }});
  };
  const script = document.createElement('script');
  script.src = 'https://www.youtube.com/iframe_api';
  script.onerror = () => message('Video service unavailable. Please contact our team.', 'वीडियो सेवा उपलब्ध नहीं है। कृपया हमारी टीम से सम्पर्क करें।');
  document.head.appendChild(script);
})();
