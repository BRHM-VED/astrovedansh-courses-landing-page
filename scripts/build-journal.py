from site_promotion import promotion
"""Build original study content and crawlable, bilingual journal pages."""
from pathlib import Path
import json, html, re
from collections import Counter
from xml.etree.ElementTree import Element, SubElement, ElementTree
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'public'; esc=html.escape
# Published long-form lessons and their dates are authoritative. The legacy
# short-page generator must not silently replace them on a routine rebuild.
import subprocess, sys
saved_batches = sorted((ROOT/'content/journal-batches').glob('*.json'))
if saved_batches:
 for batch in saved_batches:
  subprocess.run([sys.executable, str(ROOT/'scripts/build-journal-lessons.py'), '--date', batch.stem], check=True)
 subprocess.run([sys.executable, str(ROOT/'scripts/build-newsletter-feed.py')], check=True)
 print('Retained existing journal; reapplied saved long-form batches and newsletter feed.')
 sys.exit(0)
ORIGIN='https://courses.astrovedansh.org'; DATE='2026-10-17'; rows=[]; category=''
categories=['अध्ययन की शुरुआत','कुंडली की भाषा','ग्रहों का अध्ययन','भाव और जीवन क्षेत्र','राशियाँ और संबंध','दशा और समय','योग और वर्ग कुंडलियाँ','अभ्यास और शोध','जिम्मेदार संवाद','आगे की सीख और काम','अंकज्योतिष सीखें']
category_en=['Getting started','Reading a kundli','Studying planets','Houses and life topics','Signs and relationships','Dashas and timing','Yogas and divisional charts','Practice and research','Responsible consultations','Further study and work','Learn numerology']
for line in (ROOT/'content/journal-topics.txt').read_text().splitlines():
 if not line:continue
 if '|' not in line:category=line;continue
 title,lead,method,exercise,caution=line.split('|');rows.append(dict(category=category,title=title,paragraphs=[lead,method,exercise,caution]))
rows.sort(key=lambda r:categories.index(r['category']))
insights={int(x.split('|')[0]):x.split('|')[1:] for x in (ROOT/'content/journal-insights.txt').read_text().splitlines()}
for i,r in enumerate(rows,1):
 title,slug,example=insights[i];r.update(number=i,title=title,slug=slug,url=f'journal/lesson-{i:03}.html',lang='hi');r['paragraphs'].insert(2,example)
 # Put the specific question and example before general process advice.
 r['paragraphs']=[r['paragraphs'][2],r['paragraphs'][0],r['paragraphs'][1],r['paragraphs'][3],r['paragraphs'][4]]
english=[]
for line in (ROOT/'content/journal-english.txt').read_text().splitlines():
 a=line.split('|');i=int(a[0]);original=rows[i-1];r=dict(number=i,title=a[1],category=a[2],paragraphs=a[3:],slug=original['slug'],url=f'en/journal/{original["slug"]}.html',lang='en',alternate=original['url']);original['alternate']=r['url'];english.append(r)
research=json.loads((ROOT/'content/numerology-research.json').read_text());expansions={int(x.split('|')[0]):x.split('|')[1:] for x in (ROOT/'content/numerology-expansions.txt').read_text().splitlines()}
for data in research:
 for j,lang in enumerate(['hi','en']):
  a=data[lang];url=('' if lang=='hi' else 'en/')+'journal/'+data['slug']+'.html';alternate=('en/' if lang=='hi' else '')+'journal/'+data['slug']+'.html'
  r=dict(number=100+data['id'],title=a['title'],category=categories[-1],slug=data['slug'],url=url,lang=lang,alternate=alternate,paragraphs=[a['brief'],a['example'],expansions[data['id']][j],a['misconception']])
  (rows if lang=='hi' else english).append(r)
