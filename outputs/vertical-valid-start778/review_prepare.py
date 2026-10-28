"""Independent778 source-order, exact delta, actual-code and schema review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'vertical-crtc776';P=Path('C:/xwn778/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return re.sub(r'(?<![0-9])776(?![0-9])','778',re.sub(r'0x776(?=[0-9a-f]*\b)','0x778',s))
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->vs_cleanup_mask',' if(o->vs_cleanup_mask)o->code=0x77829;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['vs_before','vs_target','vs_attempted','vs_after','vs_restored','vs_cleanup_mask']
 for n in ['vs_disp','vs_total','vs_crtc','vs_syncstart','vs_syncend','vs_validend','vs_c13','vs_c19']:fields += [n+'_before',n+'_after',n+'_restored']
 assert d['fields']==fields and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[310]','words[340]').replace('i<310','i<340').replace('vertical_crtc_control','vertical_valid_start_control').replace('result.vc_cleanup_mask){','result.vc_cleanup_mask || result.vs_cleanup_mask){').replace('result.code==0x77826)','result.code==0x77826 || result.code==0x77828)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('NVVCRTC','NVVVALIDSTART')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=legacy.read_text();i=source.index('// NVVCRTC');j=source.index('// NVVSYNCSTART',i)
 assert '[0x680808]) = gpu->yres - 1;' in source[i:j] and '[0x680814]) = 0;' in source[i:j]
 prior=read(O/'audit001.json');assert prior['passed']
 v=prior['result']['vertical_crtc'];assert [v['before'],v['after'],v['restored']]==[719,479,719]
 assert v['neighbors_before']==v['neighbors_after']==v['neighbors_restored']==[479,524,724,729,0,719,104,48]
 native=K.parent/'native-vertical-crtc777/audit004.json';nr=read(native);assert nr['passed'] and nr['native_NVVCRTC_before_after_restored']==[719,479,719]
 for a in ['800','804','808','814']:assert body.count('R32(0x680'+a+')=')==2
 assert not re.search(r'R32\(0x680(?:80c|810|818)\)\s*=',body)
 assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 assert body.index('R32(0x680814)=o->vs_before')<body.index('R32(0x680808)=o->vc_before')<body.index('R32(0x680804)=o->vt_before')<body.index('R32(0x680800)=o->v_before')<body.index('gate(4)')
 assert 'if(o->vs_before!=0 || o->vs_disp_before!=479 || o->vs_total_before!=524 || o->vs_crtc_before!=479 || o->vs_syncstart_before!=724 || o->vs_syncend_before!=729 || o->vs_validend_before!=719 || o->vs_c13_before!=104 || o->vs_c19_before!=48)goto restore;' in body
 for n,_,_ in d['neighbors']:assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model001.json');cases=model['cases'];assert model['passed'] and len(cases)==419
 for c in cases:validate(c['raw_result'])
 assert len(read(K/'clock-model001.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,340)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][315]:
   assert c['raw_result'][0]==0x77829 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[310:]==[0,0,1,0,0,0,479,479,479,524,524,524,479,479,479,724,724,724,729,729,729,719,719,719,104,104,104,48,48,48]
 assert [v for v in cases[0]['writes'] if v[0] in ['v','vt','vc','vs']]==[['v',0x680800,479],['vt',0x680804,524],['vc',0x680808,479],['vs',0x680814,0],['vs',0x680814,0],['vc',0x680808,719],['vt',0x680804,749],['v',0x680800,719]]
 for label in ['vs-drop-write','vs-drop-undo']:
  c=next(c for c in cases if c['name']==label);assert c['raw_result']==base and c['raw_result'][0]==0x778
 bad=next(c for c in cases if c['name']=='vs-wrong-write-drop-undo');assert bad['raw_result'][0]==0x77829 and bad['raw_result'][315]==1 and bad['raw_result'][285]==32
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':340,'bytes':1360,'inherited':'0..309 same776; namespace778','new_fields':dict(zip(fields,range(310,340))),'new_statuses':{'77828':'baseline/forward/neighbor mismatch','77829':'own or neighbor recovery mismatch; output inhibited'},'target':0,'baseline':0,'same_value_drop_indistinguishable':True,'native_end_if_offset5100':0x5650,'native_requires_fresh_bounds_proof':True})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'retained_kernel_sha256':sha(O/'audit001.json'),'retained_native_sha256':sha(native),'prior_source_exact_after_removing_delta':True,'source_order':['NVVDISPEND','NVVTOTAL','NVVCRTC','NVVVALIDSTART','stop before NVVSYNCSTART68080c'],'own_reverse_recovery':True,'all_419_schema_cases_pass':True,'same_value_drop_write_and_undo_match_success':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json','preparation-failure001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=419,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS778 independent source/schema/build review')
