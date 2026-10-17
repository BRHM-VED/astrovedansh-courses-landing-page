import {moonSign,vedicSunSign} from './moon-sign.js';
export const gridOrder=[3,1,9,6,7,5,2,8,4];
export function reduceNumber(value){let n=Number(value);while(n>9)n=String(n).split('').reduce((a,b)=>a+Number(b),0);return n;}
export function parseBirthDate(value,today=new Date()){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(value))throw Error('date');
 const [y,m,d]=value.split('-').map(Number),date=new Date(y,m-1,d);
 if(y<1900||date.getFullYear()!==y||date.getMonth()!==m-1||date.getDate()!==d||date>today)throw Error('date');return {y,m,d,date};
}
export function calculate(value,today=new Date()){
 const {y,m,d,date}=parseBirthDate(value,today),year=String(y),full=`${String(d).padStart(2,'0')}${String(m).padStart(2,'0')}${year}`;
 const raw=`${String(d).padStart(2,'0')}${String(m).padStart(2,'0')}${year.startsWith('19')?year.slice(2):year}`.replaceAll('0','');
 const counts=Object.fromEntries(gridOrder.map(n=>[n,[...raw].filter(v=>Number(v)===n).length]));
 let age=today.getFullYear()-y;if(today.getMonth()<m-1||(today.getMonth()===m-1&&today.getDate()<d))age--;
 return {mulank:reduceNumber(d),bhagyank:reduceNumber([...full].reduce((a,b)=>a+Number(b),0)),counts,raw,full,day:d,age,date};
}
if(typeof document!=='undefined'){
 const en=document.documentElement.lang==='en',L=(hi,eng)=>en?eng:hi,form=document.querySelector('#birth-form'),input=document.querySelector('#birth-date'),error=document.querySelector('#tool-error');
 const now=new Date();input.max=`${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
 const put=(id,text)=>document.getElementById(id).textContent=text;
 const traits=[null,['सूर्य','Sun','पहल और आत्मनिर्भरता','initiative and independence'],['चंद्र','Moon','संवेदनशीलता और सहयोग','sensitivity and cooperation'],['गुरु','Jupiter','सीखना और मार्गदर्शन','learning and guidance'],['राहु','Rahu','अलग दृष्टिकोण और प्रयोग','unconventional thinking and experimentation'],['बुध','Mercury','संवाद और अनुकूलन','communication and adaptability'],['शुक्र','Venus','सौंदर्य और संबंध','aesthetics and relationships'],['केतु','Ketu','चिंतन और खोज','reflection and inquiry'],['शनि','Saturn','अनुशासन और धैर्य','discipline and patience'],['मंगल','Mars','ऊर्जा और कार्यशीलता','energy and action']];
 function chain(digits){let n=digits.reduce((a,b)=>a+b,0),s=digits.join(' + ')+' = '+n;while(n>9){const arr=String(n).split('').map(Number);n=arr.reduce((a,b)=>a+b,0);s+=' → '+arr.join(' + ')+' = '+n;}return s;}
 form.addEventListener('submit',event=>{event.preventDefault();error.textContent='';try{
 const r=calculate(input.value);put('mulank-value',r.mulank);put('bhagyank-value',r.bhagyank);put('mulank-math',chain(String(r.day).split('').map(Number)));put('bhagyank-math',chain(r.full.split('').map(Number)));put('age-value',r.age+' '+L('वर्ष','years'));
 const t=traits[r.mulank];put('short-reading',L(`परंपरागत अंकज्योतिष में मूलांक ${r.mulank} का संबंध ${t[0]} और ${t[2]} से जोड़ा जाता है। भाग्यांक ${r.bhagyank} पूरी जन्मतिथि का संक्षिप्त अंक है। इन दोनों को साथ पढ़ना सीखें; केवल एक अंक से किसी घटना या व्यक्ति का निश्चित निर्णय नहीं निकलता।`,`Traditional numerology connects birth number ${r.mulank} with ${t[1]}, ${t[3]}. Your full-date number is ${r.bhagyank}. Study these numbers together; one number does not establish a fixed personality or predict an event.`));
 const grid=document.querySelector('#birth-grid');grid.replaceChildren();gridOrder.forEach(n=>{const cell=document.createElement('div'),label=document.createElement('small'),value=document.createElement('strong');label.textContent=L('स्थान ','Cell ')+n;value.textContent=r.counts[n]?String(n).repeat(r.counts[n]):'—';cell.append(label,value);cell.setAttribute('aria-label',`${n}: ${r.counts[n]}`);grid.append(cell);});
 put('grid-digits',L('सारणी में लिए अंक: ','Digits used in the grid: ')+r.raw.split('').join(', '));put('grid-summary',L('दोहराए गए अंक: ','Repeated digits: ')+gridOrder.filter(n=>r.counts[n]>1).map(n=>`${n} (${r.counts[n]})`).join(', '));
 const time=document.querySelector('#birth-time').value;
 try{const sun=vedicSunSign(input.value,time,document.querySelector('#birth-offset').value);put('sun-value',sun.changing?sun.sign[en?1:0]+' / '+sun.endSign[en?1:0]:sun.sign[en?1:0]);put('sun-note',sun.changing?L('इस तारीख को सूर्य राशि बदलता है। सही राशि के लिए जन्म का समय भरें।','The Sun changes sign on this date. Enter birth time to resolve the sign.'):sun.boundary?L('सूर्य राशि की सीमा के पास है। सही जन्म-समय भरें और पूरी कुंडली से पुष्टि करें।','The Sun is near a sign boundary. Use the exact birth time and confirm with a full chart.'):sun.timed?L('जन्म-समय की सूर्य स्थिति से लाहिड़ी अयनांश का अनुमान घटाकर निकाली गई निरयन राशि।','Sidereal Sun sign calculated from the birth-time solar position with an approximate Lahiri offset.'):L('चुने हुए समय-क्षेत्र में इस पूरे दिन सूर्य इसी राशि में है।','The Sun remains in this sidereal sign throughout the selected local date.'));}catch{put('sun-value',L('गणना उपलब्ध नहीं','Calculation unavailable'));put('sun-note',L('जन्म का समय और UTC अंतर जाँचें या पेज दोबारा खोलें।','Check birth time and UTC offset, or reload the page.'));}

 put('moon-value',L('समय भरें','Enter birth time'));put('moon-note',L('चंद्र राशि देखने के लिए जन्म का समय और सही UTC अंतर भरें।','Enter birth time and the correct UTC offset to see your Moon sign.'));
 if(time){try{const moon=moonSign(input.value,time,document.querySelector('#birth-offset').value);put('moon-value',moon.sign[en?1:0]);put('moon-note',moon.boundary?L('चंद्रमा राशि की सीमा के बहुत पास है। समय और अयनांश में छोटे अंतर से राशि बदल सकती है; पूरी कुंडली से पुष्टि करें।','The Moon is very close to a sign boundary. Small time or ayanamsha differences can change the sign; confirm with a full chart.'):L('आपके दिए जन्म-समय और UTC अंतर के अनुसार अनुमानित निरयन चंद्र राशि।','Approximate sidereal Moon sign for your entered birth time and UTC offset.'));}catch{put('moon-value',L('गणना उपलब्ध नहीं','Calculation unavailable'));put('moon-note',L('समय और UTC अंतर जाँचें। यदि सही हैं तो पेज दोबारा खोलें।','Check the birth time and UTC offset. If correct, reload the page.'));}}
 document.querySelector('#tool-results').hidden=false;put('tool-status',L('आपकी गणना नीचे तैयार है।','Your results are ready below.'));document.querySelector('#results-title').focus();
 }catch{error.textContent=L('कृपया 1900 से आज तक की सही जन्मतिथि चुनें।','Choose a valid birth date between 1900 and today.');document.querySelector('#tool-results').hidden=true;}});
 form.addEventListener('reset',()=>{document.querySelector('#tool-results').hidden=true;error.textContent='';put('tool-status','');input.focus();});
 document.querySelector('#demo-date').addEventListener('click',()=>{input.value='1996-09-23';form.requestSubmit();});
 document.querySelector('#copy-results').addEventListener('click',async()=>{try{const r=calculate(input.value);await navigator.clipboard.writeText(`AstroVedansh\n${L('मूलांक','Birth number')}: ${r.mulank}\n${L('भाग्यांक','Full-date number')}: ${r.bhagyank}\n${gridOrder.map(n=>String(n).repeat(r.counts[n])||'—').reduce((a,n,i)=>a+n+(i%3===2?'\n':' | '),'')}`);put('copy-status',L('परिणाम कॉपी हो गया।','Results copied.'));}catch{put('copy-status',L('कॉपी नहीं हो सका। परिणाम चुनकर कॉपी करें।','Could not copy. Select the results and copy them manually.'));}});
}
