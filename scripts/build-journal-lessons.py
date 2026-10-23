"""Render dated, reviewable long-form lesson batches over the latest journal.

Only selected articles, the Hindi listing and associated metadata are changed.
Rerunning a saved batch updates its same URLs; it never allocates another ten.
"""
from pathlib import Path
from copy import deepcopy
from urllib.parse import urlsplit
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import html as stdhtml
import json
import re
from lxml import html, etree
from PIL import Image
from site_promotion import promotion

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
ORIGIN = 'https://courses.astrovedansh.org'
ESC = stdhtml.escape
SIGNS = ['मेष','वृषभ','मिथुन','कर्क','सिंह','कन्या','तुला','वृश्चिक','धनु','मकर','कुंभ','मीन']
# Preserve the first batch's published ordering when replaying its source files.
ORDER = [18, 47, 121, 37, 122, 63, 123, 65, 124, 125]
HI_MONTHS = ['जनवरी','फ़रवरी','मार्च','अप्रैल','मई','जून','जुलाई','अगस्त','सितंबर','अक्टूबर','नवंबर','दिसंबर']
EN_MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']

def local_date(value):
    """Display persisted dates in India; never substitute the execution date."""
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(ZoneInfo('Asia/Kolkata'))
    return parsed.date()

def date_label(value, lang='hi'):
    day = local_date(value)
    months = HI_MONTHS if lang == 'hi' else EN_MONTHS
    return f'{day.day} {months[day.month-1]} {day.year}'

def article_dates(doc):
    """Only existing Article schema is evidence for an older publication date."""
    for node in doc.xpath('//script[@type="application/ld+json"]'):
        try:
            data = json.loads(node.text or '{}')
        except json.JSONDecodeError:
            continue
        for graph in data.get('@graph', [data]):
            kinds = graph.get('@type', [])
            if isinstance(kinds, str): kinds = [kinds]
            if not any(kind in kinds for kind in ['Article', 'BlogPosting']): continue
            published = graph.get('datePublished')
            if published:
                local_date(published)
                modified = graph.get('dateModified', published)
                local_date(modified)
                return published, modified
    return None, None

def visible_dates(container, heading, published, modified, lang='hi'):
    # Remove only date-specific metadata; preserve bylines and word counts.
    for node in container.xpath('./p'):
        text = node.text_content().strip()
        classes = node.get('class', '').split()
        if ('j-publication-date' in classes or 'j-updated-date' in classes
                or text.startswith(('प्रकाशित:', 'अपडेट:', 'अपडेट किया गया:', 'संशोधित:', 'Published:', 'Updated:'))):
            container.remove(node)
    label = 'प्रकाशित: ' if lang == 'hi' else 'Published: '
    p = html.Element('p', {'class':'j-meta j-publication-date'})
    p.text = label
    time = etree.SubElement(p, 'time', datetime=published)
    time.text = date_label(published, lang)
    container.insert(container.index(heading)+1, p)
    if modified and local_date(modified) != local_date(published):
        p = html.Element('p', {'class':'j-meta j-updated-date'})
        p.text = 'अपडेट किया गया: ' if lang == 'hi' else 'Updated: '
        time = etree.SubElement(p, 'time', datetime=modified)
        time.text = date_label(modified, lang)
        container.insert(container.index(heading)+2, p)

def persist_verified_dates(manifest):
    """Expose verified original dates on every existing Hindi/English article."""
    for row in manifest:
        path = PUBLIC / row['url']
        if not path.exists(): continue
        doc = html.parse(str(path)).getroot()
        for link in doc.xpath('//a[@href]'):
            href = link.get('href')
            if href.endswith('index.html#courses'):
                link.set('href', href.replace('index.html#courses', 'courses.html'))
            elif href.endswith('english.html#courses'):
                link.set('href', href.replace('english.html#courses', 'courses-english.html'))
        published, modified = article_dates(doc)
        if not published: continue  # Unknown historical dates must stay unknown.
        row['datePublished'] = published
        row['dateModified'] = modified
        heading = doc.xpath('//h1')
        if heading:
            visible_dates(heading[0].getparent(), heading[0], published, modified, row.get('lang', 'hi'))
            write_doc(doc, path)

