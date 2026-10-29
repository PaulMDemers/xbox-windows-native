"""Independent790 source/target/recovery/schema/link review; no physical access."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vsync-low788';P=Path('C:/xwn790/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return s.replace('788','790').replace('crtc-vsync-low790','crtc-vtotal-high790')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->ct7_cleanup_mask',' if(o->ct7_cleanup_mask)o->code=0x79035;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['ct7_before','ct7_target','ct7_attempted','ct7_after','ct7_restored','ct7_cleanup_mask']
 for n in ['ct7_c6','ct7_c9','ct7_c10','ct7_c12','ct7_c15','ct7_c16','ct7_c18','ct7_c25']:fields += [n+'_before',n+'_after',n+'_restored']
 assert d['fields']==fields and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[490]','words[520]').replace('i<490','i<520').replace('crtc_vsync_low_control','crtc_vtotal_high_control').replace('result.c10_cleanup_mask){','result.c10_cleanup_mask || result.ct7_cleanup_mask){').replace('result.code==0x79032)','result.code==0x79032 || result.code==0x79034)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('CR10 VSYNC LOW','CR07 VTOTAL HIGH')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=re.sub(r'\s+','',legacy.read_text());a=source.index('//CRTC_VTOTAL');snippet=source[a:source.index('//CRTC_VBLANKEND',a)]
 assert snippet=='//CRTC_VTOTALb=NvGetCrtc(pbRegs,7)&0xde;NvSetCrtc(pbRegs,7,b|((gpu->crtcvtotal>>4)&0x20)|((gpu->crtcvtotal>>8)&0x01));NvSetCrtc(pbRegs,6,(gpu->crtcvtotal&0xff));'
 target=K.parent/'xcal-transaction704/transaction003.c';types=K.parent/'xcal-transaction704/gpu_types.h'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','')
 assert re.findall(r'long\s+(\w+);',types.read_text())[:9]==['xres','crtchdispend','nvhstart','nvhtotal','yres','nvvstart','crtcvstart','crtcvtotal','nvvtotal']
 assert (0x74&0xde)|((524>>4)&0x20)|((524>>8)&1)==0x74
 prior=read(O/'audit002.json');assert prior['passed'] and read(O/'closed001.json')['closed']
 assert [prior['result']['crtc_vsync_low'][n] for n in ['before','after','restored']]==[212,233,212]
 native=K.parent/'native-vsync-low789';assert read(native/'closed001.json')['closed'] and read(native/'audit006.json')['passed']
 crtc=next(v['data']['crtc_kernel_reads'] for v in read(O/'collection001.json')['reports'].values() if v['data'].get('crtc_kernel_reads'))
 assert [dict(crtc)[i] for i in [7,6,9,16,18,21,22,24,37]]==[240,236,96,212,207,207,237,255,16]
 for a in ['800','804','808','814','80c','810','818']:assert body.count('R32(0x680'+a+')=')==2
 assert body.count('cw(7,')==4 and body.count('cw(0x10,')==2
 assert not re.search(r'cw\((?:0x1b|0x22|0x33|0x07|0x06|6|0x16),',body)
 order=['cw(7,o->c7_target)','cw(0x10,o->c10_target)','cw(7,o->ct7_target)','cw(7,o->ct7_before)','cw(0x10,o->c10_before)','cw(7,o->c7_before)','R32(0x680818)=o->ve_before','R32(0x680810)=o->se_before','R32(0x68080c)=o->sy_before','R32(0x680814)=o->vs_before','R32(0x680808)=o->vc_before','R32(0x680804)=o->vt_before','R32(0x680800)=o->v_before','gate(4)']
 assert [body.index(t) for t in order]==sorted(body.index(t) for t in order)
 assert 'o->ct7_target=(o->ct7_before&0xdeu)|((524u>>4)&0x20u)|((524u>>8)&1u);' in body
 assert d['neighbors']==[['ct7_c6',6,236],['ct7_c9',9,96],['ct7_c10',16,233],['ct7_c12',18,207],['ct7_c15',21,207],['ct7_c16',22,237],['ct7_c18',24,255],['ct7_c25',37,16]]
 for n,a,v in d['neighbors']:
  assert 'o->'+n+'_before!='+hex(v) in d['block']
  assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model001.json');cases=model['cases'];assert model['passed'] and len(cases)==654
 for c in cases:
  try:validate(c['raw_result'])
  except AssertionError:raise AssertionError(('schema',c['name']))
 assert len(read(K/'clock-model001.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,520)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][495]:
   assert c['raw_result'][0]==0x79035 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[490:]==[116,116,1,116,116,0]+[a for n in [236,96,233,207,207,237,255,16] for a in [n]*3]
 assert [v for v in cases[0]['writes'] if v[0]=='cr' and v[1] in [7,16]]==[['cr',7,116],['cr',16,233],['cr',7,116],['cr',7,116],['cr',16,212],['cr',7,240]]
 byname={c['name']:c for c in cases}
 for n in ['ct7-drop-write','ct7-drop-undo']:assert byname[n]['raw_result']==base
 assert byname['ct7-wrong-write-drop-undo']['raw_result'][495]==1 and byname['ct7-wrong-write-drop-undo']['raw_result'][465]==4
 assert byname['ct7-coupling-3']['raw_result'][495]==8 and byname['ct7-coupling-3']['raw_result'][465]==byname['ct7-coupling-3']['raw_result'][435]==0
 for j,m in [(1,2),(2,8),(4,16),(5,32),(6,64),(7,128),(8,256)]:assert byname['ct7-coupling-'+str(j)]['raw_result'][465]==m
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':520,'bytes':2080,'inherited':'0..489 same788; namespace790','new_fields':dict(zip(fields,range(490,520))),'new_statuses':{'79034':'baseline/forward/neighbor mismatch','79035':'own or neighbor recovery mismatch; output inhibited'},'target':116,'baseline':116,'same_value_drop_indistinguishable':True,'native_requires_fresh_bounds_proof':True,'native_warning':'No native payload created/admitted; previous789 result ended5fe8 with24bytes before IDT6000. New result adds120bytes; fresh layout required.'})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'target_types_sha256':sha(types),'target_derivation':'crtcvtotal524, CR07=(74&DE)|20|00=74 afterCR10=E9. Own saved-value reverse beforeCR10 then earlierCR07. Same-value writes cannot prove transition.','retained_kernel_sha256':sha(O/'audit002.json'),'retained_native_closure_sha256':sha(native/'closed001.json'),'prior_source_exact_after_removing_delta':True,'own_reverse_recovery':True,'all_654_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json','clock-lineage001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=654,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS790 independent source/schema/build review')
