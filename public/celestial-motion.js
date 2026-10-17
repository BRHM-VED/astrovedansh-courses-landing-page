(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const en = document.documentElement.lang === 'en';
  const sections = [...document.querySelectorAll('.hero, #free-numerology, #masterclasses, #about')];
  if (!sections.length) return;
  const ns = 'http://www.w3.org/2000/svg';
  function svgElement(name, attrs) { const el = document.createElementNS(ns, name); Object.entries(attrs).forEach(([k,v]) => el.setAttribute(k, v)); return el; }
  sections.forEach((section, index) => {
    section.classList.add('av-motion-section');
    const layer = document.createElement('div'); layer.className = 'av-celestial-layer'; layer.setAttribute('aria-hidden','true');
    const ring = svgElement('svg', {viewBox:'0 0 300 300',class:'av-zodiac-wheel'});
    [108,132,146].forEach(r => ring.append(svgElement('circle',{cx:150,cy:150,r,fill:'none',stroke:'currentColor','stroke-width':1})));
    Array.from('♈♉♊♋♌♍♎♏♐♑♒♓').forEach((sign,i) => {
      const angle = i * Math.PI / 6;
      const text = svgElement('text',{x:150+120*Math.sin(angle),y:157-120*Math.cos(angle),'text-anchor':'middle','font-size':18,fill:'currentColor'});text.textContent=sign;ring.append(text);
      const a=angle+Math.PI/12;ring.append(svgElement('line',{x1:150+108*Math.sin(a),y1:150-108*Math.cos(a),x2:150+146*Math.sin(a),y2:150-146*Math.cos(a),stroke:'currentColor','stroke-width':1}));
    }); layer.append(ring);
    const chart=svgElement('svg',{viewBox:'0 0 160 160',class:'av-floating-chart'});
    chart.append(svgElement('path',{d:'M8 8H152V152H8Z M8 8L152 152 M152 8L8 152 M80 8L152 80L80 152L8 80Z',fill:'none',stroke:'currentColor','stroke-width':1.5}));layer.append(chart);
    ['☉','♄','☽',...(section.id==='free-numerology'?['3','7','9']:['♃','✧','♀'])].forEach((symbol,i)=>{
      const node=document.createElement('span');node.className='av-floating-symbol av-symbol-'+i;node.textContent=symbol;node.style.setProperty('--delay',`${-i*2-index}s`);layer.append(node);
    });section.prepend(layer);
  });
  let paused=false;try{paused=localStorage.getItem('av-motion-paused')==='yes';}catch{}
  const toggle=document.createElement('button');toggle.type='button';toggle.className='av-motion-toggle';sections[0].append(toggle);
  function update(){const stop=paused||reduced.matches;document.documentElement.classList.toggle('av-motion-paused',stop);toggle.textContent=stop?(en?'▶ Resume animation':'▶ गति चालू करें'):(en?'Ⅱ Pause animation':'Ⅱ गति रोकें');toggle.setAttribute('aria-pressed',String(stop));toggle.hidden=reduced.matches;}
  toggle.addEventListener('click',()=>{paused=!paused;try{localStorage.setItem('av-motion-paused',paused?'yes':'no');}catch{}update();});reduced.addEventListener('change',update);update();
  const observer='IntersectionObserver' in window?new IntersectionObserver(entries=>entries.forEach(e=>e.target.classList.toggle('av-motion-visible',e.isIntersecting)),{rootMargin:'80px'}):null;
  sections.forEach(s=>observer?observer.observe(s):s.classList.add('av-motion-visible'));
  document.addEventListener('visibilitychange',()=>document.documentElement.classList.toggle('av-tab-hidden',document.hidden));
})();
