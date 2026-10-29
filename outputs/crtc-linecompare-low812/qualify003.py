"""Freeze812 host qualification and controller; does not prove physical behavior."""
from pathlib import Path
import ast,hashlib,json,datetime
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
assert read('review002.json')['passed'] and read('controller-review003.json')['passed']
assert read('model004.json')['case_count']==51 and read('model005.json')['case_count']==1014
assert read('layout-model001.json')['case_count']==2353
assert read('frontend-model002.json')['case_count']==26 and len(read('clock-model006.json')['cases'])==10
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
s=(K/'physical.py').read_text()
assert "datetime.datetime(2026,10,29,22,50,tzinfo=datetime.timezone.utc)" in s
a=(K/'audit_collection002.py').read_text()
assert 'len(v)==820' in a and "launch['utc']<dashboard['utc']<=c['utc']" in a
assert "'crtc_linecompare_low_control_armed','crtc_linecompare_low_control_returned'" in a
checks=list(read('review002.json')['checks'])+['review002.json','controller-review003.json','controller-lineage001.json']
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer_sha256':sha(Path(__file__)),
 'checks':{n:sha(K/n) for n in checks},'host_qualification_only':True,'physical_result':None,
 'launch_qualified':True,'mode':'kernel-context automatic return, no startup hook or Windows',
 'remaining':'Fresh dashboard authentication, unique staging/readback, one launch, collection and independent audit',
 'preserved_failures':['model002.json','clock-model005.json','review001.json'],
 'same_value_effectiveness_proved':False}
with (K/'review003.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
with (K/'sources001.json').open('x') as f:
 json.dump({p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h'] or p.name in ['Makefile','.gitattributes','.gitignore']},f,indent=2);f.write('\n')
print('PASS812 frozen host qualification; physical result remains unknown')
