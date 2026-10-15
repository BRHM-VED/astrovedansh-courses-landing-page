(()=>{
 const form=document.getElementById('coupon-form');if(!form)return;
 const en=document.documentElement.lang==='en',message=document.getElementById('coupon-feedback'),input=document.getElementById('coupon-input');
 let unlocked=false,active=0,player=null,playerReady=false;
 const titles=[...document.querySelectorAll('.lesson-title')];
 const lessonButtons=titles.map((heading,i)=>{const b=document.createElement('button');b.type='button';b.className='series-lesson-button';b.textContent=heading.textContent;b.dataset.index=i;b.addEventListener('click',()=>choose(i,true));heading.replaceChildren(b);return b;});
 const area=document.getElementById('free-course-player');
 const current=document.createElement('p');current.className='series-current';current.setAttribute('aria-live','polite');area.insertBefore(current,area.querySelector('.coupon-video'));
 const nav=document.createElement('div');nav.className='series-navigation';
 const prev=document.createElement('button'),next=document.createElement('button');prev.type=next.type='button';prev.textContent=en?'← Previous class':'← पिछली कक्षा';next.textContent=en?'Next class →':'अगली कक्षा →';prev.onclick=()=>choose(active-1,true);next.onclick=()=>choose(active+1,true);nav.append(prev,next);area.querySelector('.coupon-video').after(nav);
 const playback=document.createElement('p');playback.className='compact-note';playback.setAttribute('role','status');nav.after(playback);
 function mark(i){active=i;current.textContent=(en?'Class ':'कक्षा ')+(i+1)+(en?' of 24 · ':' / 24 · ')+lessonButtons[i].textContent;prev.disabled=i===0;next.disabled=i===23;lessonButtons.forEach((b,j)=>b.setAttribute('aria-pressed',String(j===i)));}
 function choose(i,play){
  if(i<0||i>=24)return;
  if(!unlocked){message.textContent=en?'Apply NUMEROPRO first to open your classes.':'कक्षाएँ खोलने के लिए पहले NUMEROPRO कूपन लगाएँ।';input.focus();form.scrollIntoView({behavior:'smooth',block:'center'});return;}
  mark(i);
  if(playerReady){player.loadPlaylist({listType:'playlist',list:'PLN80wspGZ5mw',index:i,startSeconds:0});player.setShuffle(false);player.setLoop(false);}
  else playback.textContent=en?'Loading the selected class…':'चुनी गई कक्षा लोड हो रही है…';
  if(play)area.scrollIntoView({behavior:'smooth',block:'start'});
 }
 function initialisePlayer(){
  if(player)return;
  player=new YT.Player('free-course-frame',{events:{onReady:e=>{playerReady=true;e.target.cuePlaylist({listType:'playlist',list:'PLN80wspGZ5mw',index:active,startSeconds:0});e.target.setShuffle(false);e.target.setLoop(false);},onStateChange:e=>{if(e.data===1||e.data===5){const i=e.target.getPlaylistIndex();if(Number.isInteger(i)&&i>=0&&i<24)mark(i);playback.textContent='';}if(e.data===0&&active===23){e.target.stopVideo();playback.textContent=en?'You have reached the end of the course.':'आप पाठ्यक्रम की अंतिम कक्षा तक पहुँच गए हैं।';}},onError:()=>{playback.textContent=en?'This class is not available in the supplied playlist yet.':'दी गई प्लेलिस्ट में यह कक्षा अभी उपलब्ध नहीं है।';}}});
 }
 function loadPlayer(){
  const frame=document.getElementById('free-course-frame');
  if(!frame.src)frame.src='https://www.youtube-nocookie.com/embed/videoseries?list=PLN80wspGZ5mw&enablejsapi=1&playsinline=1&rel=0&origin='+encodeURIComponent(location.origin);
  if(window.YT?.Player){initialisePlayer();return;}
  if(document.getElementById('course-youtube-api'))return;
  const prior=window.onYouTubeIframeAPIReady;window.onYouTubeIframeAPIReady=()=>{if(prior)prior();initialisePlayer();};
  const script=document.createElement('script');script.id='course-youtube-api';script.src='https://www.youtube.com/iframe_api';script.onerror=()=>{playback.textContent=en?'Video controls could not load. Please reload the page.':'वीडियो के बटन लोड नहीं हुए। कृपया पेज दोबारा खोलें।';};document.head.append(script);
 }
 const unlock=()=>{
  document.querySelector('.coupon-discount').hidden=false;document.querySelector('[data-coupon-total]').textContent='₹0';
  message.textContent=en?'NUMEROPRO applied. You saved ₹999. Your course is free.':'NUMEROPRO लागू हुआ। ₹999 की छूट मिली। आपका पाठ्यक्रम निःशुल्क है।';message.className='coupon-success';
  document.getElementById('start-free-course').hidden=false;document.getElementById('free-course-player').hidden=false;
  unlocked=true;mark(active);loadPlayer();
  input.value='NUMEROPRO';input.setAttribute('aria-invalid','false');form.querySelector('button').textContent=en?'Applied ✓':'लागू हुआ ✓';
  try{sessionStorage.setItem('astro-numeropro','applied');}catch{}
 };
 form.addEventListener('submit',e=>{e.preventDefault();if(input.value.trim().toUpperCase()!=='NUMEROPRO'){input.setAttribute('aria-invalid','true');message.className='coupon-error';message.textContent=en?'Invalid coupon. Enter NUMEROPRO for the full discount.':'कूपन सही नहीं है। पूरी छूट के लिए NUMEROPRO डालें।';return;}unlock();});
 try{if(sessionStorage.getItem('astro-numeropro')==='applied')unlock();}catch{}
})();