allrows=rows+english
assets={'ancient-study':('पुरानी पांडुलिपि और पीतल के खगोलीय उपकरणों का कल्पनात्मक चित्र','An editorial illustration of manuscripts and brass astronomy instruments'),'planetary-study':('ग्रहों और पीतल के खगोलीय यंत्र का कल्पनात्मक चित्र','An editorial illustration of planets and a brass astronomical instrument'),'learning-practice':('धूप में रखी अध्ययन पुस्तकों और नोटबुक का कल्पनात्मक चित्र','An editorial illustration of study books and a notebook in sunlight'),'numerology-study':('अंकज्योतिष अभ्यास की खाली सारणी और पीतल की पट्टियों का कल्पनात्मक चित्र','An editorial illustration of a blank numerology practice grid and brass tiles')}
for r in allrows:
 r['words']=len(' '.join(r['paragraphs']).split());assert 150<=r['words']<=200,(r['number'],r['lang'],r['words'])
 r['image']='numerology-study' if r['number']>100 or r['number']==96 else 'planetary-study' if 21<=r['number']<=70 else 'learning-practice' if r['number']>=71 else 'ancient-study'
 r['description']=r['paragraphs'][0]
 if len(r['description'])>165:r['description']=r['description'][:162].rsplit(' ',1)[0]+'…'
assert len(set(r['url'] for r in allrows))==len(allrows)
assert len(set(' '.join(r['paragraphs']) for r in allrows))==len(allrows)

def labels(lang):
 return dict(home='मुख्य पृष्ठ',journal='अध्ययन पत्रिका',courses='पाठ्यक्रम देखें',read='लेख पढ़ें',all='सभी लेख',words='शब्द',related='आगे यह पढ़ें',author='AstroVedansh अध्ययन पत्रिका',updated='अपडेट: 17 अक्टूबर 2026',illustration='विषय-आधारित कल्पनात्मक चित्र',editorial='हमारी संपादकीय प्रक्रिया',byline='वेदांश वल्लभ के संस्थान से',cta='समझ को अभ्यास में बदलें।',ctacopy='क्रमबद्ध कक्षाओं और उदाहरणों के साथ अगला कदम लें।') if lang=='hi' else dict(home='Home',journal='Journal',courses='Explore courses',read='Read article',all='All articles',words='words',related='Read next',author='AstroVedansh Journal',updated='Updated: 17 October 2026',illustration='Conceptual editorial illustration',editorial='Our editorial approach',byline='From the institute founded by Vedansh Vallabh',cta='Turn understanding into practice.',ctacopy='Take the next step with structured lessons and worked examples.')
def cat(r):return r['category'] if r['lang']=='hi' else category_en[categories.index(r['category'])]
def absurl(path):return ORIGIN+'/'+path

def page(title,desc,body,url,lang='hi',alternate=None,image='ancient-study',schema=None,script=False):
 depth=len(Path(url).parts)-1;prefix='../'*depth;l=labels(lang);index='journal.html' if lang=='hi' else 'journal-english.html';home='index.html' if lang=='hi' else 'english.html';other='en' if lang=='hi' else 'hi';img=f'assets/journal/{image}.webp'
 head=f'<link rel="canonical" href="{absurl(url)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta property="og:type" content="{ "article" if schema else "website"}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{absurl(url)}"><meta property="og:image" content="{absurl(img)}"><meta property="og:locale" content="{ "hi_IN" if lang=="hi" else "en_IN"}"><meta name="twitter:card" content="summary_large_image">'
 if alternate:head+=f'<link rel="alternate" hreflang="{lang}" href="{absurl(url)}"><link rel="alternate" hreflang="{other}" href="{absurl(alternate)}">'
 if schema:head+='<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script>'
 switch=f'<a class="j-language" lang="{other}" hreflang="{other}" href="{prefix}{alternate}">{"English" if other=="en" else "हिन्दी"}</a>' if alternate else ''
 return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#631ca0"><title>{esc(title)} | AstroVedansh®</title><meta name="description" content="{esc(desc)}">{head}<link rel="icon" href="{prefix}assets/astrovedansh-logo.webp"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700;800&family=Mulish:wght@400;500;600;700;800&display=swap" rel="stylesheet"><link rel="stylesheet" href="{prefix}journal.css"><link rel="stylesheet" href="{prefix}promotion.css"></head><body><a class="journal-skip" href="#main">{'मुख्य सामग्री पर जाएँ' if lang=='hi' else 'Skip to content'}</a><header class="j-header"><div class="j-container"><a class="j-brand" href="{prefix}{home}"><img src="{prefix}assets/astrovedansh-logo.webp" width="44" height="44" alt=""><span>Astro<strong>Vedansh</strong><sup>®</sup></span></a><nav aria-label="{'मुख्य मार्ग' if lang=='hi' else 'Main navigation'}">{switch}<a href="{prefix}{index}">{l['journal']}</a><a href="{prefix}{home}#courses">{l['courses']} ↗</a></nav></div></header>{body}{promotion(prefix,lang)}<footer class="j-footer"><div class="j-container"><strong>{l['author']}</strong><p>{'परम्परा को समझें। प्रश्न पूछें। अभ्यास से आगे बढ़ें।' if lang=='hi' else 'Understand the tradition. Ask better questions. Practise thoughtfully.'}</p><a href="{prefix}{home}#about">{l['byline']} →</a><p><a href="{prefix}{'editorial.html' if lang=='hi' else 'editorial-english.html'}">{l['editorial']}</a></p></div></footer>{'<script src="journal.js" defer></script>' if script else ''}</body></html>'''

