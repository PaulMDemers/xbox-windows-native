"""Independent delta and complete compiled result qualification for816."""
from pathlib import Path
import ast,re,json,hashlib,datetime
K=Path(__file__).resolve().parent;O=K.parent/'crtc-mode-controls815';P=Path('C:/xwn816/build002')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x815(?=[0-9a-f]{0,2}$)','0x816',p) if i%2 else p.replace('815','816') for i,p in enumerate(parts))
out=K/'review001.json';assert not out.exists();r=dict(passed=False,physical_access=False,reviewer_sha256=sha(Path(__file__)))
try:
 for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
 d=read(K/'lineage001.json');assert read(O/'closed001.json')['closed'] and sha(O/'audit002.json')==d['measurement']
 assert read(O/'audit002.json')['raw_result'][820:830]==[56,16,131,224,104,48,227,255,62,64]
 for n,h in d['parent'].items():assert sha(O/n)==h
 for n in ['main.c','probe.h','layout.c','layout.h','Makefile']:assert (K/n).read_text()==ns((O/n).read_text())
 expected=ns((O/'probe.c').read_text()).replace('o->mc_target[0]=4;','o->mc_target[0]=o->mc_before[0]|4;').replace('Pinned704 final four geometry controls','Diagnostic alternative: CR1A bit2-only; remaining704 geometry controls')
 assert (K/'probe.c').read_text()==expected
 assert 'o->mc_target[3]=o->mc_before[3]&0xe0;' in expected
 for n in ['main.c','probe.c','probe.h','layout.c','layout.h','Makefile']:assert sha(K/n)==sha(P/n)==read(K/'build002.json')['files'][n]['sha256']
 from prefix_audit import validate as pv
 from audit_logic import validate
 p=read(K/'prefix002.json');t=read(K/'tail002.json');assert p['passed'] and p['case_count']==1014 and t['passed'] and t['case_count']==146
 for case in p['cases']:
  v=case['raw_result'];assert len(v)==917;pv(v[:820])
  if v[0]==0x816:validate(v)
 clean=t['cases'][0]['raw_result'];validate(clean);rejected=[]
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,917)):
  v=clean.copy();v[i]^=1
  try:validate(v)
  except AssertionError:rejected.append(i)
  else:raise AssertionError(('accepted mutation',i))
 checks=['build002.json','prefix002.json','tail002.json','layout-model001.json','frontend-model002.json','clock-model006.json','link-review001.json','layout-link-review001.json','main-link-review001.json','controller-review002.json']
 assert all(read(K/n)['passed'] for n in checks)
 assert read(K/'controller-review002.json')['controller_sha256']==sha(K/'physical.py')
 r.update(passed=True,checks={n:sha(K/n) for n in checks},prefix_cases=1014,tail_cases=146,rejected_schema_mutations=rejected,result_words=917,launch_qualified=True,scope='Bit2-only CR1A preservation diagnostic qualification; kernel context only; physical result unknown')
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
with (K/'sources001.json').open('x') as f:json.dump({p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h'] or p.name in ['Makefile','.gitattributes','.gitignore']},f,indent=2);f.write('\n')
print('PASS816 frozen host qualification')
