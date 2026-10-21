import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const mapping=JSON.parse(readFileSync('public/numerology-videos.json','utf8'));
function setup(search='', saved='applied'){
 const nodes=new Map();
 const node=(text='')=>({textContent:text,hidden:false,src:'',value:'',children:[],dataset:{},events:{},attributes:{},append(...n){this.children.push(...n)},after(){},insertBefore(){},replaceChildren(...n){this.children=n},setAttribute(k,v){this.attributes[k]=v},addEventListener(k,v){this.events[k]=v},scrollIntoView(){},focus(){},querySelector(){return node();}});
 const get=id=>{if(!nodes.has(id))nodes.set(id,node());return nodes.get(id)};
 const titles=Array.from({length:24},(_,i)=>node('Class '+(i+1)));
 let player;const loads=[];
 const context={document:{documentElement:{lang:'en'},head:node(),getElementById:get,querySelector:get,querySelectorAll:()=>titles,createElement:()=>node()},location:{origin:'https://example.test',search},sessionStorage:{getItem:()=>saved,setItem(){}},encodeURIComponent,URLSearchParams};
 context.YT={Player:class{constructor(id,options){this.events=options.events;player=this;}cueVideoById(o){this.current=o.videoId;loads.push(o.videoId)}loadVideoById(o){this.current=o.videoId;loads.push(o.videoId)}getVideoData(){return {video_id:this.current}}}};context.window={YT:context.YT};
 vm.runInNewContext(readFileSync('public/numerology-coupon.js','utf8'),context);if(player)player.events.onReady({target:player});
 return {titles,loads,player,nodes};
}
test('class 1 starts its exact video, not the first playlist item',()=>{const s=setup();assert.equal(s.loads[0],'2I2SFqUP1Ig');assert.notEqual(s.loads[0],'-19A4HhgKn0')});
test('every class button loads its matching direct video ID',()=>{const s=setup();assert.equal(new Set(mapping.map(v=>v.videoId)).size,24);for(let i=0;i<24;i++){s.titles[i].children[0].events.click();assert.equal(s.loads.at(-1),mapping[i].videoId);assert.equal(s.titles[i].children[0].attributes['aria-pressed'],'true')}});
test('completion advances in syllabus order and stops after class 24',()=>{const s=setup();for(let i=0;i<23;i++){s.player.events.onStateChange({target:s.player,data:0});assert.equal(s.loads.at(-1),mapping[i+1].videoId)}const n=s.loads.length;s.player.events.onStateChange({target:s.player,data:0});assert.equal(s.loads.length,n)});
test('mapping matches uploaded titles, with documented health numbering correction',()=>{for(let i=0;i<24;i++){assert.equal(mapping[i].class,i+1);if(i===17)assert.match(mapping[i].title,/Health/);else assert.match(mapping[i].title,new RegExp('^Class '+(i+1)+':'));}});

test('published coupon in a link unlocks without prior saved access',()=>{const s=setup('?coupon=NUMEROPRO',null);assert.equal(s.loads[0],'2I2SFqUP1Ig');assert.equal(s.nodes.get('[data-coupon-total]').textContent,'₹0');});
test('unknown coupon in a link does not unlock any lesson',()=>{const s=setup('?coupon=INVALID',null);assert.equal(s.loads.length,0);s.titles[0].children[0].events.click();assert.equal(s.loads.length,0);});
