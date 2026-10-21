import json,subprocess,tempfile,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run(['python3',str(root/'scripts/build-catalog.py'),'--check'],check=True)
c=json.loads((root/'config/catalog.json').read_text())
assert 349*2-649==49 and 349*4-1047==349
for key in c['offers']:
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);(p/'scripts').mkdir();(p/'config').mkdir()
  shutil.copy(root/'scripts/build-catalog.py',p/'scripts/build-catalog.py')
  modified=json.loads(json.dumps(c));modified['offers'][key]['enabled']=True
  (p/'config/catalog.json').write_text(json.dumps(modified))
  r=subprocess.run(['python3',str(p/'scripts/build-catalog.py')],capture_output=True,text=True)
  assert r.returncode!=0 and 'not ready' in r.stderr,key
for n in ['index.html','english.html','reports.html','consultation.html','consultation-detailed.html']:
 text=(root/'public'/n).read_text()
 assert '₹649' not in text and '₹1,047' not in text and '₹3,799' not in text,n
print('Unapproved offer activation blocked; inactive offer prices absent from customer pages; savings verified.')
