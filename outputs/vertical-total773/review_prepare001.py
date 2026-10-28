"""Independent source-order, source-delta, compiled-case/schema and build review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'vertical-display-end771';P=Path('C:/xwn773/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return re.sub(r'(?<![0-9])771(?![0-9])','773',re.sub(r'0x771(?=[0-9a-f]*\b)','0x773',s))
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->vt_cleanup_mask',' if(o->vt_cleanup_mask)o->code=0x77325;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['vt_before','vt_target','vt_attempted','vt_after','vt_restored','vt_cleanup_mask']
 for n in ['vt_disp','vt_syncstart','vt_syncend','vt_validend','vt_c13','vt_c19']:fields += [n+'_before',n+'_after',n+'_restored']
 assert d['fields']==fields and len(fields)==24
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[256]','words[280]').replace('i<256','i<280').replace('vertical_display_end_control','vertical_total_control').replace('result.v_cleanup_mask){','result.v_cleanup_mask || result.vt_cleanup_mask){').replace('result.code==0x77322)','result.code==0x77322 || result.code==0x77324)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('NVVDISPEND','NVVTOTAL')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=legacy.read_text();i=source.index('// NVVDISPEND');j=source.index('// NVVCRTC',i)
 assert re.search(r'\[0x680800\]\) = gpu->yres - 1;',source[i:j])
 assert re.search(r'\[0x680804\]\) = gpu->nvvtotal;',source[i:j])
 target=K.parent/'xcal-transaction704/transaction003.c'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','') and '{0x680804,524}' in target.read_text()
 retained=O/'audit001.json';rr=read(retained);assert rr['passed']
 previous=rr['result']['vertical_display_end'];assert [previous['before'],previous['after'],previous['restored']]==[719,479,719]
 assert previous['neighbors_after']==[749,724,729,719,104,48]
 assert body.count('R32(0x680804)=')==2 and body.count('R32(0x680800)=')==2
 assert not re.search(r'R32\(0x680(?:808|80c|810|814|818)\)\s*=',body)
 assert 'R32(0x680808)' not in body and 'R32(0x680814)' not in body
 assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 assert body.index('R32(0x680804)=o->vt_before')<body.index('R32(0x680800)=o->v_before')<body.index('cw(0x13,(uint8_t)o->c13_before)')<body.index('gate(4)')
 assert 'if(o->vt_before!=749 || o->vt_disp_before!=479 || o->vt_syncstart_before!=724 || o->vt_syncend_before!=729 || o->vt_validend_before!=719 || o->vt_c13_before!=104 || o->vt_c19_before!=48)goto restore;' in body
 for n in ['vt_disp','vt_syncstart','vt_syncend','vt_validend','vt_c13','vt_c19']:
  assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model001.json');cases=model['cases'];assert model['passed'] and len(cases)==340
 for c in cases:validate(c['raw_result'])
 assert len(read(K/'clock-model001.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,280)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][261]:
   assert c['raw_result'][0]==0x77325 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[256:]==[749,524,1,524,749,0,479,479,479,724,724,724,729,729,729,719,719,719,104,104,104,48,48,48]
 assert [v for v in cases[0]['writes'] if v[0] in ['v','vt']]==[['v',0x680800,479],['vt',0x680804,524],['vt',0x680804,749],['v',0x680800,719]]
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':280,'bytes':1120,'inherited':'0..255 same771; namespace773','new_fields':dict(zip(fields,range(256,280))),'new_statuses':{'77324':'fresh baseline/forward/neighbor mismatch','77325':'own or neighbor recovery mismatch; output inhibited'},'target':524,'baseline':749,'native_end_if_offset5100':0x5560,'native_requires_fresh_bounds_proof':True,'native772_zero_end5500_insufficient':True})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'retained_baseline_sha256':sha(retained),'prior_source_exact_after_removing_delta':True,'source_order':['NVVDISPEND','NVVTOTAL','stop before NVVCRTC680808'],'own_reverse_recovery':True,'all_340_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow evidence only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=340,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS773 independent source/schema/build review')
