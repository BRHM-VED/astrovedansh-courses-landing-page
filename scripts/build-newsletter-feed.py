"""Build a public RSS feed from published Hindi articles, preserving publication dates."""
from pathlib import Path
from html.parser import HTMLParser
import json
from datetime import datetime
from email.utils import format_datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://courses.astrovedansh.org'

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__(); self.capture=False; self.parts=[]; self.schemas=[]; self.description=''
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='meta' and a.get('name')=='description': self.description=a.get('content','')
        if tag=='script' and a.get('type')=='application/ld+json': self.capture=True; self.parts=[]
    def handle_data(self, data):
        if self.capture: self.parts.append(data)
    def handle_endtag(self, tag):
        if tag=='script' and self.capture:
            self.schemas.append(json.loads(''.join(self.parts))); self.capture=False

items=[]
for row in json.loads((ROOT/'content/journal-manifest.json').read_text()):
    if row['lang']!='hi': continue
    parser=Metadata(); parser.feed((ROOT/'public'/row['url']).read_text())
    for schema in parser.schemas:
        for article in schema.get('@graph',[schema]):
            if article.get('@type') not in ('BlogPosting','Article'): continue
            date=datetime.fromisoformat(article['datePublished'].replace('Z','+00:00'))
            if date.tzinfo is None:
                from zoneinfo import ZoneInfo
                date=date.replace(tzinfo=ZoneInfo('Asia/Kolkata'))
            items.append((date,row,parser.description))
items.sort(key=lambda x:(x[0],x[1]['number']),reverse=True)
root=Element('rss',version='2.0'); channel=SubElement(root,'channel')
for key,value in [('title','AstroVedansh अध्ययन पत्रिका'),('link',ORIGIN+'/journal.html'),('description','ज्योतिष और अंकज्योतिष सीखने के लिए सरल उदाहरण और उपयोगी अभ्यास।'),('language','hi-IN')]:
    SubElement(channel,key).text=value
for date,row,description in items[:10]:
    item=SubElement(channel,'item'); url=ORIGIN+'/'+row['url']
    for key,value in [('title',row['title']),('link',url),('description',description),('pubDate',format_datetime(date)),('guid',url)]:
        SubElement(item,key).text=value
ElementTree(root).write(ROOT/'public/journal-feed.xml',encoding='utf-8',xml_declaration=True)
print(f'RSS: {min(10,len(items))} articles, original publication dates retained')
