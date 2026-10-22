"""Generate static prices and offer markup; never changes an external checkout."""
import json,re,sys
from pathlib import Path
from html import escape
from pricing_components import booking_data, overview, pricing_page, chooser, bi as plan_bi
ROOT=Path(__file__).resolve().parents[1]
catalog=json.loads((ROOT/'config/catalog.json').read_text())
products=catalog['products'];offers=catalog['offers']
plans=booking_data(catalog)
def money(n):return '₹'+format(n,',')
def bi(tag,en,hi,cls=''):
 return '<'+tag+(f' class="{cls}"' if cls else '')+' data-en="'+escape(en,quote=True)+'" data-hi="'+escape(hi,quote=True)+'">'+escape(hi)+'</'+tag+'>'
def card(key,review=False):
 single=key=='timing';o=products[key] if single else offers[key];n=1 if single else o['questions'];price=o['amount'];active=single or o['enabled']
 regular=n*products['timing']['amount'];saving=regular-price
 if active and not single:
  assert o['businessApproved'] and o['checkoutVerified'] and o['checkoutUrl'] and o['sameBirthChart'] is not None and o['deliveryScope'], 'Offer requires approval, verified checkout and terms'
  assert o['checkoutUrl'].startswith('https://'),'Checkout must use HTTPS'
 if not active and not review:return ''
 out='<article class="timing-pack'+(' best-value' if n==4 else '')+'">'
 if n==4:out+=bi('small','Best Bundle Value · Proposed','बेहतर बंडल वैल्यू · प्रस्तावित')
 out+=bi('h3',f'{n} Question'+('s' if n>1 else ''),f'{n} सवाल')+'<strong class="pack-price">'+money(price)+'</strong>'
 if saving:out+=bi('p',f'Combined value {money(regular)} · Save {money(saving)}',f'कुल कीमत {money(regular)} · {money(saving)} की बचत')
 if n==4:out+=bi('p','Pay for 3. Get the 4th Question Free.','3 सवालों के पैसे दें, चौथा सवाल निःशुल्क पाएँ।')
 out+=bi('p','One selected timing question with personalized written analysis.' if single else f'Analysis for {n} eligible timing questions.', 'एक चुने हुए सवाल का व्यक्तिगत लिखित समय-विश्लेषण।' if single else f'{n} पात्र Timing सवालों का विश्लेषण।')
 if active:
  href=o['url'] if single else o['checkoutUrl'];out+='<a class="pack-cta" data-timing-package="'+key+'" href="'+escape(href,quote=True)+'">'+bi('span',f'Get {n} Question Report →' if single else f'Get {n} Questions Bundle →',f'{n} सवाल की रिपोर्ट लें →')+'</a>'
 else:out+=bi('p','Preview only — not available to purchase. Approval, chart scope and checkout are pending.','सिर्फ समीक्षा के लिए — खरीदारी उपलब्ध नहीं। स्वीकृति, कुंडली की शर्तें और checkout बाकी हैं।','pending-note')+'<button class="pack-cta" disabled>Not active / सक्रिय नहीं</button>'
 return out+'</article>'
def section(review=False):
 return '<section class="hub-section timing-offers" id="timing-offers">'+bi('h2','Waiting for an Important Change?','शादी, नौकरी या प्रमोशन — कब हो सकता है?')+bi('p','Explore potential timing periods through your birth chart and Vimshottari Dasha.','कुंडली और विंशोत्तरी दशा के आधार पर संभावित समय-अवधि समझें।')+'<div class="timing-packs">'+''.join(card(k,review) for k in ['timing','timing_two','timing_four'])+'</div>'+bi('p','Perfect Timing · Digital PDF delivered on WhatsApp. Review the product page for delivery terms.','Perfect Timing · डिजिटल PDF, WhatsApp पर डिलीवरी। पूरी शर्तें प्रोडक्ट पेज पर देखें।','hub-note')+'<a class="sample-link" href="https://perfect-timing.astrovedansh.com/icons/sample.pdf">'+bi('span','View Sample Report →','सैंपल रिपोर्ट देखें →')+'</a></section>'
# Enabling an experiment requires explicit approval and matching booking/checkout conditions.
for key,o in offers.items():
 if o['enabled']:
  assert o['businessApproved'] and o['checkoutVerified'] and o.get('checkoutUrl'),key+' not ready'
  if key=='detailed_pilot':raise ValueError('Connect the approved pilot booking conditions and analytics before activation')
