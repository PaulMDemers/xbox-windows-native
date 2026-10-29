"""Independent812 source-delta and raw-result schema review; no launch admission."""
from pathlib import Path
import re,json,hashlib,datetime,ast
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-cold810';P=Path('C:/xwn812/build002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x810(?=[0-9a-f]{0,2}$)','0x812',p) if i%2 else re.sub(r'\b810\b|(?<=[A-Za-z_])810\b','812',p) for i,p in enumerate(parts))
r={'passed':False,'physical_access':False,'reviewer_sha256':sha(Path(__file__))};out=K/'review002.json';assert not out.exists()
try:
 for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
 d=read(K/'delta001.json');s=(K/'probe.c').read_text()
 assert s.index(d['block'])<s.index('restore:')<s.index(d['undo'])<s.index(' if(o->cl9_attempted){')
 assert s.count('cw(0x18,')==2 and not re.search(r'cw\(0x22,',s)
 for t in [d['block'],d['undo'],d['init']]:assert s.count(t)==1;s=s.replace(t,'')
 s=s.replace(' && !o->cl18_cleanup_mask','').replace(' if(o->cl18_cleanup_mask)o->code=0x81249;\n','')
 assert s==ns((O/'probe.c').read_text()),'probe delta outside declared transaction'
 h=(K/'probe.h').read_text();addition=' uint32_t '+','.join(d['fields'])+';\n'
 assert h.count(addition)==1 and h.replace(addition,'')==ns((O/'probe.h').read_text())
 main=(K/'main.c').read_text();s=main.replace('words[820]','words[790]').replace('i<820','i<790').replace('crtc_linecompare_low_control','crtc_linecompare_bit_control').replace(' || result.cl18_cleanup_mask','').replace(' || result.code==0x81248','')
 assert s==ns((O/'main.c').read_text()),'frontend delta outside declared changes'
 for name in ['main.c','probe.c','probe.h','layout.c','layout.h','Makefile']:
  assert sha(K/name)==sha(P/name)==read(K/'build002.json')['files'][name]['sha256']
 for name in ['layout.c','layout.h']:assert (K/name).read_text()==ns((O/name).read_text())
 from audit_logic import validate
 counts={}
 for name in ['model004.json','model005.json']:
  m=read(K/name);assert m['passed'];counts[name]=len(m['cases'])
  for case in m['cases']:
   try:validate(case['raw_result'])
   except AssertionError as e:raise AssertionError((name,case['name'],'schema rejection')) from e
 assert counts=={'model004.json':51,'model005.json':1014}
 base=read(K/'model004.json')['cases'][0]['raw_result'];rejected=[]
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,820)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:rejected.append(i)
  else:raise AssertionError(('accepted mutation',i))
 checks=['build002.json','model001.json','model003.json','model004.json','model005.json','layout-model001.json','frontend-model002.json','clock-model006.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 r.update(passed=True,checks={n:sha(K/n) for n in checks},schema_cases=counts,rejected_schema_mutations=rejected,
  result_words=820,launch_qualified=False,remaining=['controller and collection audit derivation/review','frozen source manifest','physical staging/readback','physical kernel result'])
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS812 source and schema review; controller and physical gates remain')
