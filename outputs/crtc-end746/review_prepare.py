"""Independent delta, bit preservation, schema and linked-byte review746."""
import ast,datetime,hashlib,json,re,struct
from pathlib import Path
from audit_logic import validate,BASELINE,TARGET
K=Path(__file__).resolve().parent;W=K.parents[1];O=K.parent/'crtc-start744';P=Path('C:/xwn746/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
save=lambda n,v:(K/n).write_text(json.dumps(v,indent=2)+'\n',newline='\n')
assert not (K/'review001.json').exists()
r={'passed':False,'script_sha256':sha(Path(__file__))}
try:
 for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 legacy=W/'outputs/xcal-transaction704/gpu_legacy.c'
 assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=legacy.read_text();at=source.index('m = gpu->nvhtotal - 32;')
 excerpt=source[at:at+350]
 assert 'NvSetCrtc(pbRegs, 4, m/8);' in excerpt and '0xe0' in excerpt and 'm + 16' in excerpt
 assert 'target={720,720,738,779,480,489,489,524,524,4,3}' in (W/'outputs/xcal-transaction704/transaction003.c').read_text()
 assert (779-32)//8==93 and (((779-32+16)//8-1)&31)==30
 cap=read(W/'outputs/native-crtc745/collection001.json')
 samples=[d['data'] for d in cap['reports'].values() if d['data']['phase']=='kernel_context_captured']
 assert len(samples)==1 and dict(samples[0]['crtc_kernel_reads'])[4]==0xa7 and dict(samples[0]['crtc_kernel_reads'])[5]==0x31
 body=(K/'probe.c').read_text();old=(O/'probe.c').read_text().replace('744','746')
 # Remove only the intended CR05 additions, then compare all remaining code.
 start=body.index(' /* Original next read/modify/write:');end=body.index(' o->forward_status=0x746;\nrestore:',start)
 removed=body[:start]+body[end:]
 removed=removed.replace(' o->c5_after=o->c4_after=0xffffffff;\n','')
 removed=removed.replace(' /* Undo only attempted writes, newest first, using own saved full bytes. */\n if(o->c5_attempted)cw(5,(uint8_t)o->c5_before);',' /* Undo newest access first; never guess a repair for the unwritten CR05. */')
 assert removed[removed.index('#include'):]==old[old.index('#include'):]
 for s in ['o->c5_target=(o->c5_checked&0xe0)|((((779u-32u+16u)/8u)-1u)&0x1f);','o->c5_attempted=1;cw(5,(uint8_t)o->c5_target);o->forward_status=0x746d;','o->c5_after=cr(5);o->c4_after=cr(4);','if(o->c5_after!=o->c5_target || o->c4_after!=93)goto restore;']:assert s in body
 assert body.index('cw(5,(uint8_t)o->c5_before)')<body.index('cw(4,(uint8_t)o->c4_before)')<body.index('R32(horizontal[i-1][0])=o->h_before[i-1]')<body.index('gate(4)')
 assert len(re.findall(r'cw\(5,',body))==2 and not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 main=(K/'main.c').read_text();expected=(O/'main.c').read_text().replace('744','746').replace('crtc_start_control','crtc_end_control').replace('words[112]','words[116]').replace('i<112','i<116').replace('result.code==0x746b)','result.code==0x746b || result.code==0x746d)')
 assert main==expected
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 for n in ['model.py','layout_model.py']:assert "bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3')" in (K/n).read_text()
 cases=read(K/'model001.json')['cases'];assert len(cases)==104
 for case in cases:validate(case['raw_result'])
 mutations=[];base=cases[0]['raw_result']
 for i,value in [(0,0x746b),(1,0x746d),(28,0),(30,1),(83,0),(90,0),(97,6),(98,6),(100,1),(101,0),(104,0),(105,0),(106,0),(107,0),(108,1),(109,0),(110,0),(111,0),(112,0),(113,0),(114,0),(115,0)]:
  v=base.copy();v[i]=value
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('schema accepted mutation',i))
 for name in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling','c5-drop-restore']:
  v=next(c['raw_result'] for c in cases if c['name']==name).copy();v[101]=1
  try:validate(v)
  except AssertionError:mutations.append(name)
  else:raise AssertionError('schema admitted unsafe enable')
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (P/n).read_bytes().count(table)==1
 schema={'words':116,'inherited':'0..111 same744; namespace746; word110 is pre-CR05-write read','CR05_target':112,'CR05_attempted':113,'CR05_after':114,'CR04_after_CR05':115,'new_status':'746d CR05 full-byte/CR04 interaction mismatch','recovery':'746c either CRTC byte differs; no output enable','target_CR04':93,'target_CR05':62,'scope':'kernel checkpoint only'}
 save('schema001.json',schema)
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'legacy_excerpt':excerpt,'baseline_capture_sha256':sha(W/'outputs/native-crtc745/collection001.json'),'kernel744_audit_sha256':sha(O/'audit001.json'),'native745_audit_sha256':sha(W/'outputs/native-crtc745/audit001.json'),'original_prefix_exact744':True,'upper_three_bits_preserved':True,'full_byte_readback_required':True,'restore_newest_first':True,'model_cases':104,'rejected_schema_mutations':mutations,'scope_document_sha256':sha(K/'SOURCE-REVIEW.md')})
 checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 checks+=['schema001.json','lineage001.json','SOURCE-REVIEW.md','FAILURES.md']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=104,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS746 source, schema and linked-build review; no hardware claim')