outputs={}
def plan_callout(group):
 en='Not sure which service fits? Choose one step at a time.'
 hi='समझ नहीं आ रहा क्या चुनें? एक-एक कदम में सही विकल्प चुनें।'
 href='/pricing.html?guidance=live' if group=='consultation' else '/pricing.html?guidance=written'
 return '<aside class="category-plan-link">'+plan_bi('p',en,hi)+'<a class="plan-cta secondary" href="'+href+'">'+plan_bi('span','Help Me Choose →','मेरे लिए विकल्प चुनें →')+'</a></aside>'
astrology_card='<a class="visual-card peach" href="/book-guidance.html?plan=astrology_report"><div class="visual-media"><img alt="AstroVedansh report" src="/assets/report-editorial.webp" width="720" height="480" loading="lazy"></div><div class="visual-body">'+plan_bi('h2','Astrology Report','ज्योतिष रिपोर्ट')+plan_bi('p',products['astrology_report']['description']['en'],products['astrology_report']['description']['hi'],'class="card-description"')+'<div class="price-block"><strong>'+money(products['astrology_report']['amount'])+'</strong>'+plan_bi('small','Personalized written analysis','व्यक्तिगत लिखित विश्लेषण')+'</div><div class="visual-cta">'+plan_bi('span','Get Astrology Report','ज्योतिष रिपोर्ट लें')+'<span aria-hidden="true">→</span></div></div></a>'
for template in (ROOT/'templates/pricing').glob('*.html'):
 s=template.read_text();s=re.sub(r'\{\{price:([A-Za-z_]+)\}\}',lambda m:money((products|catalog['bundles'])[m[1]]['amount']),s).replace('{{timing_offers}}',section()).replace('{{guidance_overview}}',overview(plans)).replace('{{guidance_chooser}}',chooser(plans,products)).replace('{{report_plan_callout}}',plan_callout('reports')).replace('{{consultation_plan_callout}}',plan_callout('consultation')).replace('{{astrology_report_card}}',astrology_card)
 assert '{{price:' not in s and '{{timing_offers}}' not in s
 outputs[ROOT/'public'/template.name]=s
source=(ROOT/'templates/pricing/reports.html').read_text()
header=re.search(r'<header.*?</header>',source,re.S)[0]
footer=re.search(r'<footer.*?</footer>',source,re.S)[0]
outputs[ROOT/'public/pricing.html']=pricing_page(header,footer,plans,products)
outputs[ROOT/'public/booking-catalog.js']='/* Generated from config/catalog.json. Do not edit. */\nwindow.AV_BOOKING = '+json.dumps(plans,ensure_ascii=False,separators=(',',':'))+';\n'
review='''<!doctype html><html lang="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>AstroVedansh — Offer review only</title><link rel="stylesheet" href="/offer-cards.css"><style>body{margin:0;padding:20px;background:#faf8f3;color:#542b39;font:16px/1.6 system-ui,sans-serif}main{max-width:950px;margin:auto}button{min-height:44px}h1{font-size:26px}.review-note{padding:16px;border:1px solid #c29a61;border-radius:12px}</style></head><body><main><h1>Offer review / ऑफर समीक्षा</h1><p class="review-note">Staging only. These proposals are NOT active on the homepage or checkout. / प्रस्ताव सक्रिय नहीं हैं।</p><div><button onclick="setLang('hi')">हिन्दी</button> <button onclick="setLang('en')">EN</button></div>'''+section(True)+bi('h2','60-minute consultation pilot','60 मिनट परामर्श का प्रस्तावित परीक्षण')+bi('p',f'Current: {money(products["detailed"]["amount"])} · Proposed: {money(offers["detailed_pilot"]["amount"])}. Not active.',f'मौजूदा: {money(products["detailed"]["amount"])} · प्रस्तावित: {money(offers["detailed_pilot"]["amount"])}। सक्रिय नहीं।')+bi('p','60 minutes live with Vedansh. Multiple questions and follow-ups within the session.','वेदांश जी के साथ 60 मिनट लाइव। सेशन में कई सवाल और फॉलो-अप।')+'''</main><script>function setLang(l){document.documentElement.lang=l;document.querySelectorAll('[data-en][data-hi]').forEach(e=>e.textContent=e.dataset[l]);}</script></body></html>'''
outputs[ROOT/'public/offer-review.html']=review
check='--check' in sys.argv
for path,s in outputs.items():
 if check:assert path.exists() and path.read_text()==s,str(path)+' is stale; run scripts/build-catalog.py'
 else:path.write_text(s)
print(('Checked' if check else 'Generated')+f' {len(outputs)} outputs; approved service combos active, unrelated proposals inactive.')
