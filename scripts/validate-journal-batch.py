"""Publication gate for a dated journal batch and its newsletter feed."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from collections import Counter
import hashlib
import json
import sys
from lxml import html, etree
from PIL import Image

root = Path(__file__).resolve().parents[1]
public = root / 'public'
date = sys.argv[1]
batch = json.loads((root / f'content/journal-batches/{date}.json').read_text())
manifest = json.loads((root / 'content/journal-manifest.json').read_text())
assert len(batch['items']) == 10
for field in ['url', 'title']:
    assert not [k for k,v in Counter(r[field] for r in manifest).items() if v > 1], field
bodies = []
for row in manifest:
    path = public / row['url']
    doc = html.parse(str(path)).getroot()
    graphs = sum([json.loads(n.text).get('@graph',[json.loads(n.text)]) for n in doc.xpath('//script[@type="application/ld+json"]')], [])
    schema = next(n for n in graphs if n.get('@type') in ['Article', 'BlogPosting'])
    assert schema['datePublished'] == row['datePublished'], row['url']
    assert doc.xpath('//h1/following-sibling::*[1]/time[@datetime=$d]',d=row['datePublished']), row['url']
for item in batch['items']:
    path = public / item['url']
    doc = html.parse(str(path)).getroot()
    body = doc.xpath('//article[contains(@class,"j-longform")]')[0]
    words = len(body.text_content().split())
    assert 1200 <= words <= 2200 and words == item['body_words'], (item['url'], words)
    assert len(doc.xpath('//h1')) == 1
    assert doc.xpath('//h1')[0].text_content() == item['title']
    assert doc.xpath('//link[@rel="canonical"]/@href') == ['https://courses.astrovedansh.org/'+item['url']]
    assert len(doc.xpath('//meta[@name="description"]/@content')[0]) > 40
    assert len(body.xpath('.//aside[contains(@class,"prediction-note")]')) >= 4
    assert body.xpath('.//svg') and 'काल्पनिक' in body.text_content()
    assert len(doc.xpath('//*[@id="copy-notes"]')) == 1
    assert len(doc.xpath('//*[@id="save-article"]')) == 1
    assert doc.xpath('//*[@id="lesson-action-status"][@aria-live="polite"]')
    assert doc.xpath('//aside[contains(@class,"av-promotion")]//a[contains(@href,"com.FinalAstroTry.app")]')
    assert doc.xpath('//aside[contains(@class,"av-promotion")]//a[@href="../index.html#enrol"]')
    assert doc.xpath('//aside[contains(@class,"av-promotion")]//a[@href="../numerology.html"]')
    assert not doc.xpath('//link[@hreflang]'), item['url']
    text = doc.text_content()
    for forbidden in ['AI की सहायता', 'व्यक्तिगत रूप से जाँचा', 'AI-generated', 'AI-assisted']:
        assert forbidden not in text, (item['url'], forbidden)
    for element in doc.xpath('//*[@href or @src]'):
        value = element.get('href') or element.get('src')
        if not value or value.startswith(('#', 'mailto:', 'tel:', 'data:')): continue
        u = urlsplit(value)
        if u.scheme or u.netloc: continue
        target = (path.parent / unquote(u.path)).resolve()
        assert target.exists(), (item['url'],value)
        if u.fragment and target.suffix == '.html':
            target_doc = html.parse(str(target)).getroot()
            if target.name in ['index.html','english.html'] and u.fragment in ['enrol','courses','about']:
                assert target_doc.xpath('//script[@src="/course-legacy-links.js"]')
                destination = public / ('courses-english.html' if target.name == 'english.html' else 'courses.html')
                assert html.parse(str(destination)).xpath('//*[@id=$id]', id=u.fragment)
            else:
                assert target_doc.xpath('//*[@id=$id]', id=u.fragment), (item['url'],value)
    image = doc.xpath('//figure[contains(@class,"j-article-cover")]//img')[0]
    assert image.get('alt') and image.get('srcset') and image.get('sizes')
    for candidate in image.get('srcset').split(','):
        file = path.parent / candidate.strip().split()[0]
        with Image.open(file) as opened: assert opened.format == 'WEBP'
    bodies.append(hashlib.sha256(body.text_content().encode()).hexdigest())
assert len(set(bodies)) == 10
for filename,lang in [('journal.html','hi'),('journal-english.html','en')]:
    doc = html.parse(str(public / filename)).getroot()
    for row in [r for r in manifest if r['lang'] == lang]:
        card = doc.xpath('//*[@id="journal-grid"]/article[.//h2/a[@href=$url]]',url=row['url'])
        assert len(card) == 1 and card[0].xpath('.//time[@datetime=$d]',d=row['datePublished']), row['url']
feed = etree.parse(str(public / 'journal-feed.xml'))
assert len(feed.xpath('//item')) == 10
assert len(set(feed.xpath('//item/guid/text()'))) == 10
for item in feed.xpath('//item'):
    assert item.findtext('link') == item.findtext('guid')
    row = next(r for r in manifest if 'https://courses.astrovedansh.org/'+r['url'] == item.findtext('link'))
    assert row['lang'] == 'hi' and item.findtext('pubDate')
sitemap = etree.parse(str(public / 'sitemap.xml'))
for item in batch['items']:
    assert sitemap.xpath('//*[local-name()="loc" and text()=$url]',url='https://courses.astrovedansh.org/'+item['url'])
assert 'Sitemap: https://courses.astrovedansh.org/sitemap.xml' in (public / 'robots.txt').read_text()
print(json.dumps({'batch':date,'passed':True,'lessons':10,'all_article_dates_checked':len(manifest),'words':[i['body_words'] for i in batch['items']],'feed_items':10}))
