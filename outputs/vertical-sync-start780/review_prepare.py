"""Independent780 source/delta, pinned target, execution/schema and build review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'vertical-valid-start778';P=Path('C:/xwn780/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return s.replace('778','780').replace('vertical-valid-start780','vertical-sync-start780')
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->sy_cleanup_mask',' if(o->sy_cleanup_mask)o->code=0x7802b;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['sy_before','sy_target','sy_attempted','sy_after','sy_restored','sy_cleanup_mask']
 for n in ['sy_disp','sy_total','sy_crtc','sy_validstart','sy_syncend','sy_validend','sy_c13','sy_c19']:fields += [n+'_before',n+'_after',n+'_restored']
 assert d['fields']==fields and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[340]','words[370]').replace('i<340','i<370').replace('vertical_valid_start_control','vertical_sync_start_control').replace('result.vs_cleanup_mask){','result.vs_cleanup_mask || result.sy_cleanup_mask){').replace('result.code==0x78028)','result.code==0x78028 || result.code==0x7802a)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('NVVVALIDSTART','NVVSYNCSTART')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=legacy.read_text();i=source.index('// NVVVALIDSTART');j=source.index('// NVVSYNCEND',i)
 assert '[0x680814]) = 0;' in source[i:j] and '[0x68080c])=gpu->nvvstart;' in source[i:j]
 target=K.parent/'xcal-transaction704/transaction003.c';types=K.parent/'xcal-transaction704/gpu_types.h'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','') and '{0x68080c,489}' in target.read_text()
 members=re.findall(r'long\s+(\w+);',types.read_text());assert members[:9]==['xres','crtchdispend','nvhstart','nvhtotal','yres','nvvstart','crtcvstart','crtcvtotal','nvvtotal']
 prior=read(O/'audit002.json');assert prior['passed']
 v=prior['result']['vertical_valid_start'];assert [v['before'],v['after'],v['restored']]==[0,0,0]
 assert v['neighbors_before']==v['neighbors_after']==v['neighbors_restored']==[479,524,479,724,729,719,104,48]
 native=K.parent/'native-valid-start779/closed001.json';assert read(native)['closed'] and read(K.parent/'native-valid-start779/audit004.json')['passed']
 for a in ['800','804','808','814','80c']:assert body.count('R32(0x680'+a+')=')==2
 assert not re.search(r'R32\(0x680(?:810|818)\)\s*=',body)
 assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 assert body.index('R32(0x68080c)=o->sy_before')<body.index('R32(0x680814)=o->vs_before')<body.index('R32(0x680808)=o->vc_before')<body.index('R32(0x680804)=o->vt_before')<body.index('R32(0x680800)=o->v_before')<body.index('gate(4)')
 assert 'if(o->sy_before!=724 || o->sy_disp_before!=479 || o->sy_total_before!=524 || o->sy_crtc_before!=479 || o->sy_validstart_before!=0 || o->sy_syncend_before!=729 || o->sy_validend_before!=719 || o->sy_c13_before!=104 || o->sy_c19_before!=48)goto restore;' in body
 for n,_,_ in d['neighbors']:assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model001.json');cases=model['cases'];assert model['passed'] and len(cases)==458
 for c in cases:validate(c['raw_result'])
 assert len(read(K/'clock-model002.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,370)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][345]:
   assert c['raw_result'][0]==0x7802b and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[340:]==[724,489,1,489,724,0,479,479,479,524,524,524,479,479,479,0,0,0,729,729,729,719,719,719,104,104,104,48,48,48]
 assert [v for v in cases[0]['writes'] if v[0] in ['v','vt','vc','vs','sy']]==[['v',0x680800,479],['vt',0x680804,524],['vc',0x680808,479],['vs',0x680814,0],['sy',0x68080c,489],['sy',0x68080c,724],['vs',0x680814,0],['vc',0x680808,719],['vt',0x680804,749],['v',0x680800,719]]
 assert next(c for c in cases if c['name']=='sy-drop-write')['raw_result'][0]==0x7802a
 assert next(c for c in cases if c['name']=='sy-drop-undo')['raw_result'][0]==0x7802b
 checks=['build001.json','model001.json','layout-model001.json','clock-model002.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':370,'bytes':1480,'inherited':'0..339 same778; namespace780','new_fields':dict(zip(fields,range(340,370))),'new_statuses':{'7802a':'baseline/forward/neighbor mismatch','7802b':'own or neighbor recovery mismatch; output inhibited'},'target':489,'baseline':724,'native_end_if_offset5100':0x56c8,'native_requires_fresh_bounds_proof':True})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'target_types_sha256':sha(types),'target_derivation':'GPU_PARAMETER sixth field nvvstart=489; independent expected write {68080c,489}; next source-order word after NVVVALIDSTART','retained_kernel_sha256':sha(O/'audit002.json'),'retained_native_closure_sha256':sha(native),'prior_source_exact_after_removing_delta':True,'source_order':['NVVDISPEND','NVVTOTAL','NVVCRTC','NVVVALIDSTART','NVVSYNCSTART','stop before NVVSYNCEND680810'],'own_reverse_recovery':True,'all_458_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json','host-invocation-failure001.json','clock-model001.json','clock-lineage002.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=458,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS780 independent source/schema/build review')
