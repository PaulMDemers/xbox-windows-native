"""Independent source/order/schema review and frozen source admission for764."""
from pathlib import Path
import ast,datetime,hashlib,json,re,struct
from audit_logic import validate,BASELINE,TARGET
K=Path(__file__).resolve().parent;O=K.parent/'crtc-repeat-blank762';P=Path('C:/xwn764/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
def ns(s):return re.sub(r'(?<![0-9])762(?![0-9])','764',re.sub(r'0x762(?=[0-9a-f]*\b)','0x764',s))
def save(n,r):
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'reviewer_sha256':sha(Path(__file__))};assert not (K/'review001.json').exists()
try:
 for f in K.glob('*.py'):ast.parse(f.read_text())
 legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 lines=legacy.read_text();a=lines.index('NvSetCrtc(pbRegs, 1, ((gpu->crtchdispend)/8)-1);');b=lines.index('NvSetCrtc(pbRegs, 2, ((gpu->crtchdispend)/8)-1);',a);c=lines.index('NvSetCrtc(pbRegs, 0x17, (NvGetCrtc(pbRegs, 0x17)&0x7f)|0x80);',b);assert a<b<c
 body=(K/'probe.c').read_text()
 block=''' /* Original next CR17 RMW: set bit7, fresh own value under outer blank. */
 o->forward_status=0x7641c;o->c17b_before=cr(0x17);
 if(o->c17b_before!=o->c17_after_c2b)goto restore;
 o->c17b_target=(o->c17b_before&0x7f)|0x80;o->c17b_attempted=1;cw(0x17,(uint8_t)o->c17b_target);
 o->c17b_after=cr(0x17);o->c0_after_c17b=cr(0);o->c1_after_c17b=cr(1);o->c2_after_c17b=cr(2);o->c3_after_c17b=cr(3);o->c4_after_c17b=cr(4);o->c5_after_c17b=cr(5);
 if(o->c17b_after!=o->c17b_target || o->c0_after_c17b!=o->c0_target || o->c1_after_c17b!=o->c1_target || o->c2_after_c17b!=o->c2b_target || o->c3_after_c17b!=o->c3_target || o->c4_after_c17b!=93 || o->c5_after_c17b!=o->c5b_target)goto restore;
'''
 assert body.count(block)==1;stripped=body.replace(block,'')
 for t in [' o->c17b_after=o->c17b_restored=o->c0_after_c17b=o->c1_after_c17b=o->c2_after_c17b=o->c3_after_c17b=o->c4_after_c17b=o->c5_after_c17b=0xffffffff;\n',' if(o->c17b_attempted){cw(0x17,(uint8_t)o->c17b_before);o->c17b_restored=cr(0x17);if(o->c17b_restored!=o->c17b_before)o->c17b_cleanup_mask=1;}\n',' && !o->c17b_cleanup_mask',' if(o->c17b_cleanup_mask)o->code=0x7641d;\n']:
  assert stripped.count(t)==1;stripped=stripped.replace(t,'')
 assert stripped==ns((O/'probe.c').read_text())
 fields=['c17b_before','c17b_target','c17b_attempted','c17b_after','c17b_restored','c17b_cleanup_mask','c0_after_c17b','c1_after_c17b','c2_after_c17b','c3_after_c17b','c4_after_c17b','c5_after_c17b']
 assert (K/'probe.h').read_text().replace(' uint32_t '+','.join(fields)+';\n','')==ns((O/'probe.h').read_text())
 order=['cw(0x17,(uint8_t)o->c17b_before)','cw(2,(uint8_t)o->c2b_before)','cw(1,(uint8_t)o->c1_before)','cw(0x17,(uint8_t)o->c17_before)','cw(5,(uint8_t)o->c5b_before)','cw(3,(uint8_t)o->c3_before)','cw(2,(uint8_t)o->c2_before)','cw(0,(uint8_t)o->c0_before)','cw(5,(uint8_t)o->c5_before)','cw(4,(uint8_t)o->c4_before)','R32(horizontal[i-1][0])=o->h_before[i-1]','gate(4)']
 assert [body.index(v) for v in order]==sorted(body.index(v) for v in order)
 assert len(re.findall(r'cw\(0x17,',body))==4 and not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 expected=ns((O/'main.c').read_text()).replace('crtc_repeat_blank_control','crtc_reenable_control').replace('words[188]','words[200]').replace('i<188','i<200').replace('result.c2b_cleanup_mask){','result.c2b_cleanup_mask || result.c17b_cleanup_mask){').replace('result.code==0x7641a)','result.code==0x7641a || result.code==0x7641c)')
 assert (K/'main.c').read_text()==expected and 'frequency!=3375000' in expected
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 cases=read('model001.json')['cases'];assert len(cases)==228 and len(read('clock-model001.json')['cases'])==10
 for c in cases:validate(c['raw_result'])
 save('schema-validation001.json',{'passed':True,'cases':len(cases),'validator_sha256':sha(K/'audit_logic.py'),'prefix_validator_sha256':sha(K/'prefix_schema.py'),'model_sha256':sha(K/'model001.json')})
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,200)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][193]:
   assert c['raw_result'][0]==0x7641d and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe enable admitted')
 assert base[188:194]==[99,227,1,227,99,0]
 assert [v for v in cases[0]['writes'] if v[:2]==['cr',0x17]]==[['cr',0x17,227],['cr',0x17,99],['cr',0x17,227],['cr',0x17,99],['cr',0x17,227]]
 for name in ['c2b-drop-write','c2b-drop-undo']:assert next(c['raw_result'] for c in cases if c['name']==name)==base
 for name in ['c17b-drop-write','c17b-low-read','c17b-wrong-write']:
  c=next(c for c in cases if c['name']==name);assert c['raw_result'][0]==0x7641c and c['raw_result'][192:194]==[99,0]
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (P/n).read_bytes().count(table)==1
 save('schema001.json',{'words':200,'bytes':800,'inherited':'0..187 same762; namespace764','new_fields':dict(zip(fields,range(188,200))),'new_statuses':{'7641c':'CR17 second fresh-read/forward/neighbor mismatch','7641d':'CR17 second recovery mismatch; inhibit output'},'CR17_target':227,'scope':'kernel checkpoint only; no native handoff; outer blank held'})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'source_order_verified':['CR01','laterCR02','CR17bit7enable'],'prior_probe762_exact_after_removing_delta':True,'prior_main762_exact_except_namespace_length_status':True,'own_reverse_recovery':True,'fresh_capture_guarded_by_prior_read':True,'model_cases':228,'rejected_schema_mutations':mutations,'prior_same_value_limit_retained':True,'prior_kernel762_audit_sha256':sha(O/'audit001.json'),'prior_native763_audit_sha256':sha(K.parent/'native-crtc-repeat763/audit001.json'),'result_bytes':800,'future_native_end_if_offset5100':0x5420,'exceeds_previous_initialized5400':True,'native_requires_expanded_initialization_and_fresh_bounds_proof':True})
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','schema-validation001.json','source-review001.json']
 assert all(read(n)['passed'] for n in checks);checks+=['schema001.json','lineage001.json']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=228,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS764 source/schema/link review; outer blank preserved')
