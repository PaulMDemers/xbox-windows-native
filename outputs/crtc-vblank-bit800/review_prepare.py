"""Review source delta, independent literals, recovery, and actual compiled evidence."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vdisplay-low798';P=Path('C:/xwn800/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return s.replace('798','800').replace('crtc-vdisplay-low800','crtc-vblank-bit800')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->cb9_cleanup_mask',' if(o->cb9_cleanup_mask)o->code=0x8003f;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['cb9_before','cb9_target','cb9_attempted','cb9_after','cb9_restored','cb9_cleanup_mask']
 for n in ['cb9_c6','cb9_c7','cb9_c10','cb9_c12','cb9_c15','cb9_c16','cb9_c18','cb9_c25']:fields += [n+'_before',n+'_after',n+'_restored']
 assert fields==d['fields'] and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[640]','words[670]').replace('i<640','i<670').replace('crtc_vdisplay_low_control','crtc_vblank_bit_control').replace('result.cd12_cleanup_mask){','result.cd12_cleanup_mask || result.cb9_cleanup_mask){').replace('result.code==0x8003c)','result.code==0x8003c || result.code==0x8003e)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('CR12 VDISPLAY LOW','CR09 VBLANK BIT')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=re.sub(r'\s+','',legacy.read_text());assert 'b=NvGetCrtc(pbRegs,9)&0xdf;NvSetCrtc(pbRegs,9,b|(((gpu->yres-1)>>4)&0x20));' in source
 target=K.parent/'xcal-transaction704/transaction003.c';types=K.parent/'xcal-transaction704/gpu_types.h'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','')
 assert re.findall(r'long\s+(\w+);',types.read_text())[:9]==['xres','crtchdispend','nvhstart','nvhtotal','yres','nvvstart','crtcvstart','crtcvtotal','nvvtotal']
 assert (96&0xdf)|(((480-1)>>4)&0x20)==64
 prior=read(O/'audit002.json');assert prior['passed'] and read(O/'closed001.json')['closed']
 assert [prior['result']['crtc_vdisplay_low'][n] for n in ['before','after','restored']]==[207,223,207]
 assert prior['result']['crtc_vdisplay_low']['neighbors_after'][2]==96
 native=K.parent/'native-vdisplay-low799';assert read(native/'closed001.json')['closed'] and read(native/'audit001.json')['passed']
 assert not re.search(r'cw\((?:0x1b|0x22|0x33|0x15),',body)
 order=['cw(0x12,o->cd12_target)','cw(9,o->cb9_target)','cw(9,o->cb9_before)','cw(0x12,o->cd12_before)','cw(7,o->cd7_before)','cw(0x16,o->ct16_before)','cw(6,o->ct6_before)','cw(7,o->ct7_before)','cw(0x10,o->c10_before)','cw(7,o->c7_before)','gate(4)']
 assert [body.index(t) for t in order]==sorted(body.index(t) for t in order)
 assert 'o->cb9_target=(o->cb9_before&0xdfu)|(((480u-1u)>>4)&0x20u);' in body
 assert d['neighbors']==[['cb9_c6',6,12],['cb9_c7',7,54],['cb9_c10',16,233],['cb9_c12',18,223],['cb9_c15',21,207],['cb9_c16',22,140],['cb9_c18',24,255],['cb9_c25',37,16]]
 for n,a,v in d['neighbors']:
  assert 'o->'+n+'_before!='+hex(v) in d['block']
  assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model001.json');cases=model['cases'];assert model['passed'] and len(cases)==854
 for c in cases:
  try:validate(c['raw_result'])
  except AssertionError:raise AssertionError(('schema',c['name']))
 assert len(read(K/'clock-model001.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,670)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][645]:
   assert c['raw_result'][0]==0x8003f and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[640:]==[96,64,1,64,96,0]+[a for n in [12,54,233,223,207,140,255,16] for a in [n]*3]
 byname={c['name']:c for c in cases}
 assert byname['cb9-drop-write']['raw_result'][1]==0x8003e
 for n in ['cb9-drop-undo','cb9-wrong-undo','cb9-wrong-write-drop-undo']:
  assert [byname[n]['raw_result'][i] for i in [645,615,585,555,525,495,465,435]]==[1,8,4,8,4,4,8,4]
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':670,'bytes':2680,'inherited':'0..639 same798; namespace800','new_fields':dict(zip(fields,range(640,670))),'new_statuses':{'8003e':'baseline/forward/neighbor mismatch','8003f':'own or neighbor recovery mismatch; output inhibited'},'target':64,'baseline':96,'native_requires_fresh_bounds_proof':True})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'target_types_sha256':sha(types),'target_derivation':'CR09 (60 & DF) | (((480-1)>>4)&20) =40 after CR12=DF. Restore saved CR09 before CR12.','retained_kernel_sha256':sha(O/'audit002.json'),'retained_native_closure_sha256':sha(native/'closed001.json'),'prior_source_exact_after_removing_delta':True,'own_reverse_recovery':True,'all_854_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json','clock-lineage001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=854,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes','.gitignore']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS800 independent source/schema/build review')
