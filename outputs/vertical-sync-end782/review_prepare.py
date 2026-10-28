"""Independent782 source/delta, target, exact bytes, schema and fault review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'vertical-sync-start780';P=Path('C:/xwn782/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return s.replace('780','782').replace('vertical-sync-start782','vertical-sync-end782')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->se_cleanup_mask',' if(o->se_cleanup_mask)o->code=0x7822d;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['se_before','se_target','se_attempted','se_after','se_restored','se_cleanup_mask']
 for n in ['se_disp','se_total','se_crtc','se_validstart','se_syncstart','se_validend','se_c13','se_c19']:fields += [n+'_before',n+'_after',n+'_restored']
 assert d['fields']==fields and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[370]','words[400]').replace('i<370','i<400').replace('vertical_sync_start_control','vertical_sync_end_control').replace('result.sy_cleanup_mask){','result.sy_cleanup_mask || result.se_cleanup_mask){').replace('result.code==0x7822a)','result.code==0x7822a || result.code==0x7822c)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('NVVSYNCSTART','NVVSYNCEND')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=legacy.read_text();i=source.index('// NVVSYNCSTART');j=source.index('// NVVVALIDEND',i)
 assert '[0x68080c])=gpu->nvvstart;' in source[i:j] and '[0x680810])=(gpu->nvvstart+3);' in source[i:j]
 target=K.parent/'xcal-transaction704/transaction003.c';types=K.parent/'xcal-transaction704/gpu_types.h'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','') and '{0x680810,492}' in target.read_text()
 assert 489+3==492
 members=re.findall(r'long\s+(\w+);',types.read_text());assert members[:9]==['xres','crtchdispend','nvhstart','nvhtotal','yres','nvvstart','crtcvstart','crtcvtotal','nvvtotal']
 prior=read(O/'audit001.json');assert prior['passed']
 v=prior['result']['vertical_sync_start'];assert [v['before'],v['after'],v['restored']]==[724,489,724]
 assert v['neighbors_before']==v['neighbors_after']==v['neighbors_restored']==[479,524,479,0,729,719,104,48]
 native=K.parent/'native-sync-start781/closed001.json';assert read(native)['closed'] and read(K.parent/'native-sync-start781/audit005.json')['passed']
 for a in ['800','804','808','814','80c','810']:assert body.count('R32(0x680'+a+')=')==2
 assert not re.search(r'R32\(0x680818\)\s*=',body)
 assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 order=['R32(0x680810)=o->se_before','R32(0x68080c)=o->sy_before','R32(0x680814)=o->vs_before','R32(0x680808)=o->vc_before','R32(0x680804)=o->vt_before','R32(0x680800)=o->v_before','gate(4)']
 assert [body.index(t) for t in order]==sorted(body.index(t) for t in order)
 assert 'if(o->se_before!=729 || o->se_disp_before!=479 || o->se_total_before!=524 || o->se_crtc_before!=479 || o->se_validstart_before!=0 || o->se_syncstart_before!=489 || o->se_validend_before!=719 || o->se_c13_before!=104 || o->se_c19_before!=48)goto restore;' in body
 for n,_,_ in d['neighbors']:assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model001.json');cases=model['cases'];assert model['passed'] and len(cases)==497
 for c in cases:validate(c['raw_result'])
 assert len(read(K/'clock-model001.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,400)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][375]:
   assert c['raw_result'][0]==0x7822d and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[370:]==[729,492,1,492,729,0,479,479,479,524,524,524,479,479,479,0,0,0,489,489,489,719,719,719,104,104,104,48,48,48]
 assert [v for v in cases[0]['writes'] if v[0] in ['v','vt','vc','vs','sy','se']]==[['v',0x680800,479],['vt',0x680804,524],['vc',0x680808,479],['vs',0x680814,0],['sy',0x68080c,489],['se',0x680810,492],['se',0x680810,729],['sy',0x68080c,724],['vs',0x680814,0],['vc',0x680808,719],['vt',0x680804,749],['v',0x680800,719]]
 assert next(c for c in cases if c['name']=='se-drop-write')['raw_result'][0]==0x7822c
 assert next(c for c in cases if c['name']=='se-drop-undo')['raw_result'][0]==0x7822d
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':400,'bytes':1600,'inherited':'0..369 same780; namespace782','new_fields':dict(zip(fields,range(370,400))),'new_statuses':{'7822c':'baseline/forward/neighbor mismatch','7822d':'own or neighbor recovery mismatch; output inhibited'},'target':492,'baseline':729,'native_end_if_offset5100':0x5740,'native_requires_fresh_bounds_proof':True})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'target_types_sha256':sha(types),'target_derivation':'GPU_PARAMETER sixth field nvvstart489+3=492; independent expected write {680810,492}; next source-order word after NVVSYNCSTART','retained_kernel_sha256':sha(O/'audit001.json'),'retained_native_closure_sha256':sha(native),'prior_source_exact_after_removing_delta':True,'source_order':['NVVDISPEND','NVVTOTAL','NVVCRTC','NVVVALIDSTART','NVVSYNCSTART','NVVSYNCEND','stop before NVVVALIDEND680818'],'own_reverse_recovery':True,'all_497_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json','clock-lineage001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=497,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS782 independent source/schema/build review')
