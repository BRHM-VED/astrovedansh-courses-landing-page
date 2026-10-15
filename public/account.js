(() => {
 const en=document.querySelector('main').lang==='en';
 const text=(hi,english)=>en?english:hi;
 const status=document.getElementById('account-status'),button=document.getElementById('purchase-button');
 if(!button)return;
 let busy=false, polling=0;
 async function api(path,body){const r=await fetch('/api/course/'+path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:undefined,body:body?JSON.stringify(body):undefined,cache:'no-store',credentials:'same-origin'});const data=await r.json();if(!r.ok)throw new Error(data.error||'service_unavailable');return data;}
 const fail=error=>{status.textContent=error.message==='too_many_attempts'?text('कृपया कुछ मिनट बाद दोबारा प्रयास करें।','Please wait a few minutes before trying again.'):text('अभी जाँच पूरी नहीं हुई। यदि भुगतान हो चुका है तो दोबारा भुगतान न करें; स्थिति फिर जाँचें।','Verification is not complete. If you have paid, do not pay again; check your payment status again.');};
 async function unlock(){
  const data=await api('lessons');
  const syllabus=await fetch(en?'/lesson-titles-en.json':'/lesson-titles-hi.json').then(r=>r.json());
  const list=document.getElementById('owned-lessons'),frame=document.getElementById('owned-player');list.replaceChildren();
  data.videos.forEach((id,index)=>{const b=document.createElement('button');b.type='button';b.textContent=(index+1)+'. '+syllabus[index];b.addEventListener('click',()=>{frame.src='https://www.youtube-nocookie.com/embed/'+id+'?rel=0&playsinline=1';document.getElementById('active-lesson').textContent=b.textContent;list.querySelectorAll('button').forEach(n=>n.setAttribute('aria-pressed',String(n===b)));});list.append(b);});
  document.getElementById('purchase-area').hidden=true;document.getElementById('owned-course').hidden=false;list.firstElementChild.click();
 }
 async function refresh(){
  try{const state=await api('status');
   if(!state.signedIn){location.reload();return;}
   if(state.hasAccess){await unlock();return;}
   if(!state.ready){button.disabled=true;button.textContent=text('प्रवेश जल्द शुरू होगा','Enrolment opens soon');status.textContent=text('ऑनलाइन प्रवेश अभी उपलब्ध नहीं है। अभी कोई भुगतान न करें।','Online enrolment is not available yet. Please do not make a payment now.');return;}
   status.textContent=text('सफल भुगतान की पुष्टि के बाद इसी खाते में सभी कक्षाएँ खुलेंगी।','All classes unlock in this account once your successful payment is verified.');
   button.textContent=text('₹'+state.amount/100+' में प्रवेश लें','Enrol for ₹'+state.amount/100);button.disabled=busy;
  }catch(e){button.disabled=true;fail(e);}
 }
 function checkoutScript(){if(window.Razorpay)return Promise.resolve();return new Promise((resolve,reject)=>{const s=document.createElement('script');s.src='https://checkout.razorpay.com/v1/checkout.js';s.onload=resolve;s.onerror=reject;document.head.append(s);});}
 async function poll(){polling=0;for(;polling<12;polling++){await new Promise(r=>setTimeout(r,3000));const state=await api('status');if(state.hasAccess){await unlock();return;}}status.textContent=text('भुगतान की पुष्टि की प्रतीक्षा है। दोबारा भुगतान न करें। कुछ देर बाद स्थिति फिर जाँचें।','Waiting for payment confirmation. Do not pay again. Check your status again shortly.');}
 button.addEventListener('click',async()=>{
  if(busy)return;busy=true;button.disabled=true;
  try{await checkoutScript();const order=await api('order',{});if(order.hasAccess){await unlock();busy=false;return;}
   const checkout=new window.Razorpay({key:order.keyId,order_id:order.orderId,amount:order.amount,currency:order.currency,name:'AstroVedansh',description:text('अंकज्योतिष पाठ्यक्रम — 24 कक्षाएँ','Numerology Course — 24 Classes'),prefill:{email:order.email},theme:{color:'#682e23'},modal:{ondismiss:()=>{busy=false;refresh();}},handler:async result=>{
    try{const verified=await api('verify',result);if(verified.hasAccess)await unlock();else{status.textContent=text('भुगतान की पुष्टि हो रही है…','Verifying payment…');await poll();}}catch(e){fail(e);}finally{busy=false;}
   }});checkout.on('payment.failed',()=>{busy=false;status.textContent=text('भुगतान पूरा नहीं हुआ। स्थिति जाँचकर दोबारा प्रयास करें।','Payment was not completed. Check the status before retrying.');button.disabled=false;});checkout.open();
  }catch(e){busy=false;fail(e);button.disabled=false;}
 });
 document.getElementById('refresh-access').addEventListener('click',refresh);
 refresh();
})();
