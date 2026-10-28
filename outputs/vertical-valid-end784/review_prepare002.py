"""Independent784 source/delta, target, exact bytes, schema and fault review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'vertical-sync-end782';P=Path('C:/xwn784/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return s.replace('782','784').replace('vertical-sync-end784','vertical-valid-end784')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review002.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->ve_cleanup_mask',' if(o->ve_cleanup_mask)o->code=0x7842f;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['ve_before','ve_target','ve_attempted','ve_after','ve_restored','ve_cleanup_mask']
 for n in ['ve_disp','ve_total','ve_crtc','ve_validstart','ve_syncstart','ve_syncend','ve_c13','ve_c19']:fields += [n+'_before',n+'_after',n+'_restored']
 assert d['fields']==fields and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[400]','words[430]').replace('i<400','i<430').replace('vertical_sync_end_control','vertical_valid_end_control').replace('result.se_cleanup_mask){','result.se_cleanup_mask || result.ve_cleanup_mask){').replace('result.code==0x7842c)','result.code==0x7842c || result.code==0x7842e)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('NVVSYNCEND','NVVVALIDEND')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=legacy.read_text().replace(' ','');i=source.index('//NVVSYNCSTART');j=source.index('//CRTC_VSYNCSTART',i)
 assert '[0x680810])=(gpu->nvvstart+3);' in source[i:j] and '[0x680818])=gpu->yres-1;' in source[i:j]
 target=K.parent/'xcal-transaction704/transaction003.c';types=K.parent/'xcal-transaction704/gpu_types.h'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','') and '{0x680818,479}' in target.read_text()
 assert 480-1==479
 members=re.findall(r'long\s+(\w+);',types.read_text());assert members[:9]==['xres','crtchdispend','nvhstart','nvhtotal','yres','nvvstart','crtcvstart','crtcvtotal','nvvtotal']
 prior=read(O/'audit001.json');assert prior['passed']
 v=prior['result']['vertical_sync_end'];assert [v['before'],v['after'],v['restored']]==[729,492,729]
 assert v['neighbors_before']==v['neighbors_after']==v['neighbors_restored']==[479,524,479,0,489,719,104,48]
 native=K.parent/'native-sync-end783/closed001.json';assert read(native)['closed'] and read(K.parent/'native-sync-end783/audit005.json')['passed']
 for a in ['800','804','808','814','80c','810','818']:assert body.count('R32(0x680'+a+')=')==2
 assert not re.search(r'cw\((?:0x1b|0x22|0x33|0x07|0x7|0x10),',body)
 order=['R32(0x680818)=o->ve_before','R32(0x680810)=o->se_before','R32(0x68080c)=o->sy_before','R32(0x680814)=o->vs_before','R32(0x680808)=o->vc_before','R32(0x680804)=o->vt_before','R32(0x680800)=o->v_before','gate(4)']
 assert [body.index(t) for t in order]==sorted(body.index(t) for t in order)
 assert 'if(o->ve_before!=719 || o->ve_disp_before!=479 || o->ve_total_before!=524 || o->ve_crtc_before!=479 || o->ve_validstart_before!=0 || o->ve_syncstart_before!=489 || o->ve_syncend_before!=492 || o->ve_c13_before!=104 || o->ve_c19_before!=48)goto restore;' in body
 for n,_,_ in d['neighbors']:assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model001.json');cases=model['cases'];assert model['passed'] and len(cases)==536
 for c in cases:validate(c['raw_result'])
 assert len(read(K/'clock-model001.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,430)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][405]:
   assert c['raw_result'][0]==0x7842f and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[400:]==[719,479,1,479,719,0,479,479,479,524,524,524,479,479,479,0,0,0,489,489,489,492,492,492,104,104,104,48,48,48]
 assert [v for v in cases[0]['writes'] if v[0] in ['v','vt','vc','vs','sy','se','ve']]==[['v',0x680800,479],['vt',0x680804,524],['vc',0x680808,479],['vs',0x680814,0],['sy',0x68080c,489],['se',0x680810,492],['ve',0x680818,479],['ve',0x680818,719],['se',0x680810,729],['sy',0x68080c,724],['vs',0x680814,0],['vc',0x680808,719],['vt',0x680804,749],['v',0x680800,719]]
 assert next(c for c in cases if c['name']=='ve-drop-write')['raw_result'][0]==0x7842e
 assert next(c for c in cases if c['name']=='ve-drop-undo')['raw_result'][0]==0x7842f
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review002.json','layout-link-review002.json','main-link-review002.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':430,'bytes':1720,'inherited':'0..399 same782; namespace784','new_fields':dict(zip(fields,range(400,430))),'new_statuses':{'7842e':'baseline/forward/neighbor mismatch','7842f':'own or neighbor recovery mismatch; output inhibited'},'target':479,'baseline':719,'native_end_if_offset5100':0x57b8,'native_requires_fresh_bounds_proof':True})
 save('source-review002.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'target_types_sha256':sha(types),'target_derivation':'GPU_PARAMETER fifth field yres480-1=479; independent expected write {680818,479}; next source-order word after NVVSYNCEND','retained_kernel_sha256':sha(O/'audit001.json'),'retained_native_closure_sha256':sha(native),'prior_source_exact_after_removing_delta':True,'source_order':['NVVDISPEND','NVVTOTAL','NVVCRTC','NVVVALIDSTART','NVVSYNCSTART','NVVSYNCEND','NVVVALIDEND','stop before CRTC_VSYNCSTART CR7/10'],'own_reverse_recovery':True,'all_536_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow only; no physical semantics proof'})
 checks+=['schema001.json','source-review002.json','lineage001.json','delta001.json','clock-lineage001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=536,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review002.json',r)
print('PASS784 independent source/schema/build review')
