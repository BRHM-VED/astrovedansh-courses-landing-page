import {validHmac,lessonIds,priceAt} from './course-service.mjs';
export const ORIGIN='https://astrovedansh-basic-astrology.astrovedansh.chatgpt.site';
const COOKIE='__Host-astro-course';
const enc=new TextEncoder();
const hex=b=>Array.from(new Uint8Array(b),x=>x.toString(16).padStart(2,'0')).join('');
export const hash=async s=>hex(await crypto.subtle.digest('SHA-256',enc.encode(s)));
const random=()=>hex(crypto.getRandomValues(new Uint8Array(32)));
const emailOf=s=>typeof s==='string'&&s.length<=254&&/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(s.trim())?s.trim().toLowerCase():null;
const reply=(data,status=200,headers={})=>Response.json(data,{status,headers:{'Cache-Control':'private, no-store','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff',...headers}});
const sql=(env,q,...args)=>env.DB.prepare(q).bind(...args);
// Only provider-owned entity identifiers are supported. Never match an amount,
// description, customer-supplied note or email alone to decide which course was purchased.
export function courseSource(event,env){
 const entity=env.COURSE_SOURCE_KIND==='payment_link'?event.payload?.payment_link?.entity:env.COURSE_SOURCE_KIND==='payment_page'?event.payload?.payment_page?.entity:null;
 return !!(entity && entity.id===env.COURSE_SOURCE_ID && entity.entity===env.COURSE_SOURCE_KIND);
}
export function ready(env){return !!(env.COURSE_EMAIL_ENABLED==='true'&&env.COURSE_SOURCE_VERIFIED==='true'&&['payment_link','payment_page'].includes(env.COURSE_SOURCE_KIND)&&env.COURSE_SOURCE_ID&&env.RAZORPAY_ACCOUNT_ID&&env.RAZORPAY_WEBHOOK_SECRET&&env.RESEND_API_KEY&&env.COURSE_EMAIL_FROM&&env.COURSE_TOKEN_SECRET?.length>=32&&lessonIds(env));}
async function tokenFor(env,id){const key=await crypto.subtle.importKey('raw',enc.encode(env.COURSE_TOKEN_SECRET),{name:'HMAC',hash:'SHA-256'},false,['sign']);return hex(await crypto.subtle.sign('HMAC',key,enc.encode('course-login:'+id)));}
async function paid(env,email){return !!await sql(env,"SELECT payment_id FROM email_purchases WHERE email=? AND status='paid' LIMIT 1",email).first();}
async function session(env,request){
 const raw=request.headers.get('Cookie')?.split(';').map(s=>s.trim()).find(s=>s.startsWith(COOKIE+'='))?.slice(COOKIE.length+1);
 if(!raw||!/^\w{64}$/.test(raw))return null;
 const s=await sql(env,'SELECT email FROM email_sessions WHERE token_hash=? AND expires_at>?',await hash(raw),Date.now()).first();
 return s&&await paid(env,s.email)?s.email:null;
}
async function limit(env,key,max,period){
 const bucket=Math.floor(Date.now()/period);const row=await sql(env,'INSERT INTO email_limits (key,bucket,count) VALUES (?,?,1) ON CONFLICT(key) DO UPDATE SET count=CASE WHEN bucket=excluded.bucket THEN count+1 ELSE 1 END,bucket=excluded.bucket RETURNING count',key,bucket).first();return row.count<=max;
}
async function sendLink(env,email,reason,lang='hi'){
 let row=await sql(env,'SELECT * FROM email_links WHERE reason=?',reason).first();
 if(!row){const id=crypto.randomUUID(),token=await tokenFor(env,id),now=Date.now();await sql(env,'INSERT OR IGNORE INTO email_links (id,reason,email,token_hash,created_at,expires_at,lang) VALUES (?,?,?,?,?,?,?)',id,reason,email,await hash(token),now,now+15*60000,lang).run();row=await sql(env,'SELECT * FROM email_links WHERE reason=?',reason).first();}
 if(row.sent_at)return;
 // Renew an unsent, expired token on a provider retry; never email a dead link.
 if(row.expires_at<=Date.now()){
  const id=crypto.randomUUID(),token=await tokenFor(env,id),now=Date.now();
  await sql(env,'UPDATE email_links SET id=?,token_hash=?,created_at=?,expires_at=?,used_at=NULL WHERE id=? AND sent_at IS NULL',id,await hash(token),now,now+15*60000,row.id).run();
  row=await sql(env,'SELECT * FROM email_links WHERE reason=?',reason).first();
  if(row.sent_at)return;
 }
 const token=await tokenFor(env,row.id),en=row.lang==='en';
 const link=ORIGIN+'/account'+(en?'?lang=en':'')+'#access='+token;
 const label=en?'Open my course':'अपना पाठ्यक्रम खोलें';
 const intro=en?'Your private link to the 24-class numerology course is ready.':'24 कक्षाओं वाले अंकज्योतिष पाठ्यक्रम का आपका निजी प्रवेश लिंक तैयार है।';
 const note=en?'This link expires 15 minutes after it was requested and works once. Do not forward it. If you did not request it, ignore this email.':'यह लिंक अनुरोध के 15 मिनट बाद समाप्त होगा और केवल एक बार चलेगा। इसे किसी और को न भेजें। यदि आपने अनुरोध नहीं किया, तो इस ईमेल को अनदेखा करें।';
 const res=await fetch('https://api.resend.com/emails',{method:'POST',headers:{Authorization:'Bearer '+env.RESEND_API_KEY,'Content-Type':'application/json','Idempotency-Key':'course-link/'+row.id},body:JSON.stringify({from:env.COURSE_EMAIL_FROM,to:[email],subject:en?'AstroVedansh — Your course access':'AstroVedansh — आपके पाठ्यक्रम का प्रवेश लिंक',text:intro+'\n\n'+label+': '+link+'\n\n'+note,html:'<div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;padding:32px;background:#fff9ef;color:#542b22"><h1>AstroVedansh®</h1><p>'+intro+'</p><p><a style="display:inline-block;background:#682e23;color:white;padding:16px 24px;text-decoration:none;border-radius:6px" href="'+link+'">'+label+'</a></p><p>'+note+'</p></div>'}),signal:AbortSignal.timeout(12000)});
 if(!res.ok)throw Error('email_delivery_pending');
 await sql(env,'UPDATE email_links SET sent_at=? WHERE id=?',Date.now(),row.id).run();
}
async function webhook(request,env){
 const raw=await request.text();if(raw.length>65536)return reply({error:'payload_too_large'},413);
 if(!env.RAZORPAY_WEBHOOK_SECRET)return reply({error:'not_configured'},503);
 if(!await validHmac(env.RAZORPAY_WEBHOOK_SECRET,raw,request.headers.get('X-Razorpay-Signature')))return reply({error:'invalid_signature'},401);
 const event=JSON.parse(raw);
 if(!env.RAZORPAY_ACCOUNT_ID||event.account_id!==env.RAZORPAY_ACCOUNT_ID)return reply({error:'wrong_account'},403);
 const p=event.payload?.payment?.entity;
 if(['refund.processed','payment.dispute.created'].includes(event.event)){
  const id=event.payload?.refund?.entity?.payment_id||event.payload?.dispute?.entity?.payment_id||p?.id;
  if(!/^pay_[A-Za-z0-9]+$/.test(id||''))return reply({received:true});
  // Tombstones also handle a refund/dispute arriving before the capture event.
  await sql(env,"INSERT INTO email_purchases(payment_id,email,status,amount,created_at) VALUES (?,NULL,'revoked',0,?) ON CONFLICT(payment_id) DO UPDATE SET status='revoked'",id,Date.now()).run();return reply({received:true});
 }
 if(!['payment.captured','payment_link.paid','order.paid'].includes(event.event))return reply({received:true});
 if(!ready(env))return reply({error:'not_configured'},503);
 if(!courseSource(event,env))return reply({received:true,ignored:true});
 const email=emailOf(p?.email);
 if(!email||!/^pay_[A-Za-z0-9]+$/.test(p?.id||'')||p.status!=='captured'||p.captured!==true||p.currency!=='INR'||p.amount_refunded>0||!Number.isInteger(p.created_at)||p.created_at*1000>Date.now()+300000||p.amount!==priceAt(p.created_at*1000))return reply({received:true,ignored:true});
 await sql(env,"INSERT OR IGNORE INTO email_purchases(payment_id,email,status,amount,created_at) VALUES (?,?,'paid',?,?)",p.id,email,p.amount,Date.now()).run();
 const saved=await sql(env,'SELECT * FROM email_purchases WHERE payment_id=?',p.id).first();
 if(saved.status==='paid'&&saved.email===email)await sendLink(env,email,'purchase:'+p.id);
 return reply({received:true});
}
export async function handleEmailCourse(request,env){
 if(!env.DB)return reply({error:'service_unavailable'},503);
 const path=new URL(request.url).pathname.split('/').pop();
 if(request.method==='POST'&&path!=='webhook'&&request.headers.get('Origin')!==ORIGIN)return reply({error:'invalid_origin'},403);
 if(Number(request.headers.get('Content-Length')||0)>65536)return reply({error:'payload_too_large'},413);
 try{
  if(path==='webhook'&&request.method==='POST')return await webhook(request,env);
  if(path==='status'&&request.method==='GET'){const email=await session(env,request);return reply({ready:ready(env),hasAccess:!!email,email,amount:priceAt()});}
  if(path==='lessons'&&request.method==='GET'){if(!await session(env,request))return reply({error:'access_required'},401);const videos=lessonIds(env);return videos?reply({videos}):reply({error:'lessons_unavailable'},503);}
  if(path==='logout'&&request.method==='POST'){
   const raw=request.headers.get('Cookie')?.split(';').map(s=>s.trim()).find(s=>s.startsWith(COOKIE+'='))?.slice(COOKIE.length+1);
   if(raw)await sql(env,'DELETE FROM email_sessions WHERE token_hash=?',await hash(raw)).run();
   return reply({ok:true},200,{'Set-Cookie':COOKIE+'=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0'});
  }
  if(path==='request-link'&&request.method==='POST'){
   if(!ready(env))return reply({error:'not_configured'},503);
   const raw=await request.text();if(raw.length>2048)return reply({error:'invalid_request'},400);const data=JSON.parse(raw),email=emailOf(data.email);
   if(!email)return reply({error:'invalid_email'},400);
   const ip=request.headers.get('CF-Connecting-IP')||'shared';
   if(!await limit(env,'ip:'+await hash(ip),20,3600000))return reply({error:'try_later'},429);
   if(await limit(env,'mail:'+await hash(email),3,3600000)&&await paid(env,email)){
    try{await sendLink(env,email,'request:'+await hash(email)+':'+Math.floor(Date.now()/300000),data.lang==='en'?'en':'hi');}catch{console.error('course_email_delivery_pending');}
   }
   return reply({message:'If this email has a verified purchase, an access link will be sent.'},202);
  }
  if(path==='consume'&&request.method==='POST'){
   const raw=await request.text();if(raw.length>1024)return reply({error:'invalid_link'},400);const {token}=JSON.parse(raw);
   if(!/^[a-f0-9]{64}$/.test(token||''))return reply({error:'invalid_link'},400);
   const digest=await hash(token);
   const existing=await sql(env,'SELECT email FROM email_links WHERE token_hash=? AND used_at IS NULL AND expires_at>?',digest,Date.now()).first();
   if(!existing||!await paid(env,existing.email))return reply({error:'expired_or_used'},401);
   // One atomic UPDATE claims the token; concurrent/replayed requests cannot both succeed.
   const claimed=await sql(env,'UPDATE email_links SET used_at=? WHERE token_hash=? AND used_at IS NULL AND expires_at>? RETURNING email',Date.now(),digest,Date.now()).first();
   if(!claimed)return reply({error:'expired_or_used'},401);
   const sessionToken=random(),expires=Date.now()+30*86400000;
   await sql(env,'INSERT INTO email_sessions(token_hash,email,expires_at) VALUES (?,?,?)',await hash(sessionToken),claimed.email,expires).run();
   return reply({hasAccess:true},200,{'Set-Cookie':COOKIE+'='+sessionToken+'; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=2592000'});
  }
  return reply({error:'not_found'},404);
 }catch{return reply({error:'service_unavailable'},503);}
}
