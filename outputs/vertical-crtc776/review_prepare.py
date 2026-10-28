"""Independent source-order/delta, actual COFF/schema and linked build review."""
from pathlib import Path
import ast,datetime,hashlib,json,re
from audit_logic import validate
K=Path(__file__).resolve().parent;O=K.parent/'vertical-total773';P=Path('C:/xwn776/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s):return re.sub(r'(?<![0-9])773(?![0-9])','776',re.sub(r'0x773(?=[0-9a-f]*\b)','0x776',s))
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 d=read(K/'delta001.json');body=(K/'probe.c').read_text();stripped=body
 for token in [d['init'],d['block'],d['undo'],' && !o->vc_cleanup_mask',' if(o->vc_cleanup_mask)o->code=0x77627;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['vc_before','vc_target','vc_attempted','vc_after','vc_restored','vc_cleanup_mask']
 for n in ['vc_disp','vc_total','vc_syncstart','vc_syncend','vc_validstart','vc_validend','vc_c13','vc_c19']:fields += [n+'_before',n+'_after',n+'_restored']
 assert d['fields']==fields and len(fields)==30
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 expected=ns((O/'main.c').read_text()).replace('words[280]','words[310]').replace('i<280','i<310').replace('vertical_total_control','vertical_crtc_control').replace('result.vt_cleanup_mask){','result.vt_cleanup_mask || result.vc_cleanup_mask){').replace('result.code==0x77624)','result.code==0x77624 || result.code==0x77626)')
 assert (K/'main.c').read_text()==expected
 assert (K/'Makefile').read_text()==ns((O/'Makefile').read_text()).replace('NVVTOTAL','NVVCRTC')
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=legacy.read_text();i=source.index('// NVVTOTAL');j=source.index('// NVVVALIDSTART',i)
 assert re.search(r'\[0x680804\]\) = gpu->nvvtotal;',source[i:j]) and re.search(r'\[0x680808\]\) = gpu->yres - 1;',source[i:j])
 target=K.parent/'xcal-transaction704/transaction003.c'
 assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','') and '{0x680808,479}' in target.read_text()
 retained=O/'audit002.json';rr=read(retained);assert rr['passed']
 previous=rr['result']['vertical_total'];assert [previous['before'],previous['after'],previous['restored']]==[749,524,749]
 physical=K.parent/'vertical-read775/audit001.json';br=read(physical);assert br['passed']
 assert br['result']['first']==br['result']['second']==br['result']['third']==[719,749,719,724,729,0,719]
 for a in ['800','804','808']:assert body.count('R32(0x680'+a+')=')==2
 assert not re.search(r'R32\(0x680(?:80c|810|814|818)\)\s*=',body)
 assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 assert body.index('R32(0x680808)=o->vc_before')<body.index('R32(0x680804)=o->vt_before')<body.index('R32(0x680800)=o->v_before')<body.index('cw(0x13,(uint8_t)o->c13_before)')<body.index('gate(4)')
 assert 'if(o->vc_before!=719 || o->vc_disp_before!=479 || o->vc_total_before!=524 || o->vc_syncstart_before!=724 || o->vc_syncend_before!=729 || o->vc_validstart_before!=0 || o->vc_validend_before!=719 || o->vc_c13_before!=104 || o->vc_c19_before!=48)goto restore;' in body
 for n,_,_ in d['neighbors']:
  assert 'o->'+n+'_after!=o->'+n+'_before' in d['block'] and 'o->'+n+'_restored!=o->'+n+'_before' in d['undo']
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 model=read(K/'model001.json');cases=model['cases'];assert model['passed'] and len(cases)==379
 for c in cases:validate(c['raw_result'])
 assert len(read(K/'clock-model001.json')['cases'])==10 and read(K/'layout-model001.json')['case_count']==2353
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,310)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][285]:
   assert c['raw_result'][0]==0x77627 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe output enable admitted')
 assert base[280:]==[719,479,1,479,719,0,479,479,479,524,524,524,724,724,724,729,729,729,0,0,0,719,719,719,104,104,104,48,48,48]
 assert [v for v in cases[0]['writes'] if v[0] in ['v','vt','vc']]==[['v',0x680800,479],['vt',0x680804,524],['vc',0x680808,479],['vc',0x680808,719],['vt',0x680804,749],['v',0x680800,719]]
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 save('schema001.json',{'words':310,'bytes':1240,'inherited':'0..279 same773; namespace776','new_fields':dict(zip(fields,range(280,310))),'new_statuses':{'77626':'fresh baseline/forward/neighbor mismatch','77627':'own or neighbor recovery mismatch; output inhibited'},'target':479,'baseline':719,'native_end_if_offset5100':0x55d8,'native_requires_fresh_bounds_proof':True,'native774_zero_end5560_insufficient':True})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'retained_prefix_sha256':sha(retained),'physical_readonly_baseline_sha256':sha(physical),'prior_source_exact_after_removing_delta':True,'source_order':['NVVDISPEND','NVVTOTAL','NVVCRTC','stop before NVVVALIDSTART680814'],'own_reverse_recovery':True,'all_379_schema_cases_pass':True,'rejected_schema_mutations':mutations,'scope':'host access/control-flow evidence only; no physical semantics proof'})
 checks+=['schema001.json','source-review001.json','lineage001.json','delta001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=379,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS776 independent source/schema/build review')
