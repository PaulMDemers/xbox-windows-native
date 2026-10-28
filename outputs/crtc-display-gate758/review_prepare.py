"""Independent758 delta, source order, result schema and exact build freeze."""
from pathlib import Path
import ast,datetime,hashlib,json,re,struct
from audit_logic import validate,BASELINE,TARGET
k=Path(__file__).resolve().parent;o=k.parent/'crtc-blank-bit756';p=Path('C:/xwn758/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda n:json.loads((k/n).read_text())
def ns(s):return re.sub(r'(?<![0-9])756(?![0-9])','758',re.sub(r'0x756(?=[0-9a-f]*\b)','0x758',s))
def save(n,r):
 with (k/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
r={'passed':False,'script_sha256':sha(Path(__file__))};assert not (k/'review001.json').exists()
try:
 for f in k.glob('*.py'):ast.parse(f.read_text())
 legacy=k.parent/'xcal-transaction704/gpu_legacy.c'
 assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 line='NvSetCrtc(pbRegs, 0x17, (NvGetCrtc(pbRegs, 0x17)&0x7f));'
 assert line in legacy.read_text()
 assert 'target={720,720,738,779,480,489,489,524,524,4,3}' in (k.parent/'xcal-transaction704/transaction003.c').read_text()
 body=(k/'probe.c').read_text();old=ns((o/'probe.c').read_text())
 block=''' /* Next original CR17 RMW: clear bit7 only, with fresh own-byte capture. */
 o->forward_status=0x75816;o->c17_before=cr(0x17);
 if(o->c17_before!=o->crtc_checked[1])goto restore;
 o->c17_target=o->c17_before&0x7f;o->c17_attempted=1;cw(0x17,(uint8_t)o->c17_target);
 o->c17_after=cr(0x17);o->c0_after_c17=cr(0);o->c2_after_c17=cr(2);o->c3_after_c17=cr(3);o->c4_after_c17=cr(4);o->c5_after_c17=cr(5);
 if(o->c17_after!=o->c17_target || o->c0_after_c17!=o->c0_target || o->c2_after_c17!=o->c2_target || o->c3_after_c17!=o->c3_target || o->c4_after_c17!=93 || o->c5_after_c17!=o->c5b_target)goto restore;
'''
 assert body.count(block)==1;stripped=body.replace(block,'')
 for text in [' o->c17_after=o->c17_restored=o->c0_after_c17=o->c2_after_c17=o->c3_after_c17=o->c4_after_c17=o->c5_after_c17=0xffffffff;\n',
 ' if(o->c17_attempted){cw(0x17,(uint8_t)o->c17_before);o->c17_restored=cr(0x17);if(o->c17_restored!=o->c17_before)o->c17_cleanup_mask=1;}\n',
 ' && !o->c17_cleanup_mask',' if(o->c17_cleanup_mask)o->code=0x75817;\n']:
  assert stripped.count(text)==1;stripped=stripped.replace(text,'')
 assert stripped[stripped.index('#include'):]==old[old.index('#include'):]
 hline=' uint32_t c17_before,c17_target,c17_attempted,c17_after,c17_restored,c17_cleanup_mask,c0_after_c17,c2_after_c17,c3_after_c17,c4_after_c17,c5_after_c17;\n'
 assert (k/'probe.h').read_text().replace(hline,'')==ns((o/'probe.h').read_text())
 order=['cw(0x17,(uint8_t)o->c17_before)','cw(5,(uint8_t)o->c5b_before)','cw(3,(uint8_t)o->c3_before)','cw(2,(uint8_t)o->c2_before)','cw(0,(uint8_t)o->c0_before)','cw(5,(uint8_t)o->c5_before)','cw(4,(uint8_t)o->c4_before)','R32(horizontal[i-1][0])=o->h_before[i-1]','gate(4)']
 assert [body.index(v) for v in order]==sorted(body.index(v) for v in order)
 assert len(re.findall(r'cw\(0x17,',body))==2 and not re.search(r'cw\((?:0x1b|0x22|0x33|1),',body)
 expected=ns((o/'main.c').read_text()).replace('crtc_blank_bit_control','crtc_display_gate_control').replace('words[153]','words[164]').replace('i<153','i<164').replace('result.c5b_cleanup_mask){','result.c5b_cleanup_mask || result.c17_cleanup_mask){').replace('result.code==0x75814)','result.code==0x75814 || result.code==0x75816)')
 assert (k/'main.c').read_text()==expected and 'frequency!=3375000' in expected
 for n in ['layout.c','layout.h']:assert (k/n).read_bytes()==(o/n).read_bytes()
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(k/n)==sha(p/n)
 cases=load('model002.json')['cases'];assert len(cases)==169 and len(load('clock-model001.json')['cases'])==10
 assert not load('model001.json')['passed']
 for c in cases:validate(c['raw_result'])
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,164)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('accepted mutation',i))
 for c in cases:
  if c['raw_result'][158]:
   assert c['raw_result'][0]==0x75817 and c['raw_result'][101]==0 and c['ports']==[5]
   v=c['raw_result'].copy();v[101]=1
   try:validate(v)
   except AssertionError:mutations.append(c['name'])
   else:raise AssertionError('unsafe enable admitted')
 assert [v for v in cases[0]['writes'] if v[:2]==['cr',0x17]]==[['cr',0x17,227],['cr',0x17,99],['cr',0x17,227]]
 before=next(c for c in cases if c['name']=='c17-before-read')['raw_result'];assert before[155]==0 and before[153]==226 and before[1]==0x75816
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (p/n).read_bytes().count(table)==1
 save('schema001.json',{'words':164,'bytes':656,'inherited':'0..152 same756; namespace758','new_fields':dict(zip(['c17_before','c17_target','c17_attempted','c17_after','c17_restored','c17_cleanup_mask','c0_after_c17','c2_after_c17','c3_after_c17','c4_after_c17','c5_after_c17'],range(153,164))),'new_statuses':{'75816':'CR17 pre-read, forward or neighbor mismatch','75817':'CR17 own-byte recovery mismatch; inhibit output'},'expected_sequence':[227,99,227],'scope':'kernel checkpoint only; no native handoff'})
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'legacy_line':line,'prior_probe756_exact_after_removing_delta':True,'prior_main756_exact_except_namespace_length_status':True,'own_reverse_recovery':True,'fresh_before_read_checked':True,'model_cases':169,'rejected_schema_mutations':mutations,'prior_kernel756_audit_sha256':sha(o/'audit001.json'),'prior_native757_audit_sha256':sha(k.parent/'native-crtc-bit757/audit001.json'),'result_bytes':656,'future_native_end_if_offset5100':0x5390,'future_native_requires_fresh_bounds_proof':True})
 checks=['build001.json','model002.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','schema-validation001.json','source-review001.json']
 assert all(load(n)['passed'] for n in checks)
 checks+=['schema001.json','lineage001.json','FAILURES.md','model001.json']
 r.update(passed=True,checks={n:sha(k/n) for n in checks},model_cases=169,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{f.name:sha(f) for f in k.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS758 source/schema/link review; no hardware proof')
