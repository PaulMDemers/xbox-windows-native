"""Independent namespace-only cold-condition control qualification."""
from pathlib import Path
import re,ast,json,hashlib,datetime
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-bit809';P=Path('C:/xwn810/build002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x809(?=[0-9a-f]{0,2}$)','0x810',p) if i%2 else p.replace('809','810') for i,p in enumerate(parts)).replace('crtc-linecompare-bit810','crtc-linecompare-cold810')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r=dict(passed=False,reviewer_sha256=sha(Path(__file__)));assert not (K/'review003.json').exists()
try:
 assert read(O/'closed001.json')['closed'] and not read(O/'closed001.json')['passed']
 assert read(O/'review003.json')['passed']
 for n,h in read(O/'sources001.json').items():assert sha(O/n)==h,n
 for p in K.glob('*.py'):ast.parse(p.read_text())
 guest=['probe.c','probe.h','main.c','layout.c','layout.h','Makefile']
 for n in guest:
  assert (K/n).read_text()==ns((O/n).read_text()),n
  assert sha(K/n)==sha(P/n),n
 for n in ['model006.py','layout_model.py','clock_model004.py','frontend_model002.py','audit_logic.py','prefix_schema.py']:
  assert (K/n).read_text()==ns((O/n).read_text()),n
 probe=(K/'probe.c').read_text();assert 'o->cr22_before==0xfe' in probe and not re.search(r'cw\(0x22,',probe)
 from audit_logic import validate
 m=read(K/'model006.json');assert m['passed'] and len(m['cases'])==1014
 for c in m['cases']:validate(c['raw_result'])
 base=m['cases'][0]['raw_result'];assert base[760:766]==[64,64,1,64,64,0]
 rejected=[]
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,790)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:rejected.append(i)
  else:raise AssertionError(('accepted mutation',i))
 checks=['build002.json','model006.json','layout-model001.json','clock-model005.json','frontend-model002.json','link-review001.json','layout-link-review001.json','main-link-review001.json','controller-review003.json']
 assert all(read(K/n)['passed'] for n in checks)
 assert read(K/'layout-model001.json')['case_count']==2353 and len(read(K/'clock-model005.json')['cases'])==10
 assert read(K/'frontend-model002.json')['case_count']==26
 physical=(K/'physical.py').read_text();assert "cold['user_confirmed_ten_second_power_cycle']" in physical
 save('schema001.json',read(O/'schema001.json'))
 save('source-review003.json',dict(passed=True,namespace_only_guest=True,CR22_FE_guard_preserved=True,new_cold_readiness_gate=True,model_cases=1014,rejected_schema_mutations=rejected,physical_proof=False))
 checks+=['schema001.json','source-review003.json','derivation001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=1014,physical_proof=False)
 save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes','.gitignore']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review003.json',r)
print('PASS810 namespace-only cold-condition qualification')