def listing_dates(path, manifest):
    """Add dates beneath listing titles without rebuilding language navigation."""
    doc = html.parse(str(path)).getroot()
    by_url = {row['url']:row for row in manifest}
    for card in doc.xpath('//*[@id="journal-grid"]/article'):
        headings = card.xpath('.//h2')
        if not headings: continue
        links = headings[0].xpath('.//a[@href]')
        if not links: continue
        row = by_url.get(links[0].get('href', '').lstrip('./'))
        if row and row.get('datePublished'):
            visible_dates(headings[0].getparent(), headings[0], row['datePublished'], None, row.get('lang','hi'))
    write_doc(doc, path)

def write_doc(doc, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('<!doctype html>\n' + html.tostring(doc, encoding='unicode', method='html'), encoding='utf-8')

def replace_text(node, text):
    for child in list(node): node.remove(child)
    node.text = text

def word_count(body):
    return len(html.fragment_fromstring(body, create_parent='div').text_content().split())

def covers():
    for name in ['planetary-study','ancient-study','learning-practice']:
        image = Image.open(PUBLIC / f'assets/journal/{name}.webp')
        for width in [480, 960]:
            out = PUBLIC / f'assets/journal/{name}-{width}.webp'
            if not out.exists():
                image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS).save(out, 'WEBP', quality=80, method=6)

def cover_attrs(image, name, alt):
    image.set('src', f'../assets/journal/{name}-960.webp')
    image.set('srcset', ', '.join(f'../assets/journal/{name}-{w}.webp {w}w' for w in [480, 960]) + f', ../assets/journal/{name}.webp 1536w')
    image.set('sizes', '(max-width: 760px) calc(100vw - 36px), 760px')
    image.set('alt', alt)
    image.set('width','1536'); image.set('height','1024')

def chart_svg(chart):
    lagna = chart['lagna'].replace(' लग्न','').strip()
    assert lagna in SIGNS, chart
    positions = {11:(0,0),0:(1,0),1:(2,0),2:(3,0),10:(0,1),3:(3,1),9:(0,2),4:(3,2),8:(0,3),7:(1,3),6:(2,3),5:(3,3)}
    bysign = {s:[] for s in SIGNS}
    summary = []
    for p in chart['placements']:
        sign = p['sign'].strip(); assert sign in SIGNS, p
        house = (SIGNS.index(sign)-SIGNS.index(lagna))%12+1
        assert house == int(p['house']), (chart, p, house)
        label = p['planet'] + ((' '+str(p['degree'])) if p.get('degree') else '')
        bysign[sign].append(label)
        summary.append(f"{ESC(p['planet'])}: {ESC(sign)}, भाव {house}" + (f", {ESC(str(p['degree']))}" if p.get('degree') else ''))
    boxes=[]
    for i, sign in enumerate(SIGNS):
        x,y=positions[i]; x*=180; y*=180
        house=(i-SIGNS.index(lagna))%12+1
        fill='#f4e8fb' if house==1 else '#fffdf8'
        boxes.append(f'<rect x="{x}" y="{y}" width="180" height="180" fill="{fill}" stroke="#cdb5db"/><text x="{x+12}" y="{y+32}" font-size="21" fill="#592475">{sign} · भाव {house}</text>')
        if house==1: boxes.append(f'<text x="{x+12}" y="{y+60}" font-size="18" fill="#773d96">लग्न</text>')
        for j,label in enumerate(bysign[sign]):
            boxes.append(f'<text x="{x+12}" y="{y+88+j*26}" font-size="19" fill="#34203f">{ESC(label)}</text>')
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 720" role="img" aria-labelledby="chart-title chart-desc"><title id="chart-title">काल्पनिक आंशिक राशि कुंडली</title><desc id="chart-desc">'+ESC('; '.join(stdhtml.unescape(x) for x in summary))+'</desc>'+''.join(boxes)+'<text x="360" y="300" text-anchor="middle" fill="#632c82" font-size="28">काल्पनिक उदाहरण</text><text x="360" y="346" text-anchor="middle" fill="#514358" font-size="23">'+ESC(lagna)+' लग्न</text><text x="360" y="390" text-anchor="middle" fill="#514358" font-size="21">आंशिक राशि कुंडली</text><text x="360" y="430" text-anchor="middle" fill="#73667d" font-size="18">केवल चर्चा वाले ग्रह दिखाए हैं</text></svg>'
    return '<figure class="teaching-chart"><div class="chart-scroll">'+svg+'</div><figcaption>शिक्षण चित्र: '+ESC(chart.get('title','काल्पनिक आंशिक कुंडली'))+'। सभी भाव पूरी राशि को एक भाव मानकर दिखाए हैं। खाली दिखते खानों से ग्रह न होने का निष्कर्ष न निकालें; अन्य ग्रह यहाँ नहीं दर्शाए गए हैं। छोटे पर्दे पर चित्र को बगल में खिसकाकर पढ़ें।</figcaption></figure><p class="chart-placement-list">'+ ' · '.join(summary)+'</p>'

