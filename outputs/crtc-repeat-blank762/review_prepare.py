"""Independent762 delta/order/schema/frozen review; no hardware access."""
from pathlib import Path
import ast,datetime,hashlib,json,re,struct
from audit_logic import validate,BASELINE,TARGET
k=Path(__file__).resolve().parent;o=k.parent/'crtc-display-end760';p=Path('C:/xwn762/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda n:json.loads((k/n).read_text())
def ns(s):return re.sub(r'(?<![0-9])760(?![0-9])','762',re.sub(r'0x760(?=[0-9a-f]*\b)','0x762',s))
def save(n,r):
 with (k/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'script_sha256':sha(Path(__file__))};assert not (k/'review001.json').exists()
try:
 for f in k.glob('*.py'):ast.parse(f.read_text())
 legacy=k.parent/'xcal-transaction704/gpu_legacy.c'
 assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 lines=legacy.read_text();c1=lines.index('NvSetCrtc(pbRegs, 1, ((gpu->crtchdispend)/8)-1);')
 c2=lines.index('NvSetCrtc(pbRegs, 2, ((gpu->crtchdispend)/8)-1);',c1)
 enable=lines.index('NvSetCrtc(pbRegs, 0x17, (NvGetCrtc(pbRegs, 0x17)&0x7f)|0x80);',c2)
 assert c1<c2<enable and 'target={720,720,738,779,480,489,489,524,524,4,3}' in (k.parent/'xcal-transaction704/transaction003.c').read_text()
 body=(k/'probe.c').read_text();old=ns((o/'probe.c').read_text())
 block=''' /* Original later CR02 write: same target, distinct source-ordered access. */
 o->forward_status=0x7621a;o->c2b_before=cr(2);
 if(o->c2b_before!=o->c2_after_c1)goto restore;
 o->c2b_target=(720u/8u)-1u;o->c2b_attempted=1;cw(2,(uint8_t)o->c2b_target);
 o->c2b_after=cr(2);o->c0_after_c2b=cr(0);o->c1_after_c2b=cr(1);o->c3_after_c2b=cr(3);o->c4_after_c2b=cr(4);o->c5_after_c2b=cr(5);o->c17_after_c2b=cr(0x17);
 if(o->c2b_after!=o->c2b_target || o->c0_after_c2b!=o->c0_target || o->c1_after_c2b!=o->c1_target || o->c3_after_c2b!=o->c3_target || o->c4_after_c2b!=93 || o->c5_after_c2b!=o->c5b_target || o->c17_after_c2b!=o->c17_target)goto restore;
'''
 assert body.count(block)==1;stripped=body.replace(block,'')
 for text in [' o->c2b_after=o->c2b_restored=o->c0_after_c2b=o->c1_after_c2b=o->c3_after_c2b=o->c4_after_c2b=o->c5_after_c2b=o->c17_after_c2b=0xffffffff;\n',
 ' if(o->c2b_attempted){cw(2,(uint8_t)o->c2b_before);o->c2b_restored=cr(2);if(o->c2b_restored!=o->c2b_before)o->c2b_cleanup_mask=1;}\n',
 ' && !o->c2b_cleanup_mask',' if(o->c2b_cleanup_mask)o->code=0x7621b;\n']:
  assert stripped.count(text)==1;stripped=stripped.replace(text,'')
 assert stripped==old
 fields=['c2b_before','c2b_target','c2b_attempted','c2b_after','c2b_restored','c2b_cleanup_mask','c0_after_c2b','c1_after_c2b','c3_after_c2b','c4_after_c2b','c5_after_c2b','c17_after_c2b']
 hline=' uint32_t '+','.join(fields)+';\n'
 assert (k/'probe.h').read_text().replace(hline,'')==ns((o/'probe.h').read_text())
 order=['cw(2,(uint8_t)o->c2b_before)','cw(1,(uint8_t)o->c1_before)','cw(0x17,(uint8_t)o->c17_before)','cw(5,(uint8_t)o->c5b_before)','cw(3,(uint8_t)o->c3_before)','cw(2,(uint8_t)o->c2_before)','cw(0,(uint8_t)o->c0_before)','cw(5,(uint8_t)o->c5_before)','cw(4,(uint8_t)o->c4_before)','R32(horizontal[i-1][0])=o->h_before[i-1]','gate(4)']
 assert [body.index(v) for v in order]==sorted(body.index(v) for v in order)
 assert len(re.findall(r'cw\(2,',body))==4 and len(re.findall(r'cw\(0x17,',body))==2
 assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 expected=ns((o/'main.c').read_text()).replace('crtc_display_end_control','crtc_repeat_blank_control').replace('words[176]','words[188]').replace('i<176','i<188').replace('result.c1_cleanup_mask){','result.c1_cleanup_mask || result.c2b_cleanup_mask){').replace('result.code==0x76218)','result.code==0x76218 || result.code==0x7621a)')
 assert (k/'main.c').read_text()==expected and 'frequency!=3375000' in expected
 for n in ['layout.c','layout.h']:assert (k/n).read_bytes()==(o/n).read_bytes()
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(k/n)==sha(p/n)
 cases=load('model001.json')['cases'];assert len(cases)==209 and len(load('clock-model001.json')['cases'])==10
 for c in cases:validate(c['raw_result'])
 save('schema-validation001.json',{'passed':True,'cases':len(cases),'validator_sha256':sha(k/'audit_logic.py'),'prefix_validator_sha256':sha(k/'prefix_schema.py'),'model_sha256':sha(k/'model001.json')})
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,188)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][181]:
   assert c['raw_result'][0]==0x7621b and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe enable admitted')
 assert [v for v in cases[0]['writes'] if v[:2]==['cr',2]]==[['cr',2,89],['cr',2,89],['cr',2,89],['cr',2,159]]
 for name in ['c2b-drop-write','c2b-drop-undo']:
  c=next(c for c in cases if c['name']==name)
  assert c['raw_result']==base and c['ports']==[5,4]
 c=next(c for c in cases if c['name']=='c2b-wrong-write-drop-undo')
 assert c['raw_result'][0]==0x7621b and c['raw_result'][179:182]==[88,88,1] and c['ports']==[5]
 for val in [0,255]:
  c=next(c for c in cases if c['name']=='CR01-own-value-'+str(val));assert c['raw_result'][164:170]==[val,89,1,89,val,0]
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (p/n).read_bytes().count(table)==1
 save('schema001.json',{'words':188,'bytes':752,'inherited':'0..175 same760; namespace762','new_fields':dict(zip(fields,range(176,188))),'new_statuses':{'7621a':'later CR02 fresh-read/forward/neighbor mismatch','7621b':'later CR02 recovery mismatch; inhibit output'},'CR02_target':89,'limitation':'same-value forward/undo drops indistinguishable by unchanged readback','scope':'kernel checkpoint only; no native handoff'})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'source_order_verified':['CR01','laterCR02','CR17enable excluded'],'prior_probe760_exact_after_removing_delta':True,'prior_main760_exact_except_namespace_length_status':True,'own_reverse_recovery':True,'fresh_capture_guarded_by_prior_read':True,'model_cases':209,'rejected_schema_mutations':mutations,'same_value_dropped_forward_undo_indistinguishable':True,'wrong_write_plus_dropped_undo_detected':True,'prior_kernel760_audit_sha256':sha(o/'audit001.json'),'prior_native761_audit_sha256':sha(k.parent/'native-crtc-end761/audit001.json'),'result_bytes':752,'future_native_end_if_offset5100':0x53f0,'future_native_requires_fresh_bounds_proof':True})
 checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','schema-validation001.json','source-review001.json']
 assert all(load(n)['passed'] for n in checks);checks+=['schema001.json','lineage001.json']
 r.update(passed=True,checks={n:sha(k/n) for n in checks},model_cases=209,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in k.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS762 source/schema/link review; same-value observability limits explicit')
