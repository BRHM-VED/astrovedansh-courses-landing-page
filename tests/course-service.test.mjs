import test from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import { createHmac } from 'node:crypto';
import { handleCourse,priceAt,OFFER_END,configured,capturedFor } from '../lib/course-service.mjs';
const ids=Array.from({length:24},(_,i)=>'videoid'+String(i).padStart(4,'0'));
function fixture(){
 const sql=new DatabaseSync(':memory:');sql.exec(readFileSync(new URL('../drizzle/0000_wandering_caretaker.sql',import.meta.url),'utf8'));
 const db = {prepare(query) {
   return {bind(...args) {
     return {
       async first() { return sql.prepare(query).get(...args) || null; },
       async all() { return {results: sql.prepare(query).all(...args)}; },
       async run() { return sql.prepare(query).run(...args); }
     };
   }};
 }};
 const env={DB:db,RAZORPAY_KEY_ID:'rzp_live_fixture',RAZORPAY_KEY_SECRET:'test-fixture-secret',RAZORPAY_WEBHOOK_SECRET:'test-fixture-webhook',NUMEROLOGY_VIDEO_IDS:JSON.stringify(ids)};
 const user={userId:'buyer-a',email:'a@example.test'};
 const insert=(owner='buyer-a',status='pending')=>sql.prepare("INSERT INTO course_orders VALUES (?,?,?,NULL,14900,'INR',?,?,NULL)").run('local-one',owner,'order_valid',status,Date.now());
 return {env,user,sql,insert};
}
function req(path,body,origin='https://course.example'){return new Request('https://course.example/api/course/'+path,{method:body?'POST':'GET',headers:{Origin:origin,'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});}
function verifiedBody(secret='test-fixture-secret'){return {razorpay_order_id:'order_valid',razorpay_payment_id:'pay_valid',razorpay_signature:createHmac('sha256',secret).update('order_valid|pay_valid').digest('hex')};}
const payment={id:'pay_valid',order_id:'order_valid',amount:14900,currency:'INR',status:'captured',captured:true,amount_refunded:0};
test('offer price changes at midnight IST',()=>{assert.equal(priceAt(OFFER_END-1),14900);assert.equal(priceAt(OFFER_END),99900)});
test('checkout stays closed without live keys and 24 valid lessons',()=>{const {env}=fixture();assert.equal(configured(env),true);assert.equal(configured({...env,RAZORPAY_KEY_SECRET:''}),false);assert.equal(configured({...env,NUMEROLOGY_VIDEO_IDS:'[]'}),false)});
test('anonymous and unpaid users cannot get lessons',async()=>{const {env,user}=fixture();assert.equal((await handleCourse(req('lessons'),env,null)).status,401);assert.equal((await handleCourse(req('lessons'),env,user)).status,403)});
test('cross-origin order creation is rejected',async()=>{const {env,user}=fixture();assert.equal((await handleCourse(req('order',{},'https://evil.example'),env,user)).status,403)});
test('another account cannot claim a real payment',async()=>{const {env,user,insert}=fixture();insert('buyer-b');assert.equal((await handleCourse(req('verify',verifiedBody()),env,user)).status,404)});
test('forged signature is rejected',async()=>{const {env,user,insert}=fixture();insert();assert.equal((await handleCourse(req('verify',verifiedBody('wrong')),env,user)).status,401)});
test('wrong amount, currency and uncaptured payments cannot unlock',()=>{const order={razorpay_order_id:'order_valid',amount:14900,currency:'INR'};assert.ok(capturedFor(payment,order));for(const change of [{amount:100},{currency:'USD'},{status:'authorized',captured:false},{order_id:'order_other'},{amount_refunded:1}])assert.equal(!!capturedFor({...payment,...change},order),false)});
test('verified captured payment unlocks only the owner and is idempotent',async()=>{const {env,user,insert,sql}=fixture();insert();const old=globalThis.fetch;globalThis.fetch=async()=>Response.json(payment);try{for(let i=0;i<2;i++)assert.equal((await handleCourse(req('verify',verifiedBody()),env,user)).status,200);assert.equal(sql.prepare('SELECT COUNT(*) AS n FROM course_orders WHERE status=\'paid\'').get().n,1);const result=await handleCourse(req('lessons'),env,user);assert.equal(result.status,200);assert.equal((await result.json()).videos.length,24);assert.equal((await handleCourse(req('lessons'),env,{...user,userId:'buyer-b'})).status,403);}finally{globalThis.fetch=old}});
test('signed refund webhook revokes access; unsigned webhook cannot',async()=>{const {env,user,insert,sql}=fixture();insert();sql.prepare("UPDATE course_orders SET status='paid',payment_id='pay_valid',verified_at=?").run(Date.now());const raw=JSON.stringify({event:'refund.processed',payload:{refund:{entity:{payment_id:'pay_valid'}}}});const make=sig=>new Request('https://course.example/api/course/webhook',{method:'POST',headers:{'X-Razorpay-Signature':sig},body:raw});assert.equal((await handleCourse(make('bad'),env,null)).status,401);const old=globalThis.fetch;globalThis.fetch=async()=>Response.json({...payment,status:'refunded',amount_refunded:14900});try{const sig=createHmac('sha256',env.RAZORPAY_WEBHOOK_SECRET).update(raw).digest('hex');assert.equal((await handleCourse(make(sig),env,null)).status,200);assert.equal((await handleCourse(req('lessons'),env,user)).status,403);}finally{globalThis.fetch=old}});
