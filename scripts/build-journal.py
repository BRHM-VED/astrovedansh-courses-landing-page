"""Build 100 original Hindi study articles and their searchable static index."""
from pathlib import Path
import json, re, html

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'public'
esc = html.escape
rows = []
category = ''
for line in (ROOT / 'content/journal-topics.txt').read_text().splitlines():
    if not line.strip(): continue
    if '|' not in line:
        category = line.strip(); continue
    title, lead, method, exercise, caution = line.split('|')
    rows.append(dict(category=category, title=title, paragraphs=[lead, method, exercise, caution]))
reflections = (ROOT / 'content/journal-reflections.txt').read_text().splitlines()
assert len(rows) == len(reflections) == 100
for row, reflection in zip(rows, reflections):
    row['paragraphs'].insert(3, reflection)
    row['words'] = len(' '.join(row['paragraphs']).split())
    assert 150 <= row['words'] <= 200, (row['title'], row['words'])
assert len({r['title'] for r in rows}) == len({' '.join(r['paragraphs']) for r in rows}) == 100
categories = ['अध्ययन की शुरुआत', 'कुंडली की भाषा', 'ग्रहों का अध्ययन', 'भाव और जीवन क्षेत्र', 'राशियाँ और संबंध', 'दशा और समय', 'योग और वर्ग कुंडलियाँ', 'अभ्यास और शोध', 'जिम्मेदार संवाद', 'आगे की सीख और काम']
rows.sort(key=lambda r: categories.index(r['category']))
for i, row in enumerate(rows, 1): row.update(number=i, url=f'journal/lesson-{i:03}.html')

def page(title, description, body, prefix='', script=False):
    return f'''<!doctype html>
<html lang="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#631ca0"><title>{esc(title)} | AstroVedansh®</title><meta name="description" content="{esc(description)}"><link rel="icon" href="{prefix}assets/astrovedansh-logo.webp"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700;800&display=swap" rel="stylesheet"><link rel="stylesheet" href="{prefix}journal.css"></head><body><a class="journal-skip" href="#main">मुख्य सामग्री पर जाएँ</a><header class="j-header"><div class="j-container"><a class="j-brand" href="{prefix}index.html"><img src="{prefix}assets/astrovedansh-logo.webp" width="44" height="44" alt=""><span>Astro<strong>Vedansh</strong><sup>®</sup></span></a><nav aria-label="मुख्य मार्ग"><a href="{prefix}journal.html">अध्ययन पत्रिका</a><a href="{prefix}index.html#courses">पाठ्यक्रम देखें ↗</a></nav></div></header>{body}<footer class="j-footer"><div class="j-container"><strong>AstroVedansh® अध्ययन पत्रिका</strong><p>परम्परा को समझें। प्रश्न पूछें। अभ्यास से आगे बढ़ें।</p><a href="{prefix}index.html#about">अपने शिक्षक से मिलें →</a><p class="j-editorial">ये लेख ज्योतिष की पारंपरिक अवधारणाओं और जिम्मेदार अध्ययन के लिए हैं। व्यक्तिगत भविष्यवाणी या वैज्ञानिक रूप से प्रमाणित परिणाम का दावा नहीं।</p></div></footer>{'<script src="journal.js" defer></script>' if script else ''}</body></html>'''

def card(row, prefix=''):
    return f'''<article class="j-card" data-category="{esc(row['category'])}" data-search="{esc(row['title']+' '+row['category']+' '+row['paragraphs'][0])}"><div class="j-card-art" aria-hidden="true"><span>{row['number']:02}</span><i>✧</i></div><div class="j-card-body"><span class="j-tag">{esc(row['category'])}</span><h2><a href="{prefix}{row['url']}">{esc(row['title'])}</a></h2><p>{esc(row['paragraphs'][0])}</p><div class="j-card-bottom"><span>{row['words']} शब्द</span><a href="{prefix}{row['url']}" aria-label="{esc(row['title'])} — पूरा लेख पढ़ें">पढ़ें <span aria-hidden="true">→</span></a></div></div></article>'''

