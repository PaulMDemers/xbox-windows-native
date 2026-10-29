"""Independent803 exact source, hardware constant, compiled admission and schema review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vblank-overflow802';P=Path('C:/xwn803/build002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):
 # Literal spans are processed independently: no placeholder identifiers to rename.
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x802(?=[0-9a-f]{0,2}$)','0x803',p) if i%2 else p.replace('802','803') for i,p in enumerate(parts))
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r=dict(passed=False,reviewer_sha256=sha(Path(__file__)));assert not (K/'review002.json').exists()
try:
 assert read(O/'closed001.json')['closed'] and not read(O/'closed001.json')['passed']
 for p in K.glob('*.py'):ast.parse(p.read_text())
 for n in ['probe.c','probe.h','main.c','layout.c','layout.h','Makefile']:
  src=(O/n).read_text()
  if n=='main.c':assert src.count('pci[9]==0x8021')==1;src=src.replace('pci[9]==0x8021','pci[9]==0x8001')
  assert (K/n).read_text()==ns(src),n
  assert sha(K/n)==sha(P/n),n
 # Explicit independent literals for the complete frontend admission, not inferred
 # from a successful namespace comparison or the preceding erroneous source.
 body=(K/'main.c').read_text();compact=re.sub(r'\s+','',body)
 expected='intbaseline=pci[0]==0x02a010de&&(pci[1]&2)&&(pci[2]&0xfffffff7)==0xfd000000&&pci[3]==0x01b410de&&(pci[4]&1)&&pci[5]==0xc001&&pci[6]==0x01b210de&&(pci[7]&1)&&pci[8]==0&&pci[9]==0x8001;'
 assert expected in compact and 'pci[9]==0x8031' not in body
 expected='baseline=baseline&&!(by_index[0x11]&0x80)&&(by_index[0x21]&0xfa)==0xfa&&by_index[0x44]==0&&!(by_index[9]&0x80)&&by_index[0x39]==0xff&&VIDEOREG(0x680508)==0x3c20d&&VIDEOREG(0x68050c)==0x100a0400&&VIDEOREG(0x680880)==0x21101100&&VIDEOREG(0x100200)==0x3070003&&VIDEOREG(0x600804)==3;'
 assert expected in compact
 probe=(K/'probe.c').read_text()
 assert '(o->cr0&0x80000001)!=0x80000001' in probe
 assert 'o->cb7_target=(o->cb7_before&0xf7u)|(((480u-1u)>>5)&0x08u);' in probe
 assert '(54&0xf7)|(((480-1)>>5)&8)' and ((54&0xf7)|(((480-1)>>5)&8))==62
 for n in ['audit_logic.py','prefix_schema.py']:
  assert (K/n).read_text()==ns((O/n).read_text()),n
 from audit_logic import validate
 m=read(K/'model003.json');assert m['passed'] and len(m['cases'])==894
 for c in m['cases']:validate(c['raw_result'])
 base=m['cases'][0]['raw_result'];assert base[670:]==[54,62,1,62,54,0]+[v for a in [12,64,233,223,207,140,255,16] for v in [a]*3]
 mutations=[]
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,700)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in m['cases']:
  if c['raw_result'][675]:
   assert c['raw_result'][0]==0x80341 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:pass
   else:raise AssertionError('unsafe output-enable admitted')
 checks=['build002.json','model003.json','layout-model001.json','clock-model003.json','frontend-model002.json','link-review001.json','layout-link-review001.json','main-link-review001.json','controller-review002.json']
 assert all(read(K/n)['passed'] for n in checks)
 assert read(K/'layout-model001.json')['case_count']==2353
 assert len(read(K/'clock-model003.json')['cases'])==10
 f=read(K/'frontend-model002.json');assert f['case_count']==26 and f['hardware_PCI_literal']==0x8001
 assert f['cases'][0]['refused']==False and all(c['refused'] for c in f['cases'][1:])
 save('schema001.json',dict(words=700,bytes=2800,inherited='802 exact result contract; namespace803; hardware constants unchanged',baseline=54,target=62,restoration='saved54 before CR09 recovery',recovery_mask_count=29))
 save('source-review002.json',dict(passed=True,exact_source_only_delta=True,PCI_literal=0x8001,compiled_frontend_cases=26,register_model_cases=894,rejected_schema_mutations=mutations,no_physical_proof=True))
 checks+=['schema001.json','source-review002.json','lineage001.json','qualification-failure001.json','qualification-failure002.json','qualification-failure003.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=894,frontend_cases=26,physical_proof=False)
 save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes','.gitignore']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review002.json',r)
print('PASS803 source, compiled frontend and complete schema review')
