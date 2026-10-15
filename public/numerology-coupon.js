(()=>{
 const form=document.getElementById('coupon-form');if(!form)return;
 const en=document.documentElement.lang==='en',message=document.getElementById('coupon-feedback'),input=document.getElementById('coupon-input');
 const unlock=()=>{
  document.querySelector('.coupon-discount').hidden=false;document.querySelector('[data-coupon-total]').textContent='₹0';
  message.textContent=en?'NUMEROPRO applied. You saved ₹999. Your course is free.':'NUMEROPRO लागू हुआ। ₹999 की छूट मिली। आपका पाठ्यक्रम निःशुल्क है।';message.className='coupon-success';
  document.getElementById('start-free-course').hidden=false;document.getElementById('free-course-player').hidden=false;
  const frame=document.getElementById('free-course-frame');if(!frame.src)frame.src='https://www.youtube-nocookie.com/embed/videoseries?list=PLN80wspGZ5mw&rel=0';
  input.value='NUMEROPRO';input.setAttribute('aria-invalid','false');form.querySelector('button').textContent=en?'Applied ✓':'लागू हुआ ✓';
  try{sessionStorage.setItem('astro-numeropro','applied');}catch{}
 };
 form.addEventListener('submit',e=>{e.preventDefault();if(input.value.trim().toUpperCase()!=='NUMEROPRO'){input.setAttribute('aria-invalid','true');message.className='coupon-error';message.textContent=en?'Invalid coupon. Enter NUMEROPRO for the full discount.':'कूपन सही नहीं है। पूरी छूट के लिए NUMEROPRO डालें।';return;}unlock();});
 try{if(sessionStorage.getItem('astro-numeropro')==='applied')unlock();}catch{}
})();