(P / 'journal').mkdir(exist_ok=True)
for i, row in enumerate(rows):
    previous = rows[i-1] if i else None
    next_row = rows[i+1] if i+1 < len(rows) else None
    neighbors = ''.join(f'<a href="lesson-{r["number"]:03}.html"><small>{label}</small><span>{esc(r["title"])}</span></a>' for r, label in [(previous, '← पिछला लेख'), (next_row, 'अगला लेख →')] if r)
    body = f'''<main id="main" class="j-reader"><nav class="j-breadcrumb" aria-label="आप यहाँ हैं"><a href="../index.html">मुख्य पृष्ठ</a><span>/</span><a href="../journal.html">अध्ययन पत्रिका</a></nav><header class="j-article-header"><a class="j-tag" href="../journal.html?category={esc(row['category'])}">{esc(row['category'])}</a><h1>{esc(row['title'])}</h1><p class="j-meta">लेख {row['number']:02} / 100 <span>·</span> {row['words']} शब्द <span>·</span> हिन्दी</p></header><article class="j-prose" aria-label="लेख">{''.join('<p>'+esc(p)+'</p>' for p in row['paragraphs'])}</article><aside class="j-reader-cta"><span>पढ़ने से अभ्यास की ओर</span><h2>अब सीखने को एक क्रम दें।</h2><p>कक्षा, प्रश्न और कुंडली अभ्यास के साथ अपना आधार मजबूत करें।</p><a href="../index.html#courses">पाठ्यक्रम देखें →</a></aside><nav class="j-neighbors" aria-label="और लेख पढ़ें">{neighbors}</nav><a class="j-back" href="../journal.html">सभी 100 लेख देखें →</a></main>'''
    (P / row['url']).write_text(page(row['title'], row['paragraphs'][0], body, '../'))

options = '<option value="">सभी विषय</option>' + ''.join(f'<option>{esc(c)}</option>' for c in categories)
body = f'''<main id="main"><section class="j-hero"><div class="j-container"><span class="j-eyebrow">अध्ययन पत्रिका · हिन्दी</span><h1>एक नई समझ।<br><em>हर लेख के साथ।</em></h1><p>ज्योतिष सीखने के लिए 100 उपयोगी लेख। शुरुआती सवालों से कुंडली अभ्यास और जिम्मेदार संवाद तक।</p><div class="j-pills"><span>100 अलग विषय</span><span>10 अध्ययन श्रेणियाँ</span><span>हर लेख 150–200 शब्द</span></div></div></section><section class="j-container j-library" aria-label="लेखों का संग्रह"><form class="j-controls" role="search"><div><label for="journal-search">क्या सीखना चाहते हैं?</label><input id="journal-search" type="search" placeholder="जैसे: लग्न, दशा, करियर…" autocomplete="off"></div><div><label for="journal-category">विषय चुनें</label><select id="journal-category">{options}</select></div><button type="reset">सभी दिखाएँ</button></form><div class="j-results-heading"><h2>आपकी अध्ययन सूची</h2><p id="journal-status" role="status" aria-live="polite">100 लेख उपलब्ध</p></div><div class="j-grid" id="journal-grid">{''.join(card(r) for r in rows)}</div><p id="journal-empty" hidden>इस खोज से कोई लेख नहीं मिला। दूसरा शब्द या विषय चुनें।</p><nav class="j-pagination" aria-label="लेख सूची के पृष्ठ" hidden><button id="journal-prev" type="button">← पिछला</button><span id="journal-page"></span><button id="journal-next" type="button">अगला →</button></nav><noscript><p>सभी 100 लेख नीचे उपलब्ध हैं। अपने ब्राउज़र की खोज से विषय ढूँढ़ सकते हैं।</p></noscript></section></main>'''
(P / 'journal.html').write_text(page('ज्योतिष सीखने के 100 लेख', 'ज्योतिष सीखने पर 100 हिन्दी लेख: आधार, ग्रह, भाव, दशा, कुंडली अभ्यास और जिम्मेदार संवाद।', body, script=True))
(ROOT / 'content/journal-manifest.json').write_text(json.dumps([{'title':r['title'],'category':r['category'],'url':r['url'],'words':r['words']} for r in rows],ensure_ascii=False,indent=2)+'\n')
print(f'Built {len(rows)} unique articles: {min(r["words"] for r in rows)}–{max(r["words"] for r in rows)} words each; 10 categories.')
