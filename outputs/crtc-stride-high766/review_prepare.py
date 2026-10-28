"""Review source order, retained targets, raw schemas, exact build and frozen inputs."""
from pathlib import Path
import ast,datetime,hashlib,json,re,struct
from audit_logic import validate,BASELINE,TARGET
K=Path(__file__).resolve().parent;O=K.parent/'crtc-reenable764';P=Path('C:/xwn766/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
def ns(s):return re.sub(r'(?<![0-9])764(?![0-9])','766',re.sub(r'0x764(?=[0-9a-f]*\b)','0x766',s))
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 lines=legacy.read_text();a=lines.index('NvSetCrtc(pbRegs, 0x17, (NvGetCrtc(pbRegs, 0x17)&0x7f)|0x80);');b=lines.index('m=(gpu->xres / 8) * gpu->pixelDepth;',a);c=lines.index('NvSetCrtc(pbRegs, 0x19,',b);d=lines.index('NvSetCrtc(pbRegs, 0x13,',c);assert a<b<c<d
 target=K.parent/'xcal-transaction704/transaction003.c';assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','')
 retained=K.parent/'native-crtc-reenable765/collection001.json';rr=json.loads(retained.read_text());assert rr['completed']
 context=next(v['data'] for v in rr['reports'].values() if v['data']['phase']=='kernel_context_captured')
 assert [19,128] in context['crtc_kernel_reads'] and [25,81] in context['crtc_kernel_reads']
 assert (720//8)*4==360 and ((360>>3)&224)==32 and (360&255)==104
 body=(K/'probe.c').read_text()
 a=body.index(' /* Next original stride high bits:');b=body.index(' o->forward_status=0x766;\nrestore:',a);block=body[a:b]
 assert 'o->c19b_before=cr(0x19);o->c13_before_c19b=cr(0x13);' in block
 assert 'if(o->c19b_before!=o->crtc_checked[2] || o->c13_before_c19b!=0x80)goto restore;' in block
 assert 'o->c19b_target=(o->c19b_before&0x1f)|((((720u/8u)*4u)>>3)&0xe0);' in block
 assert 'o->c19b_attempted=1;cw(0x19,(uint8_t)o->c19b_target);' in block
 assert 'o->c13_after_c19b!=o->c13_before_c19b' in block and 'o->c17_after_c19b!=o->c17b_target' in block
 assert all('o->c'+str(n)+'_after_c19b' in block for n in range(6))
 stripped=body[:a]+body[b:]
 init=' o->c19b_after=o->c19b_restored=o->c13_after_c19b=o->c17_after_c19b=o->c0_after_c19b=o->c1_after_c19b=o->c2_after_c19b=o->c3_after_c19b=o->c4_after_c19b=o->c5_after_c19b=o->c13_restored_c19b=0xffffffff;\n'
 undo=' if(o->c19b_attempted){cw(0x19,(uint8_t)o->c19b_before);o->c19b_restored=cr(0x19);o->c13_restored_c19b=cr(0x13);if(o->c19b_restored!=o->c19b_before)o->c19b_cleanup_mask|=1;if(o->c13_restored_c19b!=o->c13_before_c19b)o->c19b_cleanup_mask|=2;}\n'
 for t in [init,undo,' && !o->c19b_cleanup_mask',' if(o->c19b_cleanup_mask)o->code=0x7661f;\n']:
  assert stripped.count(t)==1;stripped=stripped.replace(t,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['c19b_before','c19b_target','c19b_attempted','c19b_after','c19b_restored','c19b_cleanup_mask','c13_before_c19b','c13_after_c19b','c17_after_c19b','c0_after_c19b','c1_after_c19b','c2_after_c19b','c3_after_c19b','c4_after_c19b','c5_after_c19b','c13_restored_c19b']
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 assert body.index('cw(0x19,(uint8_t)o->c19b_before)')<body.index('cw(0x17,(uint8_t)o->c17b_before)')<body.index('cw(0x19,(uint8_t)o->crtc_before[2])')<body.index('gate(4)')
 assert not re.search(r'cw\((?:0x13|0x1b|0x22|0x33),',body)
 expected=ns((O/'main.c').read_text()).replace('crtc_reenable_control','crtc_stride_high_control').replace('words[200]','words[216]').replace('i<200','i<216').replace('result.c17b_cleanup_mask){','result.c17b_cleanup_mask || result.c19b_cleanup_mask){').replace('result.code==0x7661c)','result.code==0x7661c || result.code==0x7661e)')
 assert (K/'main.c').read_text()==expected and 'frequency!=3375000' in expected
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 assert not read('model001.json')['passed'] and read('model002.json')['passed']
 cases=read('model002.json')['cases'];assert len(cases)==253 and len(read('clock-model001.json')['cases'])==10
 for c in cases:validate(c['raw_result'])
 save('schema-validation001.json',{'passed':True,'cases':len(cases),'validator_sha256':sha(K/'audit_logic.py'),'prefix_validator_sha256':sha(K/'prefix_schema.py'),'model_sha256':sha(K/'model002.json')})
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,216)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][205]:
   assert c['raw_result'][0]==0x7661f and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe enable admitted')
 assert base[200:216]==[16,48,1,48,16,0,128,128,227,92,89,89,128,93,190,128]
 assert [v for v in cases[0]['writes'] if v[:2]==['cr',25]]==[['cr',25,16],['cr',25,48],['cr',25,16],['cr',25,81]]
 assert all(not any(w[:2]==['cr',19] for w in c['writes']) for c in cases)
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (P/n).read_bytes().count(table)==1
 save('schema001.json',{'words':216,'bytes':864,'inherited':'0..199 same764; namespace766','new_fields':dict(zip(fields,range(200,216))),'new_statuses':{'7661e':'CR19 fresh-read/forward/neighbor mismatch','7661f':'CR19 own recovery or CR13 preservation mismatch; inhibit output'},'CR19_target':48,'CR13_write':False})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'retained_baseline_sha256':sha(retained),'source_order_verified':['CR17bit7enable','CR19strideHigh'],'prior_probe764_exact_after_removing_delta':True,'prior_main764_exact_except_namespace_length_status':True,'own_reverse_recovery':True,'fresh_capture_guarded_by_prior_read':True,'model_cases':253,'rejected_schema_mutations':mutations,'prior_kernel764_audit_sha256':sha(O/'audit001.json'),'prior_native765_audit_sha256':sha(K.parent/'native-crtc-reenable765/audit001.json'),'result_bytes':864,'future_native_end_if_offset5100':0x5460,'within_initialized5500':True,'native_requires_fresh_bounds_proof':True})
 checks=['build001.json','model002.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','schema-validation001.json','source-review001.json']
 assert all(read(n)['passed'] for n in checks);checks+=['schema001.json','lineage001.json','failure001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=253,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS766 source/schema/link review; CR13 never written, outer blank preserved')
