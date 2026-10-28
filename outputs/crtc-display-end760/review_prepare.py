"""Independent760 source delta, order, schema mutations and frozen build review."""
from pathlib import Path
import ast,datetime,hashlib,json,re,struct
from audit_logic import validate,BASELINE,TARGET
k=Path(__file__).resolve().parent;o=k.parent/'crtc-display-gate758';p=Path('C:/xwn760/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda n:json.loads((k/n).read_text())
def ns(s):return re.sub(r'(?<![0-9])758(?![0-9])','760',re.sub(r'0x758(?=[0-9a-f]*\b)','0x760',s))
def save(n,r):
 with (k/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'script_sha256':sha(Path(__file__))};assert not (k/'review001.json').exists()
try:
 for f in k.glob('*.py'):ast.parse(f.read_text())
 legacy=k.parent/'xcal-transaction704/gpu_legacy.c'
 assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 line='NvSetCrtc(pbRegs, 1, ((gpu->crtchdispend)/8)-1);'
 assert line in legacy.read_text()
 assert 'target={720,720,738,779,480,489,489,524,524,4,3}' in (k.parent/'xcal-transaction704/transaction003.c').read_text()
 body=(k/'probe.c').read_text();old=ns((o/'probe.c').read_text())
 block=''' /* Original next CR01 display-end byte, fresh own value for recovery. */
 o->forward_status=0x76018;o->c1_before=cr(1);o->c1_target=(720u/8u)-1u;
 o->c1_attempted=1;cw(1,(uint8_t)o->c1_target);
 o->c1_after=cr(1);o->c0_after_c1=cr(0);o->c2_after_c1=cr(2);o->c3_after_c1=cr(3);o->c4_after_c1=cr(4);o->c5_after_c1=cr(5);o->c17_after_c1=cr(0x17);
 if(o->c1_after!=o->c1_target || o->c0_after_c1!=o->c0_target || o->c2_after_c1!=o->c2_target || o->c3_after_c1!=o->c3_target || o->c4_after_c1!=93 || o->c5_after_c1!=o->c5b_target || o->c17_after_c1!=o->c17_target)goto restore;
'''
 assert body.count(block)==1;stripped=body.replace(block,'')
 for text in [' o->c1_after=o->c1_restored=o->c0_after_c1=o->c2_after_c1=o->c3_after_c1=o->c4_after_c1=o->c5_after_c1=o->c17_after_c1=0xffffffff;\n',
 ' if(o->c1_attempted){cw(1,(uint8_t)o->c1_before);o->c1_restored=cr(1);if(o->c1_restored!=o->c1_before)o->c1_cleanup_mask=1;}\n',
 ' && !o->c1_cleanup_mask',' if(o->c1_cleanup_mask)o->code=0x76019;\n']:
  assert stripped.count(text)==1;stripped=stripped.replace(text,'')
 assert stripped==old
 hline=' uint32_t c1_before,c1_target,c1_attempted,c1_after,c1_restored,c1_cleanup_mask,c0_after_c1,c2_after_c1,c3_after_c1,c4_after_c1,c5_after_c1,c17_after_c1;\n'
 assert (k/'probe.h').read_text().replace(hline,'')==ns((o/'probe.h').read_text())
 order=['cw(1,(uint8_t)o->c1_before)','cw(0x17,(uint8_t)o->c17_before)','cw(5,(uint8_t)o->c5b_before)','cw(3,(uint8_t)o->c3_before)','cw(2,(uint8_t)o->c2_before)','cw(0,(uint8_t)o->c0_before)','cw(5,(uint8_t)o->c5_before)','cw(4,(uint8_t)o->c4_before)','R32(horizontal[i-1][0])=o->h_before[i-1]','gate(4)']
 assert [body.index(v) for v in order]==sorted(body.index(v) for v in order)
 assert len(re.findall(r'cw\(1,',body))==2 and len(re.findall(r'cw\(0x17,',body))==2
 assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 expected=ns((o/'main.c').read_text()).replace('crtc_display_gate_control','crtc_display_end_control').replace('words[164]','words[176]').replace('i<164','i<176').replace('result.c17_cleanup_mask){','result.c17_cleanup_mask || result.c1_cleanup_mask){').replace('result.code==0x76016)','result.code==0x76016 || result.code==0x76018)')
 assert (k/'main.c').read_text()==expected and 'frequency!=3375000' in expected
 for n in ['layout.c','layout.h']:assert (k/n).read_bytes()==(o/n).read_bytes()
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(k/n)==sha(p/n)
 cases=load('model002.json')['cases'];assert len(cases)==189 and len(load('clock-model001.json')['cases'])==10
 assert not load('model001.json')['passed']
 for c in cases:validate(c['raw_result'])
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,176)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][169]:
   assert c['raw_result'][0]==0x76019 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe enable admitted')
 assert [v for v in cases[0]['writes'] if v[:2]==['cr',1]]==[['cr',1,89],['cr',1,159]]
 for val in [0,255]:
  c=next(c for c in cases if c['name']=='CR01-own-value-'+str(val))
  assert c['raw_result'][164:170]==[val,89,1,89,val,0]
  assert [v for v in c['writes'] if v[:2]==['cr',1]]==[['cr',1,89],['cr',1,val]]
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (p/n).read_bytes().count(table)==1
 save('schema001.json',{'words':176,'bytes':704,'inherited':'0..163 same758; namespace760','new_fields':dict(zip(['c1_before','c1_target','c1_attempted','c1_after','c1_restored','c1_cleanup_mask','c0_after_c1','c2_after_c1','c3_after_c1','c4_after_c1','c5_after_c1','c17_after_c1'],range(164,176))),'new_statuses':{'76018':'CR01 forward or neighbor mismatch','76019':'CR01 own-byte recovery mismatch; inhibit output'},'CR01_target':89,'CR01_before':'captured actual byte, no guessed physical baseline','scope':'kernel checkpoint only; no native handoff'})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'legacy_line':line,'prior_probe758_exact_after_removing_delta':True,'prior_main758_exact_except_namespace_length_status':True,'own_reverse_recovery':True,'fresh_own_capture_without_baseline_assumption':True,'model_cases':189,'rejected_schema_mutations':mutations,'prior_kernel758_audit_sha256':sha(o/'audit001.json'),'prior_native759_audit_sha256':sha(k.parent/'native-crtc-gate759/audit001.json'),'result_bytes':704,'future_native_end_if_offset5100':0x53c0,'future_native_requires_fresh_bounds_proof':True})
 checks=['build001.json','model002.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','schema-validation001.json','source-review001.json']
 assert all(load(n)['passed'] for n in checks)
 checks+=['schema001.json','lineage001.json','FAILURES.md','model001.json']
 r.update(passed=True,checks={n:sha(k/n) for n in checks},model_cases=189,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in k.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS760 source/schema/link review; no hardware proof')
