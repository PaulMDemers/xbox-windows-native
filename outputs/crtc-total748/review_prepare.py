"""Independent delta, bit preservation, schema and linked-byte review748."""
import ast,datetime,hashlib,json,re,struct
from pathlib import Path
from audit_logic import validate,BASELINE,TARGET
K=Path(__file__).resolve().parent;W=K.parents[1];O=K.parent/'crtc-end746';P=Path('C:/xwn748/build001')
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
 cap=read(W/'outputs/native-crtc-end747/collection001.json')
 samples=[d['data'] for d in cap['reports'].values() if d['data']['phase']=='kernel_context_captured']
 assert len(samples)==1 and dict(samples[0]['crtc_kernel_reads'])[4]==0xa7 and dict(samples[0]['crtc_kernel_reads'])[5]==0x31
 body=(K/'probe.c').read_text();old=(O/'probe.c').read_text().replace('746','748')
 assert dict(samples[0]['crtc_kernel_reads'])[0]==0xc8
 assert 'NvSetCrtc(pbRegs, 0, (gpu->nvhtotal/8)-5);' in source and 779//8-5==92
 # Strip only the new CR00 operations/guard, then compare the full746 code.
 start=body.index(' /* Next original CRTC total byte:');end=body.index(' o->forward_status=0x748;\nrestore:',start)
 removed=body[:start]+body[end:]
 for a,b in [
 (' o->c0_after=o->c0_restored=o->c4_after_c0=o->c5_after_c0=0xffffffff;\n',''),
 ('o->c5_before=cr(5);o->c0_before=cr(0);','o->c5_before=cr(5);'),
 (' || o->c0_before!=0xc8',''),
 (' if(o->c0_attempted)cw(0,(uint8_t)o->c0_before);\n',''),
 ('o->c5_restored=cr(5);o->c0_restored=cr(0);\n if(o->c0_restored!=o->c0_before)o->c0_cleanup_mask=1;','o->c5_restored=cr(5);'),
 (' && !o->c0_cleanup_mask',''),
 (' if(o->c0_cleanup_mask)o->code=0x748f;\n','')]:
  assert a in removed,a;removed=removed.replace(a,b)
 assert removed[removed.index('#include'):]==old[old.index('#include'):]
 for part in ['o->c0_target=(779u/8u)-5u;o->c0_attempted=1;cw(0,(uint8_t)o->c0_target);o->forward_status=0x748e;','o->c0_after=cr(0);o->c4_after_c0=cr(4);o->c5_after_c0=cr(5);','if(o->c0_after!=o->c0_target || o->c4_after_c0!=93 || o->c5_after_c0!=o->c5_target)goto restore;']:assert part in body
 assert body.index('cw(0,(uint8_t)o->c0_before)')<body.index('cw(5,(uint8_t)o->c5_before)')<body.index('cw(4,(uint8_t)o->c4_before)')<body.index('R32(horizontal[i-1][0])=o->h_before[i-1]')<body.index('gate(4)')
 assert len(re.findall(r'cw\(0,',body))==2 and not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
 main=(K/'main.c').read_text();expected=(O/'main.c').read_text().replace('746','748').replace('crtc_end_control','crtc_total_control').replace('words[116]','words[124]').replace('i<116','i<124').replace('result.h_cleanup_mask || result.c4_cleanup_mask','result.h_cleanup_mask || result.c4_cleanup_mask || result.c0_cleanup_mask').replace('result.code==0x748d)','result.code==0x748d || result.code==0x748e)')
 assert main==expected
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 for n in ['model.py','layout_model.py']:assert "bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3')" in (K/n).read_text()
 cases=read(K/'model001.json')['cases'];assert len(cases)==113
 for case in cases:validate(case['raw_result'])
 mutations=[];base=cases[0]['raw_result']
 for i,value in [(0,0x748b),(1,0x748e),(28,0),(30,1),(83,0),(90,0),(97,6),(98,6),(100,1),(101,0),(104,0),(105,0),(106,0),(107,0),(108,1),(109,0),(110,0),(111,0),(112,0),(113,0),(114,0),(115,0),(116,0),(117,0),(118,0),(119,0),(120,0),(121,1),(122,0),(123,0)]:
  v=base.copy();v[i]=value
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('schema accepted mutation',i))
 for name in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling','c5-drop-restore','c0-restore-read','c0-drop-restore']:
  v=next(c['raw_result'] for c in cases if c['name']==name).copy();v[101]=1
  try:validate(v)
  except AssertionError:mutations.append(name)
  else:raise AssertionError('schema admitted unsafe enable')
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (P/n).read_bytes().count(table)==1
 schema={'words':124,'inherited':'0..115 same746; namespace748','CR00_before':116,'CR00_target':117,'CR00_attempted':118,'CR00_after':119,'CR00_restored':120,'CR00_cleanup_mask':121,'CR04_after_CR00':122,'CR05_after_CR00':123,'new_statuses':{'748e':'CR00 forward or CR04/CR05 interaction mismatch','748f':'CR00 recovery mismatch; output disabled'},'target_CR00':92,'scope':'kernel checkpoint only'}
 save('schema001.json',schema)
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'legacy_excerpt':excerpt,'baseline_capture_sha256':sha(W/'outputs/native-crtc-end747/collection001.json'),'kernel746_audit_sha256':sha(O/'audit001.json'),'native747_audit_sha256':sha(W/'outputs/native-crtc-end747/audit001.json'),'original_prefix_exact746':True,'CR00_baseline':200,'CR00_target':92,'full_byte_readback_required':True,'restore_newest_first':True,'model_cases':113,'rejected_schema_mutations':mutations,'scope_document_sha256':sha(K/'SOURCE-REVIEW.md')})
 checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 checks+=['schema001.json','lineage001.json','SOURCE-REVIEW.md','FAILURES.md']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=113,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS748 source, schema and linked-build review; no hardware claim')
