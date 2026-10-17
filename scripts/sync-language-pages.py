"""Render the complete English page from the Hindi/Hinglish page.

The two language choices are normal links, so the whole page switches even
when JavaScript is disabled. Run this after changing index.html or en.json.
Requires lxml, available in the authoring environment.
"""
from pathlib import Path
import json
import re
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
ENGLISH = json.loads((ROOT / 'translations/en.json').read_text())
DEVANAGARI = re.compile(r'[\u0900-\u097f]')


def translate(value):
    if not value or not DEVANAGARI.search(value):
        return value
    key = value.strip()
    if key not in ENGLISH:
        raise ValueError(f'Missing English translation: {key}')
    prefix = value[:len(value) - len(value.lstrip())]
    suffix = value[len(value.rstrip()):]
    replacement = ENGLISH[key]
    if re.match(r'^[,.;:!?]', replacement):
        return replacement + suffix
    return prefix + replacement + suffix


def inside_language_switch(element):
    return any('language-switch' in el.get('class', '').split()
               for el in [element, *element.iterancestors()])


for source_name, target_name in [('index.html', 'english.html'), ('numerology.html', 'numerology-english.html')]:
    doc = html.document_fromstring((ROOT / ('public/' + source_name)).read_text())
    doc.set('lang', 'en')
    language_options = doc.xpath('//nav[@class="language-switch"]/a')
    for link in language_options:
        link.attrib.pop('aria-current', None)
        if link.get('lang') == 'en':
            link.set('aria-current', 'page')
        else:
            link.set('aria-label', 'Read this page in Hindi')

    for element in doc.iter():
        if not isinstance(element.tag, str):
            continue
        if element.tag not in {'script', 'style'} and not inside_language_switch(element):
            element.text = translate(element.text)
        element.tail = translate(element.tail)
        for attribute in ('alt', 'aria-label', 'title', 'content'):
            if attribute in element.attrib:
                element.set(attribute, translate(element.get(attribute)))

    for link in doc.xpath('//a[@href]'):
        if inside_language_switch(link):
            continue
        href = link.get('href')
        if href.endswith('.chatgpt.site/account'):
            link.set('href', href + '?lang=en')
        if href == 'free-tools.html':
            link.set('href', 'free-tools-english.html')
        if href == 'journal.html':
            link.set('href', 'journal-english.html')
        elif href.startswith('journal/'):
            manifest = json.loads((ROOT / 'content/journal-manifest.json').read_text())
            original = next((x for x in manifest if x['url'] == href), None)
            alternate = next((x for x in manifest if original and x['number'] == original['number'] and x['lang'] == 'en'), None)
            if alternate: link.set('href', alternate['url'])
        if href == 'numerology.html' or href.startswith('numerology.html#'):
            link.set('href', href.replace('numerology.html', 'numerology-english.html', 1))
        elif href == 'index.html' or href.startswith('index.html#'):
            link.set('href', href.replace('index.html', 'english.html', 1))
    if source_name == 'numerology.html':
        doc.xpath('//meta[@property="og:url"]')[0].set('content', 'https://astrovedansh-basic-astrology.astrovedansh.chatgpt.site/numerology-english.html')

    remaining = [text for text in doc.xpath('//text()')
                 if DEVANAGARI.search(str(text))
                 and not inside_language_switch(text.getparent())]
    if remaining:
        raise ValueError(f'Untranslated English content: {remaining}')

    output = '<!doctype html>\n' + html.tostring(doc, encoding='unicode', method='html') + '\n'
    (ROOT / ('public/' + target_name)).write_text(output)
    print(f'English page generated. {len(ENGLISH)} translations; no Hindi content outside the language selector.')
