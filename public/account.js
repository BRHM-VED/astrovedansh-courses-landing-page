(()=>{
 const en=document.querySelector('main').lang==='en',w=(hi,english)=>en?english:hi,$=id=>document.getElementById(id);
 const status=$('account-status');let token=new URLSearchParams(location.hash.slice(1)).get('access');
 // The fragment never reaches the server. Remove it immediately from this history entry.
 if(location.hash)history.replaceState(null,'',location.pathname+location.search);
 const api=async(path,body)=>{const r=await fetch('/api/course/'+path,{method:body?'POST':'GET',credentials:'same-origin',cache:'no-store',headers:body?{'Content-Type':'application/json'}:undefined,body:body?JSON.stringify(body):undefined});const d=await r.json();if(!r.ok)throw Error(d.error||'unavailable');return d;};
 async function unlock(email){const d=await api('lessons'),titles=await fetch(en?'/lesson-titles-en.json':'/lesson-titles-hi.json').then(r=>r.json());
  $('purchase-area').hidden=true;$('access-confirm').hidden=true;$('owned-course').hidden=false;$('account-email').textContent=email||'';status.textContent=w('अपने अध्ययन में आपका स्वागत है।','Welcome to your classroom.');
  const list=$('owned-lessons');list.replaceChildren();d.videos.forEach((id,i)=>{const b=document.createElement('button');b.type='button';b.textContent=(i+1)+'. '+titles[i];b.onclick=()=>{$('owned-player').src='https://www.youtube-nocookie.com/embed/'+id+'?rel=0&playsinline=1';$('active-lesson').textContent=b.textContent;list.querySelectorAll('button').forEach(n=>n.setAttribute('aria-pressed',String(n===b)));};list.append(b);});list.firstElementChild?.click();
 }
 async function refresh(){try{const s=await api('status');
  if(token){$('access-confirm').hidden=false;$('purchase-area').hidden=true;status.textContent='';return;}
  if(s.hasAccess){await unlock(s.email);return;}
  $('request-link').disabled=!s.ready;
  // The fixed merchant page is priced at 149. Do not advertise 999 until that page is updated.
  $('email-checkout').hidden=!s.ready||s.amount!==14900;
  status.textContent=s.ready?w('अपने ईमेल के निजी लिंक से कक्षाएँ खोलें।','Open your classes using the private link in your email.'):w('प्रवेश की तैयारी चल रही है। ईमेल सुविधा जुड़ने के बाद खरीद शुरू होगी। अभी भुगतान न करें।','Enrolment is being prepared. Purchases open after email access is connected. Please do not pay yet.');
 }catch{status.textContent=w('अभी पेज लोड नहीं हुआ। कृपया थोड़ी देर बाद दोबारा खोलें।','The page could not load. Please try again shortly.');}}
 $('email-access-form').onsubmit=async e=>{e.preventDefault();const b=$('request-link');b.disabled=true;try{await api('request-link',{email:$('buyer-email').value,lang:en?'en':'hi'});status.textContent=w('यदि इस ईमेल पर खरीद की पुष्टि हुई है, तो प्रवेश लिंक भेजा जाएगा। अपना इनबॉक्स और स्पैम फ़ोल्डर देखें।','If a purchase is verified for this email, an access link will be sent. Check your inbox and spam folder.');}catch{status.textContent=w('लिंक अभी नहीं भेजा जा सका। कृपया कुछ देर बाद दोबारा प्रयास करें।','The link could not be requested. Please try again later.');}finally{b.disabled=false;}};
 $('consume-link').onclick=async()=>{const b=$('consume-link');b.disabled=true;try{await api('consume',{token});token=null;await refresh();}catch{token=null;$('access-confirm').hidden=true;$('purchase-area').hidden=false;const s=await api('status').catch(()=>({ready:false}));$('request-link').disabled=!s.ready;status.textContent=w('यह लिंक समाप्त हो गया है या इस्तेमाल हो चुका है। अपने खरीद वाले ईमेल पर नया लिंक मँगवाएँ।','This link has expired or was already used. Request a new link using your purchase email.');}finally{b.disabled=false;}};
 $('logout').onclick=async()=>{try{await api('logout',{});location.reload();}catch{status.textContent=w('खाते से बाहर नहीं निकले। कृपया दोबारा प्रयास करें।','Sign-out failed. Please try again.');}};
 refresh();
})();
