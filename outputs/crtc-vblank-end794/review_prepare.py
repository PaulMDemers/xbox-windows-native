"""Independent CR16 source, schema, cleanup and linked-build review. No console access."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vtotal-low792';P=Path('C:/xwn794/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return s.replace('792','794').replace('crtc-vtotal-low794','crtc-vblank-end794')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->ct16_cleanup_mask',' if(o->ct16_cleanup_mask)o->code=0x79439;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['ct16_before','ct16_target','ct16_attempted','ct16_after','ct16_restored','ct16_cleanup_mask']
 for n in ['ct16_c6','ct16_c7','ct16_c9','ct16_c10','ct16_c12','ct16_c15','ct16_c18','ct16_c25']:fields += [n+'_before',n+'_after',n+'_restored']
 assert fields==d['fields'] and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[550]','words[580]').replace('i<550','i<580').replace('crtc_vtotal_low_control','crtc_vblank_end_control').replace('result.ct6_cleanup_mask){','result.ct6_cleanup_mask || result.ct16_cleanup_mask){').replace('result.code==0x79436)','result.code==0x79436 || result.code==0x79438)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('CR06 VTOTAL LOW','CR16 VBLANK END')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=re.sub(r'\s+','',legacy.read_text());a=source.index('//CRTC_VBLANKEND');snippet=source[a:source.index('//CRTC_VDISPEND',a)]
 assert snippet=='//CRTC_VBLANKEND=CRTC_VTOTALb=NvGetCrtc(pbRegs,0x16)&0x80;NvSetCrtc(pbRegs,0x16,b|(gpu->crtcvtotal&0x7f));'
 target=K.parent/'xcal-transaction704/transaction003.c';types=K.parent/'xcal-transaction704/gpu_types.h'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','')
 assert re.findall(r'long\s+(\w+);',types.read_text())[:9]==['xres','crtchdispend','nvhstart','nvhtotal','yres','nvvstart','crtcvstart','crtcvtotal','nvvtotal']
 assert ((237&128)|(524&127))==140
 prior=read(O/'audit001.json');assert prior['passed'] and read(O/'closed001.json')['closed']
 assert [prior['result']['crtc_vtotal_low'][n] for n in ['before','after','restored']]==[236,12,236]
 native=K.parent/'native-vtotal-low793';assert read(native/'closed001.json')['closed'] and read(native/'audit001.json')['passed']
 crtc=next(v['data']['crtc_kernel_reads'] for v in read(O/'collection001.json')['reports'].values() if v['data'].get('crtc_kernel_reads'))
 assert [dict(crtc)[i] for i in [6,7,9,16,18,21,22,24,37]]==[236,240,96,212,207,207,237,255,16]
 assert body.count('cw(0x16,')==2 and not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 order=['cw(7,o->c7_target)','cw(0x10,o->c10_target)','cw(7,o->ct7_target)','cw(6,o->ct6_target)','cw(0x16,o->ct16_target)','cw(0x16,o->ct16_before)','cw(6,o->ct6_before)','cw(7,o->ct7_before)','cw(0x10,o->c10_before)','cw(7,o->c7_before)','R32(0x680818)=o->ve_before','R32(0x680810)=o->se_before','R32(0x68080c)=o->sy_before','R32(0x680814)=o->vs_before','R32(0x680808)=o->vc_before','R32(0x680804)=o->vt_before','R32(0x680800)=o->v_before','gate(4)']
 assert [body.index(t) for t in order]==sorted(body.index(t) for t in order)
 assert 'o->ct16_target=(o->ct16_before&0x80u)|(524u&0x7fu);' in body
 assert d['neighbors']==[['ct16_c6',6,12],['ct16_c7',7,116],['ct16_c9',9,96],['ct16_c10',16,233],['ct16_c12',18,207],['ct16_c15',21,207],['ct16_c18',24,255],['ct16_c25',37,16]]
 for n,a,v in d['neighbors']:
  assert 'o->'+n+'_before!='+hex(v) in d['block']
  assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model001.json');cases=model['cases'];assert model['passed'] and len(cases)==734
 for c in cases:
  try:validate(c['raw_result'])
  except AssertionError:raise AssertionError(('schema',c['name']))
 assert len(read(K/'clock-model001.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,580)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][555]:
   assert c['raw_result'][0]==0x79439 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[550:]==[237,140,1,140,237,0]+[a for n in [12,116,96,233,207,207,255,16] for a in [n]*3]
 assert [v for v in cases[0]['writes'] if v[0]=='cr' and v[1] in [6,7,16,22]]==[['cr',7,116],['cr',16,233],['cr',7,116],['cr',6,12],['cr',22,140],['cr',22,237],['cr',6,236],['cr',7,116],['cr',16,212],['cr',7,240]]
 byname={c['name']:c for c in cases}
 assert byname['ct16-drop-write']['raw_result'][1]==0x79438
 for n in ['ct16-drop-undo','ct16-wrong-undo','ct16-wrong-write-drop-undo']:
  v=byname[n]['raw_result'];assert [v[i] for i in [555,525,495,465,435]]==[1,64,64,64,64]
 for j,m in [(1,[2,0,0,0,0]),(2,[4,2,0,0,0]),(3,[8,4,4,8,4]),(4,[16,8,8,0,0])]:
  assert [byname['ct16-coupling-'+str(j)]['raw_result'][i] for i in [555,525,495,465,435]]==m
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':580,'bytes':2320,'inherited':'0..549 same792; namespace794','new_fields':dict(zip(fields,range(550,580))),'new_statuses':{'79438':'baseline/forward/neighbor mismatch','79439':'own or neighbor recovery mismatch; output inhibited'},'target':140,'baseline':237,'native_requires_fresh_bounds_proof':True})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'target_types_sha256':sha(types),'target_derivation':'(saved ED &80)|(crtcvtotal524 &7F) =8C after CR06=0C. CR16 restored first.','retained_kernel_sha256':sha(O/'audit001.json'),'retained_native_closure_sha256':sha(native/'closed001.json'),'prior_source_exact_after_removing_delta':True,'own_reverse_recovery':True,'all_734_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json','clock-lineage001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=734,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS794 independent source/schema/build review')