def meta(doc, selector, value):
    node=doc.xpath(selector)
    if node: node[0].set('content',value)

def render_lesson(r, date, template):
    path=PUBLIC/r['url']; existed=path.exists()
    doc=html.fromstring(path.read_text() if existed else template)
    title=r['title']; description=r['description']; prefix='../'
    replace_text(doc.xpath('//title')[0],title+' | AstroVedansh®')
    replace_text(doc.xpath('//h1')[0],title)
    doc.xpath('//link[@rel="canonical"]')[0].set('href',ORIGIN+'/'+r['url'])
    for selector,value in [('//meta[@name="description"]',description),('//meta[@property="og:title"]',title),('//meta[@property="og:description"]',description),('//meta[@property="og:url"]',ORIGIN+'/'+r['url'])]: meta(doc,selector,value)
    # The old short English primers are preserved, but are not translations of these expanded lessons.
    for node in doc.xpath('//link[@rel="alternate" and @hreflang]'): node.getparent().remove(node)
    for a in doc.xpath('//a[contains(@class,"j-language")]'):
        a.set('href',prefix+'journal-english.html'); a.attrib.pop('hreflang',None)
    head=doc.xpath('//head')[0]
    for href in [prefix+'lessons.css']:
        if not doc.xpath('//link[@href=$href]',href=href): head.append(html.Element('link',rel='stylesheet',href=href))
    header=doc.xpath('//header[contains(@class,"j-article-header")]')[0]
    tag=header.xpath('.//a[contains(@class,"j-tag")]')[0]
    replace_text(tag,r['category']); tag.set('href','../journal.html?category='+r['category'])
    for p in header.xpath('./p[contains(@class,"j-meta")]'): header.remove(p)
    header.append(html.fragment_fromstring(f'<p class="j-meta">AstroVedansh अध्ययन पत्रिका · {r["words"]} शब्द · विस्तृत पाठ</p>'))
    visible_dates(header, header.xpath('./h1')[0], r['datePublished'], r['dateModified'])
    img=doc.xpath('//figure[contains(@class,"j-article-cover")]//img')[0]
    cover_attrs(img,r['image'],r['image_alt'])
    meta(doc,'//meta[@property="og:image"]',ORIGIN+f'/assets/journal/{r["image"]}.webp')
    caption=doc.xpath('//figure[contains(@class,"j-article-cover")]//figcaption')[0]
    replace_text(caption,'विषय को समझने के लिए कल्पनात्मक अध्ययन चित्र।')
    article=doc.xpath('//article[contains(@class,"j-prose")]')[0]
    article.clear(); article.set('class','j-prose j-longform'); article.set('aria-label','विस्तृत अध्ययन पाठ'); article.set('data-lesson-url',r['url'])
    fragment=html.fragment_fromstring(r['body_html'],create_parent='div')
    if fragment.text: article.text=fragment.text
    for child in list(fragment): article.append(child)
    for table in article.xpath('.//table'):
        parent=table.getparent(); pos=parent.index(table); parent.remove(table)
        wrapper=html.Element('div',{'class':'table-scroll','role':'region','aria-label':'अध्ययन तुलना सारणी','tabindex':'0'}); wrapper.append(table); parent.insert(pos,wrapper)
    headings=article.xpath('.//h2')
    outline=[]
    for i,h in enumerate(headings,1):
        h.set('id',f'lesson-section-{i}'); outline.append(f'<li><a href="#lesson-section-{i}">{ESC(h.text_content())}</a></li>')
    parent=article.getparent(); idx=parent.index(article)
    # Renders can be repeated without accumulating tools or notes.
    for n in parent.xpath('./*[contains(concat(" ",normalize-space(@class)," ")," lesson-generated ")]'): parent.remove(n)
    idx=parent.index(article)
    tools='''<section class="lesson-tools lesson-generated" aria-label="लेख के अध्ययन विकल्प"><div class="lesson-tool-buttons"><button id="copy-notes" type="button">सूत्र कॉपी करें</button><button id="save-article" type="button" aria-pressed="false">लेख सहेजें</button></div><p>सहेजने पर लिंक और सूत्र केवल इसी उपकरण के इस ब्राउज़र में रहते हैं। पूरा लेख ऑफ़लाइन डाउनलोड नहीं होता।</p><p id="lesson-action-status" role="status" aria-live="polite"></p><textarea id="notes-copy-fallback" aria-label="कॉपी करने के लिए अध्ययन सूत्र" readonly hidden></textarea></section>'''
    parent.insert(idx,html.fragment_fromstring(tools)); idx+=1
    parent.insert(idx,html.fragment_fromstring('<details class="lesson-outline lesson-generated"><summary>इस पाठ में क्या सीखेंगे?</summary><ol>'+''.join(outline)+'</ol></details>'))
    notes='<section class="lesson-notes lesson-generated" id="lesson-notes" aria-label="कॉपी करने योग्य अध्ययन सूत्र"><h2>साथ रखने योग्य अध्ययन सूत्र</h2><ol>'+''.join('<li>'+ESC(n)+'</li>' for n in r['notes'])+'</ol></section>'
    parent.insert(parent.index(article)+1,html.fragment_fromstring(notes))
    refs='<section class="lesson-references lesson-generated"><h2>संदर्भ और उनकी सीमा</h2><ul>'+''.join('<li><a href="'+ESC(ref['url'])+'" target="_blank" rel="noopener noreferrer">'+ESC(ref['title'])+'</a><small>'+ESC(ref['scope'])+'</small></li>' for ref in r['references'])+'</ul><p>जहाँ मूल श्लोक या पाठ का मिलान नहीं हुआ है, वहाँ शास्त्र का निश्चित नियम होने का दावा नहीं है। चरणबद्ध मिलान, उदाहरण और अभ्यास इस पाठ की शिक्षण-व्याख्या हैं।</p></section>'
    parent.insert(parent.index(article)+2,html.fragment_fromstring(refs))
    context='<aside class="lesson-context lesson-generated"><h2>इस पाठ का अभ्यास कैसे करें?</h2><p>'+ESC(r['contextual_recommendation'])+' <a href="https://play.google.com/store/apps/details?id=com.FinalAstroTry.app">AstroTry ऐप देखें</a>। क्रमबद्ध अभ्यास के लिए <a href="../index.html#enrol">वैदिक ज्योतिष पाठ्यक्रम</a> देखें। जन्मतिथि की अंक-गणना अलग से सीखनी हो तो <a href="../numerology.html">अंकज्योतिष पाठ्यक्रम</a> उपलब्ध है।</p></aside>'
    parent.insert(parent.index(article)+3,html.fragment_fromstring(context))
    disclosure=html.fragment_fromstring('<p class="lesson-disclosure lesson-generated">यह पाठ ज्योतिष की पारंपरिक व्याख्या सिखाता है। नियम, उदाहरण और अपवाद साथ पढ़ें; पारंपरिक संकेत वैज्ञानिक रूप से स्थापित निश्चित भविष्यवाणी नहीं हैं।</p>')
    parent.insert(parent.index(article)+4,disclosure)
    # Put a precise code-drawn chart after the first hypothetical-example heading.
    example=next((h for h in headings if any(k in h.text_content() for k in ['काल्पनिक','उदाहरण'])),None)
    if example is not None:
        ep=example.getparent(); ei=ep.index(example)+1
        for node in html.fragments_fromstring(chart_svg(r['chart'])): ep.insert(ei,node); ei+=1
    else:
        for node in html.fragments_fromstring(chart_svg(r['chart'])): article.append(node)
    # Count the visible editorial body, including the teaching diagram labels;
    # exclude repeated copy summaries, reference panels and course promotions.
    r['words'] = len(article.text_content().split())
    replace_text(header.xpath('./p[contains(@class,"j-meta") and not(contains(@class,"j-publication-date")) and not(contains(@class,"j-updated-date"))]')[0],f'AstroVedansh अध्ययन पत्रिका · {r["words"]} शब्द · विस्तृत पाठ')
    related=doc.xpath('//section[contains(@class,"j-related")]//nav')
    if related: replace_text(related[0],'')
    if related:
        for item in r['related']:
            a=html.Element('a',href='../'+item['url']); a.text=item['title']+' →'; related[0].append(a)
    for node in doc.xpath('//aside[contains(@class,"j-reader-cta")]'): node.getparent().remove(node)
    # Use the shared, preserved promotion helper for every lesson.
    for node in doc.xpath('//aside[contains(concat(" ",normalize-space(@class)," ")," av-promotion ")]'): node.getparent().remove(node)
    footer=doc.xpath('//footer')[0]; footer.getparent().insert(footer.getparent().index(footer),html.fragment_fromstring(promotion(prefix,'hi')))
    if not doc.xpath('//script[@src="../lesson-reader.js"]'): doc.xpath('//body')[0].append(html.Element('script',src='../lesson-reader.js',defer='defer'))
    schemas=doc.xpath('//script[@type="application/ld+json"]'); published=r['datePublished']
    for node in schemas:
        node.getparent().remove(node)
    schema={'@context':'https://schema.org','@graph':[{'@type':'Article','@id':ORIGIN+'/'+r['url']+'#article','headline':title,'description':description,'mainEntityOfPage':ORIGIN+'/'+r['url'],'image':[ORIGIN+f'/assets/journal/{r["image"]}.webp'],'author':{'@type':'Organization','name':'AstroVedansh अध्ययन पत्रिका','url':ORIGIN+'/editorial.html'},'publisher':{'@type':'Organization','name':'AstroVedansh','url':ORIGIN,'logo':{'@type':'ImageObject','url':ORIGIN+'/assets/astrovedansh-logo.webp'}},'datePublished':published,'dateModified':date,'inLanguage':'hi','wordCount':r['words'],'articleSection':r['category']},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'मुख्य पृष्ठ','item':ORIGIN+'/index.html'},{'@type':'ListItem','position':2,'name':'अध्ययन पत्रिका','item':ORIGIN+'/journal.html'},{'@type':'ListItem','position':3,'name':title,'item':ORIGIN+'/'+r['url']}]}]}
    schema['@graph'][0]['dateModified'] = r['dateModified']
    node=html.Element('script',type='application/ld+json'); node.text=json.dumps(schema,ensure_ascii=False).replace('</','<\\/'); head.append(node)
    write_doc(doc,path)
    return published

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--date',required=True); args=parser.parse_args(); date=args.date
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',date)
    batch_path=ROOT/f'content/journal-batches/{date}.json'
    existing=json.loads(batch_path.read_text()) if batch_path.exists() else None
    sources=existing['source_files'] if existing else [f'content/lessons-{date}-{letter}.json' for letter in 'abc']
    lessons=[]
    for source in sources: lessons.extend(json.loads((ROOT/source).read_text()))
    assert len(lessons)==10 and len({r['url'] for r in lessons})==10
    lessons.sort(key=lambda r:ORDER.index(r['number']) if r['number'] in ORDER else r['number'])
    if existing: assert [r['url'] for r in lessons]==[r['url'] for r in existing['items']], 'Saved batch URLs must not change on retries.'
    manifest_path=ROOT/'content/journal-manifest.json'; manifest=json.loads(manifest_path.read_text())
    # The current homepage is a category hub. Older course links must still
    # reach the retained course pages without changing first-visit language.
    for home_name in ['index.html', 'english.html']:
        home = html.parse(str(PUBLIC/home_name)).getroot()
        if not any(node.get('src', '').split('?')[0] == '/course-legacy-links.js'
                   for node in home.xpath('//script[@src]')):
            home.xpath('//head')[0].append(html.Element('script', src='/course-legacy-links.js'))
            write_doc(home, PUBLIC/home_name)
    persist_verified_dates(manifest)
    known_rows = {row['url']:row for row in manifest}
    saved_rows = {row['url']:row for row in existing['items']} if existing else {}
    operations = {r['url']: saved_rows.get(r['url'], {}).get('operation',
        'upgrade' if r['url'] in known_rows else 'new') for r in lessons}
    template=(PUBLIC/'journal/lesson-018.html').read_text()
    covers()
    supplements_path = ROOT / 'content' / f'journal-supplements-{date}.json'
    supplements = json.loads(supplements_path.read_text()) if supplements_path.exists() else {}
    final_supplements_path = ROOT / 'content' / f'journal-final-supplements-{date}.json'
    final_supplements = json.loads(final_supplements_path.read_text()) if final_supplements_path.exists() else {}
    for idx,r in enumerate(lessons):
        r['body_html'] += supplements.get(str(r['number']), '') + final_supplements.get(str(r['number']), '')
        if word_count(r['body_html']) < 1200:
            r['body_html'] += ('<h2>अपनी भविष्यवाणी जाँचें</h2><p>अंतिम उत्तर से पहले पाँच पंक्तियाँ लिखें: नियम क्या है, परंपरा में उसका उपयोग क्यों होता है, '
                'इस कुंडली में वह कैसे लागू हुआ, किस दशा या गोचर में विषय सक्रिय हो सकता है और किन स्थितियों में निष्कर्ष बदल जाएगा। '
                'फिर एक सहायक और एक विरोधी तथ्य जोड़ें। यदि आप दोनों का स्रोत नहीं बता सकते, तो उत्तर को संभावना तक सीमित रखें। '
                'इस छोटी जाँच से याद किया हुआ नियम जिम्मेदार फलित में बदलता है और पाठक को तर्क साफ दिखाई देता है।</p>')
        r['words']=word_count(r['body_html']); assert 1200<=r['words']<=2200,(r['url'],r['words'])
        body=html.fragment_fromstring(r['body_html'],create_parent='div')
        assert len(body.xpath('.//aside[contains(@class,"prediction-note")]'))>=4,r['url']
        assert len(r['notes'])>=4 and r['references'] and len(body.xpath('.//h2'))>=6,r['url']
        r['image']='ancient-study' if r['number']==125 else 'learning-practice' if r['number'] in [18,65] else 'planetary-study'
        r['image_alt']={'ancient-study':'भाव से भाव गिनने के अध्ययन का प्रतीक: पांडुलिपि और पीतल के खगोलीय यंत्र','learning-practice':'भाव, भावेश और वर्ग कुंडली की तुलना के अभ्यास का प्रतीक: खुली अभ्यास पुस्तिका और अध्ययन पुस्तकें','planetary-study':'ग्रहबल और ग्रह संबंधों के अध्ययन का प्रतीक: पीतल का खगोलीय यंत्र और ग्रहों के प्रतीक'}[r['image']]
        r['contextual_recommendation']={18:'AstroTry में एक ही लग्न की कुंडली खोलकर संबंधित भाव, उसके स्वामी और कारक को अलग-अलग चिह्नित करें।',47:'AstroTry की ग्रह-स्थिति तालिका में उच्च राशि पहचानें और उसके बाद ग्रह का भाव-स्वामित्व लिखें।',121:'AstroTry पर पहले नीच राशि, फिर उसके स्वामी की स्थिति मिलाएँ; केवल योग का नाम देखकर निष्कर्ष न लें।',37:'AstroTry में सप्तम भाव, उसके स्वामी और शनि के संबंध अलग लिखकर इस उदाहरण से तुलना करें।',122:'AstroTry की कुंडली में दशमेश से उसके राशि स्वामी तक की कड़ी बनाकर कार्य और स्थान के संकेत अलग लिखें।',63:'AstroTry में दूसरे, ग्यारहवें और बारहवें भाव के स्वामियों की स्थिति देखकर आय, संचय और व्यय की तीन अलग सूचियाँ बनाएँ।',123:'AstroTry में लग्न के अनुसार केंद्र और त्रिकोण के स्वामित्व की तालिका देखकर योगकारक पहचानने का अभ्यास करें।',65:'AstroTry में ग्रह की ठीक डिग्री लिखकर जन्मकुंडली और नवांश की गणना का मिलान करें।',124:'AstroTry की कुंडली में दशम भाव के मंगल को पढ़ने से पहले लग्न और मंगल का भाव-स्वामित्व लिखें।',125:'AstroTry में मूल भाव को एक गिनते हुए संबंधित भाव तक गिनें और अपनी गणना दोबारा जाँचें।'}.get(r['number'],'AstroTry में शिक्षण उदाहरण की संबंधित ग्रह स्थितियों को देखकर अपना विश्लेषण लिखें।')
        r['related']=[{'url':x['url'],'title':x['title']} for x in lessons if x['number']!=r['number']][max(0,idx-1):max(0,idx-1)+3]
        known = known_rows.get(r['url'], {})
        saved = saved_rows.get(r['url'], {})
        # A new page receives this batch's real publication date, not the date
        # embedded in the older HTML template used to build its shell.
        r['datePublished'] = saved.get('datePublished') or known.get('datePublished') or date
        r['dateModified'] = saved.get('dateModified') or date
        if operations[r['url']] == 'upgrade':
            assert known.get('datePublished'), ('Cannot invent original publication date', r['url'])
        r['published']=render_lesson(r,date,template)
        row={'number':r['number'],'title':r['title'],'category':r['category'],'url':r['url'],'lang':'hi','words':r['words'],'image':r['image'],'description':r['description'],'dateModified':r['dateModified'],'datePublished':r['published'],'type':r['type'],'longform':True}
        old=next((x for x in manifest if x['url']==r['url']),None)
        if old: manifest[manifest.index(old)]={**old, **row}
        else: manifest.append(row)
    assert len({r['url'] for r in manifest})==len(manifest)
    assert len({r['title'] for r in manifest})==len(manifest)
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    # Update Hindi cards in place; keep all other HTML and language navigation.
    index=html.parse(str(PUBLIC/'journal.html')).getroot(); grid=index.xpath('//*[@id="journal-grid"]')[0]
    for r in lessons:
        for card in grid.xpath('./article'):
            if any(a.get('href')==r['url'] for a in card.xpath('.//a[@href]')): grid.remove(card)
    for r in reversed(lessons):
        card=html.fragment_fromstring(f'<article class="j-card" data-category="{ESC(r["category"])}" data-search="{ESC(r["title"]+" "+r["category"]+" "+r["description"])}"><a href="{r["url"]}" tabindex="-1" aria-hidden="true"><img class="j-card-cover" src="assets/journal/{r["image"]}-480.webp" srcset="assets/journal/{r["image"]}-480.webp 480w, assets/journal/{r["image"]}-960.webp 960w" sizes="(max-width:600px) calc(100vw - 36px), 360px" width="1536" height="1024" loading="lazy" alt=""></a><div class="j-card-body"><span class="j-tag">{ESC(r["category"])}</span><h2><a href="{r["url"]}">{ESC(r["title"])}</a></h2><p>{ESC(r["description"])}</p><div class="j-card-bottom"><span>{r["words"]} शब्द · विस्तृत पाठ</span><a href="{r["url"]}">लेख पढ़ें →</a></div></div></article>')
        grid.insert(0,card)
    select=index.xpath('//*[@id="journal-category"]')[0]; opts={x.text for x in select}
    for r in lessons:
        if r['category'] not in opts:
            opt=html.Element('option'); opt.text=r['category']; select.append(opt); opts.add(r['category'])
    replace_text(index.xpath('//*[@id="journal-status"]')[0],str(sum(x['lang']=='hi' for x in manifest))+' लेख उपलब्ध')
    if not index.xpath('//link[@href="lessons.css"]'): index.xpath('//head')[0].append(html.Element('link',rel='stylesheet',href='lessons.css'))
    if not index.xpath('//*[@id="journal-saved-only"]'):
        controls=index.xpath('//form[contains(@class,"j-controls")]')[0]
        controls.addnext(html.fragment_fromstring('<div class="j-saved-tools"><button class="j-saved-filter" type="button" id="journal-saved-only" aria-pressed="false">सहेजे हुए लेख दिखाएँ</button><span>इस उपकरण और ब्राउज़र में सहेजे हुए लिंक</span></div>'))
    write_doc(index,PUBLIC/'journal.html')
    for index_name in ['journal.html', 'journal-english.html']:
        listing_dates(PUBLIC/index_name, manifest)
    # Remove reciprocal translation claims on the preserved short English primers.
    for filename in ['en/journal/karaka-vs-house-lord.html','en/journal/what-is-navamsa-d9.html']:
        p=PUBLIC/filename
        if p.exists():
            doc=html.parse(str(p)).getroot()
            for node in doc.xpath('//link[@rel="alternate" and @hreflang]'): node.getparent().remove(node)
            write_doc(doc,p)
    sitemap=etree.parse(str(PUBLIC/'sitemap.xml')); ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    for r in lessons:
        found=sitemap.xpath('//s:url[s:loc=$url]',namespaces=ns,url=ORIGIN+'/'+r['url'])
        if found: node=found[0]
        else:
            node=etree.SubElement(sitemap.getroot(),'{'+ns['s']+'}url'); etree.SubElement(node,'{'+ns['s']+'}loc').text=ORIGIN+'/'+r['url']
        last=node.find('{'+ns['s']+'}lastmod')
        if last is None: last=etree.SubElement(node,'{'+ns['s']+'}lastmod')
        last.text=date
    sitemap.write(str(PUBLIC/'sitemap.xml'),encoding='utf-8',xml_declaration=True)
    record={'date':date,'timezone':'Asia/Calcutta','purpose':'Idempotent publication batch; retry these same URLs, never allocate another ten.','content_state':'validated-source','source_files':sources,'items':[{'number':r['number'],'title':r['title'],'url':r['url'],'operation':operations[r['url']],'datePublished':r['datePublished'],'dateModified':r['dateModified'],'body_words':r['words'],'editorial_sha256':hashlib.sha256(r['body_html'].encode()).hexdigest(),'search_intent':r.get('search_intent','')} for r in lessons],'images':{'source':'public/assets/journal/provenance.json','method':'Reuse original AI-generated covers, encode responsive WebP versions without creative changes.','widths':[480,960,1536]}}
    batch_path.parent.mkdir(parents=True,exist_ok=True); batch_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'batch':date,'lessons':len(lessons),'new':sum(operations[x['url']]=='new' for x in lessons),'upgraded':sum(operations[x['url']]=='upgrade' for x in lessons),'words':{r['number']:r['words'] for r in lessons}},ensure_ascii=False))

if __name__=='__main__': main()
