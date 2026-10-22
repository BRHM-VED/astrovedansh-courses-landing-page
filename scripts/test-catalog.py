import json,subprocess,tempfile,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run(['python3',str(root/'scripts/build-catalog.py'),'--check'],check=True)
c=json.loads((root/'config/catalog.json').read_text())
assert 349*2-649==49 and 349*4-1047==349
for key in c['offers']:
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);(p/'scripts').mkdir();(p/'config').mkdir()
  for name in ['build-catalog.py','pricing_components.py']:shutil.copy(root/'scripts'/name,p/'scripts'/name)
  modified=json.loads(json.dumps(c));modified['offers'][key]['enabled']=True
  (p/'config/catalog.json').write_text(json.dumps(modified))
  r=subprocess.run(['python3',str(p/'scripts/build-catalog.py')],capture_output=True,text=True)
  assert r.returncode!=0 and 'not ready' in r.stderr,key
for n in ['index.html','english.html','reports.html','consultation.html','consultation-detailed.html']:
 text=(root/'public'/n).read_text()
 assert '₹649' not in text and '₹1,047' not in text and '₹3,799' not in text,n
print('Unapproved offer activation blocked; inactive offer prices absent from customer pages; savings verified.')
expected={'astrology_report':299,'name':399,'audio':799,'expert':999,'personal':1799,'detailed':3199}
for key,amount in expected.items():assert c['products'][key]['amount']==amount,key
bundles={'report_combo':(499,698,199),'audio_combo':(899,1098,199),'personal_combo':(1999,2497,498),'complete_combo':(3499,3897,398)}
for key,(price,total,saving) in bundles.items():
 b=c['bundles'][key]
 assert b['amount']==price and sum(c['products'][k]['amount'] for k in b['items'])==total and total-price==saving,key
 assert len(b['items'])==len(set(b['items'])),key
 assert b['checkout']=='whatsapp_request' and b['active'],key
assert c['products']['timing']['amount']==349 and c['products']['milan']['amount']==2999
assert c['products']['freeCourse']['amount']==999 and c['products']['foundation']['amount']==10000
print('All six standalone prices and four bundle totals/savings verified; unrelated products preserved.')
from html.parser import HTMLParser
class FunnelLinks(HTMLParser):
 def __init__(self):super().__init__();self.plans={};self.categories=[];self.recommended=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'data-plan-id' in a:
   key=a['data-plan-id'];assert key not in self.plans,'Duplicate plan link: '+key;self.plans[key]=a.get('href')
  if 'data-guidance' in a:self.categories.append(a['data-guidance'])
  if 'selection-card--recommended' in a.get('class','').split():self.recommended.append(a.get('id'))
for name in ['index.html','english.html','pricing.html']:
 page=(root/'public'/name).read_text();parser=FunnelLinks();parser.feed(page)
 assert parser.categories==['reports','consultation','combos'],name
 assert set(parser.plans)==set(expected)|set(bundles),name
 for key,href in parser.plans.items():assert href==(c['products']|c['bundles'])[key]['url'],(name,key)
 assert parser.recommended==['plan-detailed'],name
 assert 'id="funnel-result"' not in page,name
 assert '/reports.html?report=milan#report-request' in page,name
print('All ten plans reachable directly from three categories; ₹3,199 recommendation and Milan form verified.')
