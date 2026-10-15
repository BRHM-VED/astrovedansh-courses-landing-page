export const COURSE = 'numerology-24';
export const OFFER_END = Date.parse('2027-01-01T00:00:00+05:30');
export const priceAt = (now = Date.now()) => now < OFFER_END ? 14900 : 99900;
export function lessonIds(env) {
  try { const ids = JSON.parse(env.NUMEROLOGY_VIDEO_IDS || '[]');
    return Array.isArray(ids) && ids.length === 24 && ids.every(id => /^[A-Za-z0-9_-]{11}$/.test(id)) && new Set(ids).size === 24 ? ids : null;
  } catch { return null; }
}
export const configured = env => !!(env.RAZORPAY_KEY_ID?.startsWith('rzp_live_') && env.RAZORPAY_KEY_SECRET && env.RAZORPAY_WEBHOOK_SECRET && lessonIds(env));
export async function validHmac(secret, message, signature) {
  if (!secret || !/^[a-f0-9]{64}$/i.test(signature || '')) return false;
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret), {name:'HMAC', hash:'SHA-256'}, false, ['verify']);
  const bytes = new Uint8Array(signature.match(/../g).map(hex => parseInt(hex,16)));
  return crypto.subtle.verify('HMAC', key, bytes, new TextEncoder().encode(message));
}
export function capturedFor(payment, order) {
  return payment?.id && payment.order_id === order.razorpay_order_id && payment.amount === order.amount && payment.currency === order.currency && payment.status === 'captured' && payment.captured === true && (payment.amount_refunded || 0) === 0;
}
const response = (data, status=200) => Response.json(data, {status, headers:{'Cache-Control':'private, no-store','Vary':'Cookie','X-Content-Type-Options':'nosniff'}});
const error = (code,status) => response({error:code},status);
async function razorpay(env, path, method='GET', body) {
  const res = await fetch('https://api.razorpay.com/v1/'+path, {method, headers:{Authorization:'Basic '+btoa(env.RAZORPAY_KEY_ID+':'+env.RAZORPAY_KEY_SECRET),'Content-Type':'application/json'}, body:body ? JSON.stringify(body):undefined, signal:AbortSignal.timeout(12000)});
  if (!res.ok) throw new Error('Payment service unavailable');
  return res.json();
}
async function updatePayment(db, env, order, payment) {
  if (capturedFor(payment, order)) {
    await db.prepare("UPDATE course_orders SET status='paid', payment_id=?, verified_at=? WHERE id=? AND (payment_id IS NULL OR payment_id=?)").bind(payment.id,Date.now(),order.id,payment.id).run();
    return true;
  }
  if (payment?.order_id === order.razorpay_order_id && (payment.status === 'refunded' || payment.amount_refunded > 0)) {
    await db.prepare("UPDATE course_orders SET status='refunded', verified_at=? WHERE id=?").bind(Date.now(),order.id).run();
  }
  return false;
}
async function access(db,env,userId) {
  const paid = await db.prepare("SELECT * FROM course_orders WHERE user_id=? AND status='paid' ORDER BY created_at DESC LIMIT 5").bind(userId).all();
  for (const order of paid.results) {
    if (order.verified_at && Date.now()-order.verified_at < 60000) return true;
    const payment = await razorpay(env,'payments/'+encodeURIComponent(order.payment_id));
    if (await updatePayment(db,env,order,payment)) return true;
  }
  return false;
}
async function reconcile(db,env,userId) {
  const rows = await db.prepare("SELECT * FROM course_orders WHERE user_id=? AND status='pending' AND razorpay_order_id IS NOT NULL ORDER BY created_at DESC LIMIT 3").bind(userId).all();
  for (const order of rows.results) {
    const payments = await razorpay(env,'orders/'+encodeURIComponent(order.razorpay_order_id)+'/payments');
    for (const payment of (payments.items || [])) if (await updatePayment(db,env,order,payment)) return true;
  }
  return false;
}
export async function handleCourse(request, env, user) {
  const url = new URL(request.url); const path = url.pathname.split('/').pop(); const db = env.DB;
  if (!db) return error('service_unavailable',503);
  if (request.method === 'POST' && path !== 'webhook' && request.headers.get('Origin') !== url.origin) return error('invalid_origin',403);
  if (Number(request.headers.get('Content-Length') || 0)>65536) return error('payload_too_large',413);
  try {
    if (path === 'webhook' && request.method === 'POST') {
      if (!env.RAZORPAY_WEBHOOK_SECRET) return error('not_configured',503);
      const raw=await request.text(); if (raw.length>65536) return error('payload_too_large',413);
      if (!await validHmac(env.RAZORPAY_WEBHOOK_SECRET,raw,request.headers.get('X-Razorpay-Signature'))) return error('invalid_signature',401);
      const event=JSON.parse(raw);
      if (!['payment.captured','order.paid','refund.processed','payment.dispute.created'].includes(event.event)) return response({received:true});
      const id=event.payload?.payment?.entity?.id || event.payload?.refund?.entity?.payment_id || event.payload?.dispute?.entity?.payment_id;
      if (!/^pay_[A-Za-z0-9]+$/.test(id || '')) return response({received:true});
      const payment=await razorpay(env,'payments/'+id);
      const order=await db.prepare('SELECT * FROM course_orders WHERE razorpay_order_id=?').bind(payment.order_id).first();
      if (order) {
        if (event.event==='payment.dispute.created') await db.prepare("UPDATE course_orders SET status='disputed' WHERE id=?").bind(order.id).run();
        else if (order.status!=='disputed') await updatePayment(db,env,order,payment);
      }
      return response({received:true});
    }
    if (path==='status' && request.method==='GET') {
      const ready=configured(env);
      let hasAccess=false;
      if (user && ready) hasAccess=await access(db,env,user.userId) || await reconcile(db,env,user.userId);
      return response({signedIn:!!user,email:user?.email || null,ready,hasAccess,amount:priceAt(),currency:'INR'});
    }
    if (!user) return error('sign_in_required',401);
    if (!configured(env)) return error('not_configured',503);
    if (path==='order' && request.method==='POST') {
      if (await access(db,env,user.userId)) return response({hasAccess:true});
      const recent=await db.prepare('SELECT COUNT(*) AS count FROM course_orders WHERE user_id=? AND created_at>?').bind(user.userId,Date.now()-600000).first();
      if (recent.count>=3) return error('too_many_attempts',429);
      const id=crypto.randomUUID(), amount=priceAt();
      await db.prepare("INSERT INTO course_orders (id,user_id,amount,currency,status,created_at) VALUES (?,?,?,'INR','creating',?)").bind(id,user.userId,amount,Date.now()).run();
      const order=await razorpay(env,'orders','POST',{amount,currency:'INR',receipt:id,notes:{course:COURSE}});
      if (!/^order_[A-Za-z0-9]+$/.test(order.id || '') || order.amount!==amount || order.currency!=='INR') throw new Error('Invalid order');
      await db.prepare("UPDATE course_orders SET razorpay_order_id=?,status='pending' WHERE id=?").bind(order.id,id).run();
      return response({keyId:env.RAZORPAY_KEY_ID,orderId:order.id,amount,currency:'INR',email:user.email});
    }
    if (path==='verify' && request.method==='POST') {
      const raw=await request.text();if(raw.length>4096)return error('payload_too_large',413);
      const data=JSON.parse(raw);
      if (!/^order_[A-Za-z0-9]+$/.test(data.razorpay_order_id || '') || !/^pay_[A-Za-z0-9]+$/.test(data.razorpay_payment_id || '')) return error('invalid_payment',400);
      const order=await db.prepare('SELECT * FROM course_orders WHERE razorpay_order_id=? AND user_id=?').bind(data.razorpay_order_id,user.userId).first();
      if (!order) return error('order_not_found',404);
      if (['refunded','disputed'].includes(order.status)) return error('access_revoked',403);
      if (!await validHmac(env.RAZORPAY_KEY_SECRET,order.razorpay_order_id+'|'+data.razorpay_payment_id,data.razorpay_signature)) return error('invalid_signature',401);
      const payment=await razorpay(env,'payments/'+data.razorpay_payment_id);
      if (!await updatePayment(db,env,order,payment)) return response({hasAccess:false,pending:true},202);
      return response({hasAccess:true});
    }
    if (path==='lessons' && request.method==='GET') {
      if (!await access(db,env,user.userId)) return error('purchase_required',403);
      return response({videos:lessonIds(env)});
    }
    return error('not_found',404);
  } catch { return error('service_unavailable',503); }
}