def card(r,prefix=''):
 l=labels(r['lang']);return f'''<article class="j-card" data-category="{esc(cat(r))}" data-search="{esc(r['title']+' '+cat(r)+' '+r['slug'].replace('-',' ')+' '+r['paragraphs'][0])}"><a href="{prefix}{r['url']}" tabindex="-1" aria-hidden="true"><img class="j-card-cover" src="{prefix}assets/journal/{r['image']}.webp" width="1536" height="1024" loading="lazy" decoding="async" alt=""></a><div class="j-card-body"><span class="j-tag">{esc(cat(r))}</span><h2><a href="{prefix}{r['url']}">{esc(r['title'])}</a></h2><p>{esc(r['description'])}</p><div class="j-card-bottom"><span>{r['words']} {l['words']}</span><a href="{prefix}{r['url']}" aria-label="{esc(r['title'])}">{l['read']} →</a></div></div></article>'''

for r in allrows:
 lang=r['lang'];l=labels(lang);prefix='../'*(len(Path(r['url']).parts)-1);index='journal.html' if lang=='hi' else 'journal-english.html';home='index.html' if lang=='hi' else 'english.html';num=r['number'];same=rows if lang=='hi' else english
 related=[x for x in same if x['category']==r['category'] and x['number']!=num][:3]
 if len(related)<3:related += [x for x in same if x['number']!=num and x not in related][:3-len(related)]
 image_url=absurl(f'assets/journal/{r["image"]}.webp')
 schema={'@context':'https://schema.org','@graph':[{'@type':'BlogPosting','@id':absurl(r['url'])+'#article','headline':r['title'],'description':r['description'],'mainEntityOfPage':absurl(r['url']),'image':[image_url],'author':{'@type':'Organization','name':'AstroVedansh','url':absurl(home)+'#about'},'publisher':{'@type':'Organization','name':'AstroVedansh','url':ORIGIN,'logo':{'@type':'ImageObject','url':absurl('assets/astrovedansh-logo.webp')}},'datePublished':DATE,'dateModified':DATE,'inLanguage':lang,'wordCount':r['words'],'articleSection':cat(r)},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':l['home'],'item':absurl(home)},{'@type':'ListItem','position':2,'name':l['journal'],'item':absurl(index)},{'@type':'ListItem','position':3,'name':r['title'],'item':absurl(r['url'])}]}]}
 blocks=''.join('<p>'+esc(p)+'</p>' for p in r['paragraphs'])
 related_html=''.join(f'<a href="{prefix}{x["url"]}">{esc(x["title"])} →</a>' for x in related)
 course='numerology.html' if num>100 or num==96 else 'index.html#courses'
 if lang=='en':course=course.replace('numerology.html','numerology-english.html').replace('index.html','english.html')
 body=f'''<main id="main" class="j-reader"><nav class="j-breadcrumb" aria-label="{'आप यहाँ हैं' if lang=='hi' else 'Breadcrumb'}"><a href="{prefix}{home}">{l['home']}</a><span>/</span><a href="{prefix}{index}">{l['journal']}</a></nav><header class="j-article-header"><a class="j-tag" href="{prefix}{index}?category={esc(cat(r))}">{esc(cat(r))}</a><h1>{esc(r['title'])}</h1><p class="j-meta"><a href="{prefix}{home}#about">{l['author']}</a><span>·</span>{r['words']} {l['words']}</p><p class="j-meta">{l['updated']}</p></header><figure class="j-article-cover"><img src="{prefix}assets/journal/{r['image']}.webp" width="1536" height="1024" fetchpriority="high" alt="{assets[r['image']][0 if lang=='hi' else 1]}"><figcaption>{l['illustration']}</figcaption></figure><article class="j-prose" aria-label="{'लेख' if lang=='hi' else 'Article'}">{blocks}</article><aside class="j-author"><img src="{prefix}assets/astrovedansh-logo.webp" width="48" height="48" alt=""><div><strong>{l['author']}</strong><p>{l['byline']}</p><a href="{prefix}{'editorial.html' if lang=='hi' else 'editorial-english.html'}">{l['editorial']} →</a></div></aside><aside class="j-reader-cta"><h2>{l['cta']}</h2><p>{l['ctacopy']}</p><a href="{prefix}{course}">{l['courses']} →</a></aside><section class="j-related"><h2>{l['related']}</h2><nav aria-label="{l['related']}">{related_html}</nav></section><a class="j-back" href="{prefix}{index}">{l['all']} →</a></main>'''
 target=P/r['url'];target.parent.mkdir(parents=True,exist_ok=True);target.write_text(page(r['title'],r['description'],body,r['url'],lang,r.get('alternate'),r['image'],schema))

for lang,collection,index,alternate in [('hi',rows,'journal.html','journal-english.html'),('en',english,'journal-english.html','journal.html')]:
 l=labels(lang);hi=lang=='hi';cats=list(dict.fromkeys(cat(r) for r in collection));options=f'<option value="">{"सभी विषय" if hi else "All topics"}</option>'+''.join(f'<option>{esc(c)}</option>' for c in cats)
 title='ज्योतिष और अंकज्योतिष सीखें: उदाहरण सहित लेख' if hi else 'Learn Vedic astrology and numerology with worked examples'
 body=f'''<main id="main"><section class="j-hero"><div class="j-container"><span class="j-eyebrow">{l['author']}</span><h1>{'AstroVedansh के लेखों से<br><em>ज्योतिष सीखें।</em>' if hi else 'Learn astrology through<br><em>articles by AstroVedansh.</em>'}</h1><p>{'ज्योतिष कैसे सीखें, कुंडली कैसे पढ़ें और मूलांक कैसे निकालें—ऐसे सवालों पर सीधे जवाब, छोटे उदाहरण और छूट जाने वाली बारीकियाँ।' if hi else 'How to read a kundli, calculate a birth number and separate a rule from an assumption. Clear answers, worked examples and details worth questioning.'}</p><div class="j-pills"><span>{'AstroVedansh की अध्ययन पत्रिका' if hi else 'The AstroVedansh journal'}</span><span>{'हिन्दी में पढ़ें' if hi else 'Read in English'}</span><span>{'ज्योतिष + अंकज्योतिष' if hi else 'Astrology + numerology'}</span></div></div></section><section class="j-container j-library" aria-label="{l['all']}"><form class="j-controls" role="search"><div><label for="journal-search">{'क्या सीखना चाहते हैं?' if hi else 'What would you like to learn?'}</label><input id="journal-search" type="search" placeholder="{'जैसे: लग्न, मूलांक, दशा…' if hi else 'Try: ascendant, birth number, dasha…'}" autocomplete="off"></div><div><label for="journal-category">{'विषय चुनें' if hi else 'Choose a topic'}</label><select id="journal-category">{options}</select></div><button type="reset">{'सभी दिखाएँ' if hi else 'Show all'}</button></form><div class="j-results-heading"><h2>{'आपकी अध्ययन सूची' if hi else 'Your reading list'}</h2><p id="journal-status" role="status" aria-live="polite">{len(collection)} {'लेख उपलब्ध' if hi else 'articles available'}</p></div><div class="j-grid" id="journal-grid">{''.join(card(r) for r in collection)}</div><p id="journal-empty" hidden>{'इस खोज से कोई लेख नहीं मिला। दूसरा शब्द या विषय चुनें।' if hi else 'No articles match this search. Try another word or topic.'}</p><nav class="j-pagination" aria-label="{'लेख सूची के पृष्ठ' if hi else 'Article list pages'}" hidden><button id="journal-prev" type="button">{'← पिछला' if hi else '← Previous'}</button><span id="journal-page"></span><button id="journal-next" type="button">{'अगला →' if hi else 'Next →'}</button></nav><noscript><p>{'सभी लेख नीचे उपलब्ध हैं।' if hi else 'All articles are available below.'}</p></noscript></section></main>'''
 (P/index).write_text(page(title,title,body,index,lang,alternate,script=True))

for lang in ['hi','en']:
 hi=lang=='hi';url='editorial.html' if hi else 'editorial-english.html';alternate='editorial-english.html' if hi else 'editorial.html';title='हमारी संपादकीय प्रक्रिया' if hi else 'Our editorial approach'
 paras=['यह AstroVedansh की अध्ययन पत्रिका है। संस्थान के संस्थापक वेदांश वल्लभ हैं। लेखों का उद्देश्य ज्योतिष और अंकज्योतिष की पारंपरिक विधियों को स्पष्ट उदाहरणों और जिम्मेदार भाषा में समझाना है।','हमारा उद्देश्य है कि आप हर नियम का कारण समझें और उसे कुंडली पर लागू करना सीखें। लेखों के शिक्षण उदाहरण इसी अभ्यास में आपकी मदद करते हैं।','अंकगणित के परिणाम और परंपरागत व्याख्याएँ अलग हैं। गणना जाँची जा सकती है; इससे भविष्यवाणी की वैज्ञानिक पुष्टि नहीं होती। लेख चिकित्सा, कानूनी या व्यक्तिगत निवेश सलाह का विकल्प नहीं हैं।','लेखों में विषय को समझने में मदद करने वाले चित्र और उदाहरण दिए गए हैं।','किसी त्रुटि की सूचना या सुझाव vedanshvallabh@gmail.com पर भेज सकते हैं। सुधार होने पर संबंधित लेख में संशोधन तारीख अद्यतन की जाएगी।'] if hi else ['This is the AstroVedansh study journal, published by the institute founded by Vedansh Vallabh. It explains traditional astrology and numerology methods through clear examples and responsible language.','Our aim is to help you understand the reasoning behind each rule and learn to apply it to a chart. The teaching examples in our articles help you practise these steps.','Arithmetic and traditional interpretation are distinct. A sum can be checked, but this does not scientifically establish predictive claims. Articles do not replace medical, legal or personal investment advice.','Illustrations and examples help make the topics easier to understand.','Send corrections or suggestions to vedanshvallabh@gmail.com. Material corrections will be reflected in the affected article’s modification date.']
 body=f'<main id="main" class="j-reader"><h1>{title}</h1><article class="j-prose">'+''.join('<p>'+esc(p)+'</p>' for p in paras)+'</article><h2>'+('अध्ययन संदर्भ' if hi else 'Study references')+'</h2><p><a href="https://www.icasindia.org/ICAS/JyotishPraveena.html">ICAS · Jyotisha Praveena</a> · <a href="https://www.astrosage.com/magazine/learn/astrology-tutorial-houses.asp">AstroSage · Chart and house conventions</a></p><p>'+('ये संदर्भ विषय और परंपरागत शब्दावली के लिए हैं; किसी संस्था की साझेदारी या समर्थन का दावा नहीं।' if hi else 'These references support educational context and terminology, not a claim of institutional partnership or endorsement.')+'</p></main>'
 (P/url).write_text(page(title,title,body,url,lang,alternate))

paths=['courses.html','courses-english.html','reports.html','consultation.html','gemstone.html','app.html','services.html','services-english.html','free-tools.html','free-tools-english.html','index.html','english.html','numerology.html','numerology-english.html','journal.html','journal-english.html','editorial.html','editorial-english.html']+[r['url'] for r in allrows]
ns='http://www.sitemaps.org/schemas/sitemap/0.9';root=Element('urlset',xmlns=ns)
for path in paths:
 u=SubElement(root,'url');SubElement(u,'loc').text=absurl(path)
 if path not in ['index.html','english.html','numerology.html','numerology-english.html']:SubElement(u,'lastmod').text=DATE
ElementTree(root).write(P/'sitemap.xml',encoding='utf-8',xml_declaration=True)
(P/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /account\n\nSitemap: '+ORIGIN+'/sitemap.xml\n')
(ROOT/'content/journal-manifest.json').write_text(json.dumps([{k:r[k] for k in ['number','title','category','url','lang','words','image']} for r in allrows],ensure_ascii=False,indent=2)+'\n')
print(f'Built {len(rows)} Hindi and {len(english)} English articles; all 150–200 words. Sitemap: {len(paths)} URLs.')
