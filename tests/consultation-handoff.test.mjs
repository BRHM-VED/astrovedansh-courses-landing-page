import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
function setup(plan, valid=true){
 const fields=Object.fromEntries(Object.entries({plan,name:' QA Test ',gender:'Other',birthDate:'2000-01-01',birthTime:'12:00',birthPlace:' Test City ',phone:'+910000000000',email:'qa@example.test',question:' Test question & follow-up? ',sessionDate:'2099-01-01'}).map(([k,value])=>[k,{value,focus(){}}]));
 let submit;const handoffs=[];const status={textContent:''},note={textContent:''};
 const form={elements:fields,reportValidity:()=>valid,addEventListener:(event,fn)=>{if(event==='submit')submit=fn}};
 const context={document:{body:{dataset:{bookingPlan:plan}},documentElement:{lang:'en'},querySelector:s=>s==='#consult-form'?form:s==='#date-note'?note:status,addEventListener(){}},window:{location:{assign:url=>handoffs.push(url)}},FormData:class{constructor(){return Object.entries(fields).map(([k,f])=>[k,f.value]);}},Intl,Date,URLSearchParams,encodeURIComponent};
 vm.runInNewContext(readFileSync('public/consultation.js','utf8'),context);
 return {submit:()=>submit({preventDefault(){}}),handoffs,fields};
}
for(const [plan,fee,duration] of [['audio',999,'10–15'],['expert',1100,'20–25'],['30',2100,'30'],['60',4200,'60']]){
 test(`${plan}: correct WhatsApp destination, fee and format; no external request`,()=>{const s=setup(plan);s.submit();assert.equal(s.handoffs.length,1);const url=new URL(s.handoffs[0]);assert.equal(url.origin+url.pathname,'https://wa.me/919045432034');const msg=url.searchParams.get('text');assert.ok(msg.includes(`Displayed fee: ₹${fee}`));assert.ok(msg.includes(duration));assert.ok(msg.includes('Test question & follow-up?'));if(plan==='audio')assert.ok(msg.includes('not a live call'));});
}
test('invalid form never opens WhatsApp',()=>{const s=setup('expert',false);s.submit();assert.equal(s.handoffs.length,0);});
test('dates earlier than the allowed booking date never open WhatsApp',()=>{const s=setup('expert');s.fields.sessionDate.value='2001-01-01';s.submit();assert.equal(s.handoffs.length,0);});
