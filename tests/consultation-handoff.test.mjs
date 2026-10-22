import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
class Element {
 constructor(tag='div'){this.tag=tag;this.children=[];this.hidden=false;this.disabled=false;this.handlers={};this.label={hidden:false};}
 append(...children){this.children.push(...children);}
 replaceChildren(...children){this.children=children;}
 addEventListener(name,fn){this.handlers[name]=fn;}
 closest(){return this.label;}
 focus(){}
 querySelector(tag){return this.children.find(x=>x.tag===tag) || this.children.map(x=>x.querySelector?.(tag)).find(Boolean);}
}
function setup(plan, valid=true){
 const values={plan,name:' QA Test ',gender:'Other',birthDate:'2000-01-01',birthTime:'12:00',birthPlace:' Test City ',phone:'+910000000000',email:'',question:' Test question & follow-up? ',sessionDate:'2099-01-01',preferredTime:'2–5 PM IST',preferredName:' Test Name '};
 const fields=Object.fromEntries(Object.entries(values).map(([k,value])=>[k,Object.assign(new Element('input'),{value})]));
 const nodes=Object.fromEntries(['#consult-form','#booking','.booking-summary','#booking-error','#plan-upgrade','#date-note','#availability-label','#selected-plan-note','#status'].map(k=>[k,new Element()]));
 const form=nodes['#consult-form'],button=new Element('button'),handoffs=[],events=[];
 form.elements=fields;form.reportValidity=()=>valid;form.querySelector=()=>button;
 const docEvents={};
 const context={document:{body:{dataset:{bookingPlan:plan}},documentElement:{lang:'en'},querySelector:s=>nodes[s],createElement:tag=>new Element(tag),addEventListener:(type,fn)=>docEvents[type]=fn,dispatchEvent:event=>events.push(event)},window:{location:{assign:url=>handoffs.push(url)},addEventListener(){}},location:{search:''},FormData:class{constructor(){return Object.entries(fields).filter(([,f])=>!f.disabled).map(([k,f])=>[k,f.value]);}},Intl,Date,URLSearchParams,encodeURIComponent,CustomEvent:class{constructor(type,init){this.type=type;this.detail=init.detail}}};
 const ctx=vm.createContext(context);
 for(const file of ['booking-catalog.js','booking-model.js','consultation.js'])vm.runInContext(readFileSync('public/'+file,'utf8'),ctx);
 return {submit:()=>form.handlers.submit({preventDefault(){}}),handoffs,fields,nodes,events,ctx,button};
}
const expected={astrology_report:[299,['astrology_report']],name:[399,['name']],audio:[799,['audio']],expert:[999,['expert']],personal:[1799,['personal']],detailed:[3199,['detailed']],report_combo:[499,['astrology_report','name']],audio_combo:[899,['audio','astrology_report']],personal_combo:[1999,['personal','astrology_report','name']],complete_combo:[3499,['detailed','astrology_report','name']]};
for(const [plan,[fee,items]] of Object.entries(expected)){
 test(`${plan}: correct single package fee and fulfilment items; no external request`,()=>{
  const s=setup(plan);s.submit();s.submit();assert.equal(s.handoffs.length,1);
  const url=new URL(s.handoffs[0]);assert.equal(url.origin+url.pathname,'https://wa.me/919045432034');
  const msg=url.searchParams.get('text');assert.ok(msg.includes(`Package fee: ₹${fee}`));assert.ok(msg.includes(`Plan ID: ${plan}`));assert.ok(msg.includes('Test question & follow-up?'));
  for(const id of items)assert.equal(msg.split(`[${id}] × 1`).length-1,1);
  if(items.length>1)assert.ok(msg.includes('do not bill these items separately'));
  if(plan.startsWith('audio'))assert.ok(msg.includes('not a live call'));
  if(plan==='name'){assert.ok(!msg.includes('Time of birth:'));assert.ok(!msg.includes('Preferred session date'));}
  assert.ok(!JSON.stringify(s.events).includes('Test City'));assert.ok(!JSON.stringify(s.events).includes('qa@example'));
 });
}
test('original service remains selected until an upgrade is actively chosen; form details survive undo',()=>{
 const s=setup('personal');assert.equal(s.fields.plan.value,'personal');
 s.nodes['#plan-upgrade'].querySelector('button').handlers.click();
 assert.equal(s.fields.plan.value,'personal_combo');assert.equal(s.fields.name.value,' QA Test ');
 s.nodes['.booking-summary'].children.find(x=>x.className==='back-to-original').handlers.click();
 assert.equal(s.fields.plan.value,'personal');s.submit();assert.ok(new URL(s.handoffs[0]).searchParams.get('text').includes('Package fee: ₹1799'));
});
test('selected audio combo sends both items and keeps recorded format',()=>{const s=setup('audio');s.nodes['#plan-upgrade'].querySelector('button').handlers.click();s.submit();const text=new URL(s.handoffs[0]).searchParams.get('text');assert.ok(text.includes('₹899'));assert.ok(text.includes('[astrology_report] × 1'));assert.ok(text.includes('not a live call'));});
test('invalid form never opens WhatsApp',()=>{const s=setup('expert',false);s.submit();assert.equal(s.handoffs.length,0);});
test('early booking date never opens WhatsApp',()=>{const s=setup('expert');s.fields.sessionDate.value='2001-01-01';s.submit();assert.equal(s.handoffs.length,0);});
test('future birth date never opens WhatsApp',()=>{const s=setup('name');s.fields.birthDate.value='2099-01-01';s.submit();assert.equal(s.handoffs.length,0);});
test('unknown plan fails closed without a booking form',()=>{const s=setup('made_up');assert.equal(s.nodes['#booking'].hidden,true);assert.equal(s.nodes['#booking-error'].hidden,false);assert.equal(s.handoffs.length,0);});
test('existing 30 and 60 minute route aliases preserve the right new price',()=>{for(const [id,price] of [['30',1799],['60',3199]]){const s=setup(id);s.submit();assert.ok(new URL(s.handoffs[0]).searchParams.get('text').includes(`Package fee: ₹${price}`));}});
test('report-only plans do not ask for consultation availability; live plans do',()=>{const r=setup('report_combo');assert.equal(r.fields.sessionDate.disabled,true);assert.equal(r.fields.birthTime.required,true);const n=setup('name');assert.equal(n.fields.birthTime.disabled,true);const l=setup('complete_combo');assert.equal(l.fields.sessionDate.required,true);assert.equal(l.fields.preferredName.disabled,false);});
