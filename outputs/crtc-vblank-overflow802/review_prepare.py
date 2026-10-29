"""Review source delta, independent literals, recovery, and actual compiled evidence."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vblank-bit800';P=Path('C:/xwn802/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):
 constants=[]
 def keep(m):constants.append(m[0]);return '@HEX'+str(len(constants)-1)+'@'
 s=re.sub(r'0x[0-9a-fA-F]{6,}',keep,s)
 s=s.replace('800','802').replace('crtc-vblank-bit802','crtc-vblank-overflow802')
 return re.sub(r'@HEX(\d+)@',lambda m:constants[int(m[1])],s)

def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->cb7_cleanup_mask',' if(o->cb7_cleanup_mask)o->code=0x80241;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['cb7_before','cb7_target','cb7_attempted','cb7_after','cb7_restored','cb7_cleanup_mask']
 for n in ['cb7_c6','cb7_c9','cb7_c10','cb7_c12','cb7_c15','cb7_c16','cb7_c18','cb7_c25']:fields += [n+'_before',n+'_after',n+'_restored']
 assert fields==d['fields'] and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[670]','words[700]').replace('i<670','i<700').replace('crtc_vblank_bit_control','crtc_vblank_overflow_control').replace('result.cb9_cleanup_mask){','result.cb9_cleanup_mask || result.cb7_cleanup_mask){').replace('result.code==0x8023e)','result.code==0x8023e || result.code==0x80240)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('CR09 VBLANK BIT','CR07 VBLANK OVERFLOW')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=re.sub(r'\s+','',legacy.read_text());assert 'b=NvGetCrtc(pbRegs,7)&0xf7;NvSetCrtc(pbRegs,7,b|(((gpu->yres-1)>>5)&0x08));' in source
 target=K.parent/'xcal-transaction704/transaction003.c';types=K.parent/'xcal-transaction704/gpu_types.h'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','')
 assert re.findall(r'long\s+(\w+);',types.read_text())[:9]==['xres','crtchdispend','nvhstart','nvhtotal','yres','nvvstart','crtcvstart','crtcvtotal','nvvtotal']
 assert (54&0xf7)|(((480-1)>>5)&8)==62
 prior=read(O/'audit001.json');assert prior['passed'] and read(O/'closed001.json')['closed']
 assert [prior['result']['crtc_vblank_bit'][n] for n in ['before','after','restored']]==[96,64,96]
 assert prior['result']['crtc_vblank_bit']['neighbors_after'][1]==54
 native=K.parent/'native-vblank-bit801';assert read(native/'closed001.json')['closed'] and read(native/'audit001.json')['passed']
 assert not re.search(r'cw\((?:0x1b|0x22|0x33|0x15),',body)
 order=['cw(9,o->cb9_target)','cw(7,o->cb7_target)','cw(7,o->cb7_before)','cw(9,o->cb9_before)','cw(0x12,o->cd12_before)','cw(7,o->cd7_before)','cw(0x16,o->ct16_before)','cw(6,o->ct6_before)','cw(7,o->ct7_before)','cw(0x10,o->c10_before)','cw(7,o->c7_before)','gate(4)']
 assert [body.index(t) for t in order]==sorted(body.index(t) for t in order)
 assert 'o->cb7_target=(o->cb7_before&0xf7u)|(((480u-1u)>>5)&0x08u);' in body
 assert d['neighbors']==[['cb7_c6',6,12],['cb7_c9',9,64],['cb7_c10',16,233],['cb7_c12',18,223],['cb7_c15',21,207],['cb7_c16',22,140],['cb7_c18',24,255],['cb7_c25',37,16]]
 for n,a,v in d['neighbors']:
  assert 'o->'+n+'_before!='+hex(v) in d['block']
  assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model002.json');cases=model['cases'];assert model['passed'] and len(cases)==894
 for c in cases:
  try:validate(c['raw_result'])
  except AssertionError:raise AssertionError(('schema',c['name']))
 assert len(read(K/'clock-model002.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,700)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][675]:
   assert c['raw_result'][0]==0x80241 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[670:]==[54,62,1,62,54,0]+[a for n in [12,64,233,223,207,140,255,16] for a in [n]*3]
 byname={c['name']:c for c in cases}
 assert byname['cb7-drop-write']['raw_result'][1]==0x80240
 for n in ['cb7-drop-undo','cb7-wrong-undo','cb7-wrong-write-drop-undo']:
  assert [byname[n]['raw_result'][i] for i in [675,645,615,585,555,525,495,465,435]]==[1,4,4,0,0,0,0,0,0]
 checks=['build001.json','model002.json','layout-model001.json','clock-model002.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':700,'bytes':2800,'inherited':'0..669 same800; namespace802','new_fields':dict(zip(fields,range(670,700))),'new_statuses':{'80240':'baseline/forward/neighbor mismatch','80241':'own or neighbor recovery mismatch; output inhibited'},'target':62,'baseline':54,'native_requires_fresh_bounds_proof':True})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'target_types_sha256':sha(types),'target_derivation':'CR07 (36 & F7) | (((480-1)>>5)&08) =3E after CR09=40. Restore saved CR07 before CR09.','retained_kernel_sha256':sha(O/'audit001.json'),'retained_native_closure_sha256':sha(native/'closed001.json'),'prior_source_exact_after_removing_delta':True,'own_reverse_recovery':True,'all_894_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json','clock-lineage001.json','controller-review001.json','qualification-failure001.json','qualification-failure002.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=894,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes','.gitignore']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS802 independent source/schema/build review')
