"""Review declared delta, complete compiled results and executable admission."""
from pathlib import Path
import re,json,hashlib,datetime,ast
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-low812';P=Path('C:/xwn814/build002')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x812(?=[0-9a-f]{0,2}$)','0x814',p) if i%2 else p.replace('812','814') for i,p in enumerate(parts))
out=K/'review001.json';assert not out.exists()
r=dict(passed=False,physical_access=False,reviewer_sha256=sha(Path(__file__)))
try:
 for p in K.glob('*.py'):ast.parse(p.read_text())
 d=read(K/'delta001.json');s=(K/'probe.c').read_text()
 assert sha(K.parent/'xcal-transaction704/transaction003.c')==d['recipe_sha256']
 recipe=(K.parent/'xcal-transaction704/transaction003.c').read_text()
 for entry in ['{0x1a,255,4}','{0x25,255,0x10}','{0x28,255,0x83}','{0x2d,31,0}']:assert entry in recipe.replace(' ','')
 for field in ['helpers','init']:assert s.count(d[field])==1;s=s.replace(d[field],'')
 s=s.replace(' if(!controls_forward814(o))goto restore;\n','').replace(' controls_restore814(o);\n','')
 s=s.replace(' && !o->mc_cleanup_mask','').replace(' if(o->mc_cleanup_mask)o->code=0x81454;\n','')
 assert s==ns((O/'probe.c').read_text())
 assert (K/'probe.h').read_text().replace(d['decl'],'')==ns((O/'probe.h').read_text())
 s=(K/'main.c').read_text().replace('words[917]','words[820]').replace('i<917','i<820').replace('crtc_mode_controls','crtc_linecompare_low_control').replace(' || result.mc_cleanup_mask','').replace(' || (result.code>=0x81450 && result.code<=0x81453)','')
 assert s==ns((O/'main.c').read_text())
 for n in ['layout.c','layout.h']:assert (K/n).read_text()==ns((O/n).read_text())
 for n,h in d['parent'].items():assert sha(O/n)==h
 for n in ['main.c','probe.c','probe.h','layout.c','layout.h','Makefile']:
  assert sha(K/n)==sha(P/n)==read(K/'build002.json')['files'][n]['sha256']
 from prefix_audit import validate as pv
 from audit_logic import validate
 p=read(K/'prefix002.json');t=read(K/'tail002.json')
 assert p['passed'] and p['case_count']==1014 and t['passed'] and t['case_count']==146
 for case in p['cases']:
  v=case['raw_result'];assert len(v)==917;pv(v[:820])
  if v[0]==0x814:validate(v)
 clean=t['cases'][0]['raw_result'];validate(clean)
 rejected=[]
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,917)):
  v=clean.copy();v[i]^=1
  try:validate(v)
  except AssertionError:rejected.append(i)
  else:raise AssertionError(('accepted mutation',i))
 checks=['build002.json','prefix002.json','tail002.json','layout-model001.json','frontend-model002.json','clock-model006.json','link-review001.json','layout-link-review001.json','main-link-review001.json','controller-review002.json']
 assert all(read(K/n)['passed'] for n in checks)
 s=(K/'physical.py').read_text();assert 'review-only cutoff' not in s and "'prefix002.json'" in s
 a=(K/'audit_collection001.py').read_text();assert 'len(v)==917' in a and "launch['utc']<dashboard['utc']<=c['utc']" in a
 r.update(passed=True,checks={n:sha(K/n) for n in checks},prefix_cases=1014,tail_cases=146,rejected_schema_mutations=rejected,
  result_words=917,launch_qualified=True,scope='Kernel-context only; physical behavior still unknown',
  cutoff_basis='Explicit user renewal after23:00UTC; automation remains PAUSED',
  remaining=['fresh dashboard authentication','unique stage/readback','one launch','collection and independent audit'])
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
with (K/'sources001.json').open('x') as f:
 json.dump({p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h'] or p.name in ['Makefile','.gitattributes','.gitignore']},f,indent=2);f.write('\n')
print('PASS814 frozen host qualification; no physical result yet')
