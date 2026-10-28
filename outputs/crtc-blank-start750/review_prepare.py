"""Independent CR02 delta, original-source, result-schema and linked-byte review."""
import ast,datetime,hashlib,json,re,struct
from pathlib import Path
from audit_logic import validate,BASELINE,TARGET
K=Path(__file__).resolve().parent;W=K.parents[1];O=K.parent/'crtc-total748';P=Path('C:/xwn750/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def save(n,v):
 p=K/n;assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n',newline='\n')
assert not (K/'review001.json').exists()
r={'passed':False,'script_sha256':sha(Path(__file__))}
try:
 for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 legacy=W/'outputs/xcal-transaction704/gpu_legacy.c'
 assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
 source=legacy.read_text();at=source.index('NvSetCrtc(pbRegs, 0, (gpu->nvhtotal/8)-5);');excerpt=source[at:at+230]
 assert 'NvSetCrtc(pbRegs, 2, ((gpu->crtchdispend)/8)-1);' in excerpt
 assert 'target={720,720,738,779,480,489,489,524,524,4,3}' in (W/'outputs/xcal-transaction704/transaction003.c').read_text()
 assert 720//8-1==0x59
 capture=W/'outputs/native-crtc-total749/collection001.json'
 samples=[d['data'] for d in read(capture)['reports'].values() if d['data']['phase']=='kernel_context_captured']
 assert len(samples)==1
 cr=dict(samples[0]['crtc_kernel_reads']);assert [cr[i] for i in [2,0,4,5,0x11]]==[0x9f,0xc8,0xa7,0x31,9]
 body=(K/'probe.c').read_text();old=(O/'probe.c').read_text().replace('748','750')
 start=body.index(' /* Next original horizontal blank-start byte:');end=body.index(' o->forward_status=0x750;\nrestore:',start)
 removed=body[:start]+body[end:]
 for a,b in [
 (' o->c2_after=o->c2_restored=o->c0_after_c2=o->c4_after_c2=o->c5_after_c2=0xffffffff;\n',''),
 ('o->c0_before=cr(0);o->c2_before=cr(2);','o->c0_before=cr(0);'),
 (' || o->c2_before!=0x9f',''),
 (' if(o->c2_attempted)cw(2,(uint8_t)o->c2_before);\n',''),
 ('o->c0_restored=cr(0);o->c2_restored=cr(2);\n if(o->c2_restored!=o->c2_before)o->c2_cleanup_mask=1;','o->c0_restored=cr(0);'),
 (' && !o->c2_cleanup_mask',''),
 (' if(o->c2_cleanup_mask)o->code=0x75011;\n','')]:
  assert a in removed,a;removed=removed.replace(a,b)
 assert removed[removed.index('#include'):]==old[old.index('#include'):]
 for part in ['o->c2_target=(720u/8u)-1u;o->c2_attempted=1;cw(2,(uint8_t)o->c2_target);o->forward_status=0x75010;',
 'o->c2_after=cr(2);o->c0_after_c2=cr(0);o->c4_after_c2=cr(4);o->c5_after_c2=cr(5);',
 'if(o->c2_after!=o->c2_target || o->c0_after_c2!=o->c0_target || o->c4_after_c2!=93 || o->c5_after_c2!=o->c5_target)goto restore;']:assert part in body
 assert body.index('cw(2,(uint8_t)o->c2_before)')<body.index('cw(0,(uint8_t)o->c0_before)')<body.index('cw(5,(uint8_t)o->c5_before)')<body.index('cw(4,(uint8_t)o->c4_before)')<body.index('R32(horizontal[i-1][0])=o->h_before[i-1]')<body.index('gate(4)')
 assert len(re.findall(r'cw\(2,',body))==2 and not re.search(r'cw\((?:0x1b|0x22|0x33|3|1),',body)
 main=(K/'main.c').read_text()
 expected=(O/'main.c').read_text().replace('748','750').replace('crtc_total_control','crtc_blank_start_control').replace('words[124]','words[133]').replace('i<124','i<133').replace('result.c0_cleanup_mask){','result.c0_cleanup_mask || result.c2_cleanup_mask){').replace('result.code==0x750e)','result.code==0x750e || result.code==0x75010)')
 assert main==expected
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 for n in ['model.py','layout_model.py']:assert "bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3')" in (K/n).read_text()
 cases=read(K/'model001.json')['cases'];assert len(cases)==124
 for case in cases:validate(case['raw_result'])
 mutations=[];base=cases[0]['raw_result']
 for i,value in [(0,0x750b),(1,0x75010),(28,0),(30,1),(83,0),(90,0),(97,6),(98,6),(100,1),(101,0)]+[(i,1 if i in [108,121,129] else 0) for i in range(104,133)]:
  assert base[i]!=value,(i,value)
  v=base.copy();v[i]=value
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('schema accepted mutation',i))
 for name in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling','c5-drop-restore','c0-restore-read','c0-drop-restore','c2-restore-read','c2-drop-restore']:
  v=next(c['raw_result'] for c in cases if c['name']==name).copy();v[101]=1
  try:validate(v)
  except AssertionError:mutations.append(name)
  else:raise AssertionError('schema admitted unsafe enable')
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (P/n).read_bytes().count(table)==1
 schema={'words':133,'inherited':'0..123 same748; namespace750','CR02_before':124,'CR02_target':125,'CR02_attempted':126,'CR02_after':127,'CR02_restored':128,'CR02_cleanup_mask':129,'CR00_after_CR02':130,'CR04_after_CR02':131,'CR05_after_CR02':132,'new_statuses':{'75010':'CR02 forward or neighbor mismatch','75011':'CR02 restoration mismatch; output disabled'},'target_CR02':89,'scope':'kernel checkpoint only'}
 save('schema001.json',schema)
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'legacy_excerpt':excerpt,'baseline_capture_sha256':sha(capture),'kernel748_audit_sha256':sha(O/'audit001.json'),'native749_audit_sha256':sha(W/'outputs/native-crtc-total749/audit001.json'),'prior_probe_exact748':True,'CR02_baseline':159,'CR02_target':89,'full_byte_readback_required':True,'restore_newest_first':True,'model_cases':124,'rejected_schema_mutations':mutations,'scope_document_sha256':sha(K/'SOURCE-REVIEW.md')})
 checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 checks+=['schema001.json','lineage001.json','SOURCE-REVIEW.md','FAILURES.md']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=124,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS750 source, schema and linked-build review; no hardware claim')
