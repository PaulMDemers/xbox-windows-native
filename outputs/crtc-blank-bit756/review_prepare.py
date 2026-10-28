"""Independent delta, legacy target, schema, linked-byte and failure-preservation checks."""
import ast,datetime,hashlib,json,re,struct
from pathlib import Path
from audit_logic import validate,BASELINE,TARGET
k=Path(__file__).resolve().parent;o=k.parent/'crtc-blank-end754';p=Path('C:/xwn756/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda n:json.loads((k/n).read_text())
def ns(s):return re.sub(r'(?<![0-9])754(?![0-9])','756',re.sub(r'0x754(?=[0-9a-f]*\b)','0x756',s))
def save(n,r):
 with (k/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'script_sha256':sha(Path(__file__))}
assert not (k/'review001.json').exists()
try:
 for f in k.glob('*.py'):ast.parse(f.read_text())
 legacy=k.parent/'xcal-transaction704/gpu_legacy.c'
 assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 line='NvSetCrtc(pbRegs, 5, (NvGetCrtc(pbRegs, 5)&(~0x80)) | ((((gpu->nvhtotal/8)-1)&0x20)<<2) );'
 assert line in legacy.read_text()
 assert 'target={720,720,738,779,480,489,489,524,524,4,3}' in (k.parent/'xcal-transaction704/transaction003.c').read_text()
 assert (62&127)|(((779//8-1)&32)<<2)==190
 body=(k/'probe.c').read_text();old=ns((o/'probe.c').read_text())
 a=body.index(' /* Original second CR05 write:');b=body.index(' o->forward_status=0x756;\nrestore:',a)
 block=body[a:b]
 assert block==''' /* Original second CR05 write: replace only horizontal blank-end bit7. */
 o->c5b_before=o->c5_after_c3;
 o->c5b_target=(o->c5b_before&0x7f)|((((779u/8u)-1u)&0x20)<<2);
 o->c5b_attempted=1;cw(5,(uint8_t)o->c5b_target);o->forward_status=0x75614;
 o->c5b_after=cr(5);o->c0_after_c5b=cr(0);o->c2_after_c5b=cr(2);o->c3_after_c5b=cr(3);o->c4_after_c5b=cr(4);
 if(o->c5b_after!=o->c5b_target || o->c0_after_c5b!=o->c0_target || o->c2_after_c5b!=o->c2_target || o->c3_after_c5b!=o->c3_target || o->c4_after_c5b!=93)goto restore;
'''
 stripped=body[:a]+body[b:]
 for before,after in [
 (' o->c5b_after=o->c5b_restored=o->c0_after_c5b=o->c2_after_c5b=o->c3_after_c5b=o->c4_after_c5b=0xffffffff;\n',''),
 (' if(o->c5b_attempted){cw(5,(uint8_t)o->c5b_before);o->c5b_restored=cr(5);if(o->c5b_restored!=o->c5b_before)o->c5b_cleanup_mask=1;}\n',''),
 (' && !o->c5b_cleanup_mask',''),(' if(o->c5b_cleanup_mask)o->code=0x75615;\n','')]:
  assert before in stripped;stripped=stripped.replace(before,after)
 assert stripped[stripped.index('#include'):]==old[old.index('#include'):]
 order=['cw(5,(uint8_t)o->c5b_before)','cw(3,(uint8_t)o->c3_before)','cw(2,(uint8_t)o->c2_before)','cw(0,(uint8_t)o->c0_before)','cw(5,(uint8_t)o->c5_before)','cw(4,(uint8_t)o->c4_before)','R32(horizontal[i-1][0])=o->h_before[i-1]','gate(4)']
 assert [body.index(v) for v in order]==sorted(body.index(v) for v in order)
 assert len(re.findall(r'cw\(5,',body))==4 and not re.search(r'cw\((?:0x1b|0x22|0x33|1),',body)
 expected=ns((o/'main.c').read_text()).replace('crtc_blank_end_control','crtc_blank_bit_control').replace('words[143]','words[153]').replace('i<143','i<153').replace('result.c3_cleanup_mask){','result.c3_cleanup_mask || result.c5b_cleanup_mask){').replace('result.code==0x75612)','result.code==0x75612 || result.code==0x75614)')
 assert (k/'main.c').read_text()==expected and 'frequency!=3375000' in expected
 assert 'kernel_qpc_frequency_high' in expected
 assert not load('clock-model001.json')['passed'] and load('clock-model002.json')['passed']
 assert len(load('clock-model002.json')['cases'])==10
 for n in ['layout.c','layout.h']:assert (k/n).read_bytes()==(o/n).read_bytes()
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(k/n)==sha(p/n)
 cases=load('model001.json')['cases'];assert len(cases)==152
 for c in cases:validate(c['raw_result'])
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,153)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][148]:
   assert c['raw_result'][0]==0x75615 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe enable admitted')
 assert [v for v in cases[0]['writes'] if v[:2]==['cr',5]]==[['cr',5,62],['cr',5,190],['cr',5,62],['cr',5,49]]
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (p/n).read_bytes().count(table)==1
 save('schema001.json',{'words':153,'bytes':612,'inherited':'0..142 same754; exact namespace756','new_fields':dict(zip(['c5b_before','c5b_target','c5b_attempted','c5b_after','c5b_restored','c5b_cleanup_mask','c0_after_c5b','c2_after_c5b','c3_after_c5b','c4_after_c5b'],range(143,153))),'new_statuses':{'75614':'second CR05 forward/neighbor mismatch','75615':'second CR05 intermediate recovery mismatch; inhibit output'},'expected_sequence':[49,62,190,62,49],'scope':'kernel checkpoint only'})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'legacy_line':line,'prior_probe754_exact_after_removing_delta':True,'prior_main754_exact_except_namespace_length_status':True,'own_reverse_recovery':True,'model_cases':152,'rejected_schema_mutations':mutations,'prior_kernel754_audit_sha256':sha(o/'audit001.json'),'prior_native755_audit_sha256':sha(k.parent/'native-crtc-end755/audit001.json')})
 checks=['build001.json','model001.json','layout-model001.json','clock-model002.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
 assert all(load(n)['passed'] for n in checks)
 checks+=['schema001.json','lineage001.json','FAILURES.md','clock-model001.json']
 r.update(passed=True,checks={n:sha(k/n) for n in checks},model_cases=152,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in k.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS756 source/schema/link review; no hardware proof')
