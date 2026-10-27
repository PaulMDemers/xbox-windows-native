"""Independently review744 source deltas, target, result schema and frozen build."""
import ast,datetime,hashlib,json,re,struct,difflib
from pathlib import Path
from audit_logic import validate,BASELINE,TARGET
K=Path(__file__).resolve().parent;W=K.parents[1];O=K.parent/'horizontal-prefix742';P=Path('C:/xwn744/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
save=lambda n,v:(K/n).write_text(json.dumps(v,indent=2)+'\n',newline='\n')
assert not (K/'review001.json').exists()
r={'passed':False,'script_sha256':sha(Path(__file__))}
try:
 for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 legacy=W/'outputs/xcal-transaction704/gpu_legacy.c'
 assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 assert 'm = gpu->nvhtotal - 32;\n\tNvSetCrtc(pbRegs, 4, m/8);' in legacy.read_text()
 target=(779-32)//8;assert target==93
 assert 'target={720,720,738,779,480,489,489,524,524,4,3}' in (W/'outputs/xcal-transaction704/transaction003.c').read_text()
 cap=read(W/'outputs/native-horizontal743/collection001.json')
 samples=[d['data'] for d in cap['reports'].values() if d['data']['phase']=='kernel_context_captured']
 assert len(samples)==1
 assert dict(samples[0]['crtc_kernel_reads'])[4]==0xa7 and dict(samples[0]['crtc_kernel_reads'])[5]==0x31
 body=(K/'probe.c').read_text();old=(O/'probe.c').read_text().replace('742','744')
 for a,z in [('static const uint32_t setup','void probe744'),(' sw(0x21)',' o->forward_status=0x744;')]:
  end=body.index(' /* Next original') if z==' o->forward_status=0x744;' else body.index(z)
  assert body[body.index(a):end]==old[old.index(a):old.index(z)]
 for part in ['!(o->cr11_before&0x80)','o->c4_before=cr(4);o->c5_before=cr(5);','o->c4_before!=0xa7 || o->c5_before!=0x31','o->c4_attempted=1;cw(4,93)','o->c4_checked=cr(4);o->c5_checked=cr(5);','if(o->c4_attempted)cw(4,(uint8_t)o->c4_before);','if(!o->h_cleanup_mask && !o->c4_cleanup_mask){gate(4)']:assert part in body
 assert body.index('cw(4,(uint8_t)o->c4_before)')<body.index('R32(horizontal[i-1][0])=o->h_before[i-1]')<body.index('gate(4)')
 assert not re.search(r'cw\((?:5|0x05|0x1b|0x22|0x33),',body)
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes() or (K/n).read_text()==(O/n).read_text()
 main=(K/'main.c').read_text()
 for s in ['CREATE_NEW','NtFlushBuffersFile','!memcmp(report, verify, used)','Partition1','_Static_assert(sizeof(result)==sizeof(words)','Sleep(15000)','words[112]']:assert s in main
 assert main.index('probe744(&result)')<main.index('checkpoint("crtc_start_control_returned"')<main.index('if(result.h_cleanup_mask || result.c4_cleanup_mask)')<main.index('uint32_t *pixels=fb;')
 # Ensure the only main changes are namespace, phase name, record extent, and CR04 result handling.
 expected=(O/'main.c').read_text().replace('742','744').replace('horizontal_prefix_control','crtc_start_control').replace('words[104]','words[112]').replace('i<104','i<112').replace('if(result.h_cleanup_mask)','if(result.h_cleanup_mask || result.c4_cleanup_mask)').replace('result.code==0x7449)','result.code==0x7449 || result.code==0x744b)')
 assert main==expected
 for n in ['model004.py','layout_model.py']:
  assert "bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3')" in (K/n).read_text()
 cases=read(K/'model004.json')['cases'];assert len(cases)==98
 for case in cases:validate(case['raw_result'])
 mutations=[];base=cases[0]['raw_result']
 for i,value in [(0,0x744b),(1,0x7449),(28,0),(30,1),(83,0),(90,0),(97,6),(98,6),(100,1),(101,0),(104,0),(105,0),(106,0),(107,0),(108,1),(109,0),(110,0),(111,0)]:
  v=base.copy();v[i]=value
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('schema accepted mutation',i))
 for name in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling']:
  v=next(c['raw_result'] for c in cases if c['name']==name).copy();v[101]=1
  try:validate(v)
  except AssertionError:mutations.append(name)
  else:raise AssertionError('schema admitted unsafe enable')
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (P/n).read_bytes().count(table)==1
 schema={'words':112,'inherited':'0..103 same742 fields; status namespace744','CR04_before':104,'CR04_checked':105,'CR04_restored':106,'CR04_attempted':107,'CRTC_cleanup_mask':108,'CR05_before':109,'CR05_checked':110,'CR05_restored':111,'cleanup_mask_bits':{'0':'CR04 differs from own saved value','1':'unwritten CR05 differs from own saved value'},'new_statuses':{'744b':'CR04 or CR05 forward mismatch','744c':'CRTC recovery mismatch; no output enable'},'target_CR04':93,'target_CR05':'own unchanged value','scope':'kernel-context only; no visible mode switch'}
 save('schema001.json',schema)
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'baseline_capture_sha256':sha(W/'outputs/native-horizontal743/collection001.json'),'kernel742_audit_sha256':sha(O/'audit001.json'),'native743_audit_sha256':sha(W/'outputs/native-horizontal743/audit001.json'),'target_CR04':target,'baseline_CR04':167,'baseline_CR05':49,'prefix_forward_exact742':True,'restore_newest_first':True,'no_output_enable_after_either_restore_failure':True,'model_cases':98,'rejected_schema_mutations':mutations,'scope_document_sha256':sha(K/'SOURCE-REVIEW.md')})
 checks=['build001.json','model004.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 checks+=['schema001.json','lineage001.json','SOURCE-REVIEW.md','FAILURES.md']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=98,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS744 source, schema and exact-build review; no hardware claim')
