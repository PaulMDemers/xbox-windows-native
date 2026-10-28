"""Independent source delta, word schema, source-order and frozen build review."""
from pathlib import Path
import ast,datetime,hashlib,json,re,struct
from audit_logic import validate,BASELINE,TARGET
K=Path(__file__).resolve().parent;O=K.parent/'crtc-stride-high766';P=Path('C:/xwn768/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
def ns(s):return re.sub(r'(?<![0-9])766(?![0-9])','768',re.sub(r'0x766(?=[0-9a-f]*\b)','0x768',s))
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review004.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c'
 assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 lines=legacy.read_text();a=lines.index('NvSetCrtc(pbRegs, 0x17, (NvGetCrtc(pbRegs, 0x17)&0x7f)|0x80);');b=lines.index('m=(gpu->xres / 8) * gpu->pixelDepth;',a);c=lines.index('NvSetCrtc(pbRegs, 0x19,',b);d=lines.index('NvSetCrtc(pbRegs, 0x13, (m & 0xff));',c);assert a<b<c<d
 target=K.parent/'xcal-transaction704/transaction003.c';assert '{720,720,738,779,480,489,489,524,524,4,3}' in target.read_text().replace(' ','')
 assert (720//8)*4==360 and ((360>>3)&224)==32 and (360&255)==104
 retained=K.parent/'native-crtc-stride767/collection001.json';rr=json.loads(retained.read_text());assert rr['completed']
 context=next(v['data'] for v in rr['reports'].values() if v['data']['phase']=='kernel_context_captured')
 assert [19,128] in context['crtc_kernel_reads'] and [25,81] in context['crtc_kernel_reads']
 assert json.loads((K.parent/'native-crtc-stride767/audit001.json').read_text())['passed']
 body=(K/'probe.c').read_text();delta=read('delta001.json');block=delta['block']
 assert 'o->c13_before=cr(0x13);o->c19_before_c13=cr(0x19);' in block
 assert 'if(o->c13_before!=o->c13_after_c19b || o->c19_before_c13!=o->c19b_after)goto restore;' in block
 assert 'o->c13_target=((720u/8u)*4u)&0xff;' in block
 assert 'o->c13_attempted=1;cw(0x13,(uint8_t)o->c13_target);' in block
 assert 'o->c19_after_c13!=o->c19_before_c13' in block and 'o->c17_after_c13!=o->c17b_target' in block
 assert all('o->c'+str(n)+'_after_c13' in block for n in range(6))
 stripped=body
 for token in [delta['init'],block,delta['undo'],' && !o->c13_cleanup_mask',' if(o->c13_cleanup_mask)o->code=0x76821;\n']:
  assert stripped.count(token)==1;stripped=stripped.replace(token,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['c13_before','c13_target','c13_attempted','c13_after','c13_restored','c13_cleanup_mask','c19_before_c13','c19_after_c13','c17_after_c13','c0_after_c13','c1_after_c13','c2_after_c13','c3_after_c13','c4_after_c13','c5_after_c13','c19_restored_c13']
 assert delta['fields']==fields
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 assert body.count('cw(0x13,')==2 and not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 assert body.index('cw(0x13,(uint8_t)o->c13_before)')<body.index('cw(0x19,(uint8_t)o->c19b_before)')<body.index('cw(0x17,(uint8_t)o->c17b_before)')<body.index('cw(0x19,(uint8_t)o->crtc_before[2])')<body.index('gate(4)')
 expected=ns((O/'main.c').read_text()).replace('crtc_stride_high_control','crtc_stride_low_control').replace('words[216]','words[232]').replace('i<216','i<232').replace('result.c19b_cleanup_mask){','result.c19b_cleanup_mask || result.c13_cleanup_mask){').replace('result.code==0x7681e)','result.code==0x7681e || result.code==0x76820)')
 assert (K/'main.c').read_text()==expected and 'frequency!=3375000' in expected
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 cases=read('model002.json')['cases'];assert read('model002.json')['passed'] and len(cases)==278 and len(read('clock-model002.json')['cases'])==10
 for c in cases:validate(c['raw_result'])
 save('schema-validation004.json',{'passed':True,'cases':len(cases),'validator_sha256':sha(K/'audit_logic.py'),'prefix_validator_sha256':sha(K/'prefix_schema.py'),'model_sha256':sha(K/'model002.json')})
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,232)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][221]:
   assert c['raw_result'][0]==0x76821 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe enable admitted')
 assert base[216:232]==[128,104,1,104,128,0,48,48,227,92,89,89,128,93,190,48]
 assert [v for v in cases[0]['writes'] if v[:2]==['cr',19]]==[['cr',19,104],['cr',19,128]]
 assert [v for v in cases[0]['writes'] if v[:2]==['cr',25]]==[['cr',25,16],['cr',25,48],['cr',25,16],['cr',25,81]]
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (P/n).read_bytes().count(table)==1
 save('schema004.json',{'words':232,'bytes':928,'inherited':'0..215 same766; namespace768','new_fields':dict(zip(fields,range(216,232))),'new_statuses':{'76820':'CR13 fresh-read/forward/neighbor mismatch','76821':'CR13 own recovery or CR19 preservation mismatch; inhibit output'},'CR13_target':104,'CR19_forward_target':48,'native_end_if_offset5100':0x54a0,'native_requires_fresh_bounds_proof':True})
 save('source-review004.json',{'passed':True,'legacy_sha256':sha(legacy),'target_source_sha256':sha(target),'retained_baseline_sha256':sha(retained),'source_order_verified':['CR17bit7enable','CR19strideHigh','CR13strideLow'],'prior_probe766_exact_after_removing_delta':True,'prior_main766_exact_except_namespace_length_status':True,'own_reverse_recovery':True,'fresh_capture_guarded_by_prior_read':True,'model_cases':278,'rejected_schema_mutations':mutations,'prior_kernel766_audit_sha256':sha(O/'audit001.json'),'prior_native767_audit_sha256':sha(K.parent/'native-crtc-stride767/audit001.json'),'result_bytes':928,'future_native_end_if_offset5100':0x54a0,'within_initialized5500':True,'native_requires_fresh_bounds_proof':True})
 checks=['build001.json','model002.json','layout-model002.json','clock-model002.json','link-review001.json','layout-link-review001.json','main-link-review001.json','schema-validation004.json','source-review004.json']
 assert all(read(n)['passed'] for n in checks);checks+=['schema004.json','lineage001.json','delta001.json','review001.json','review002.json','failure001.json','failure002.json','review003.json','failure003.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=278,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources004.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review004.json',r)
print('PASS768 source/schema/link review; CR13 low-byte and outer blank recovery')
