"""Independent CR03 source delta, captured baseline, schema and exact linked-byte review."""
import ast,datetime,hashlib,json,re,struct
from pathlib import Path
from audit_logic import validate,BASELINE,TARGET
K=Path(__file__).resolve().parent;W=K.parents[1];O=K.parent/'crtc-blank-start750';P=Path('C:/xwn753/build001')
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
 source=legacy.read_text();at=source.index('// CRTC_HBLANKEND');excerpt=source[at:source.index('// CRTC_HDISPEND',at)]
 assert 'NvSetCrtc(pbRegs, 3, (NvGetCrtc(pbRegs, 3)&0xe0) |(((gpu->nvhtotal/8)-1)&0x1f));' in excerpt
 assert 'target={720,720,738,779,480,489,489,524,524,4,3}' in (W/'outputs/xcal-transaction704/transaction003.c').read_text()
 capture=W/'outputs/native-crtc-blank752/collection001.json'
 sample=next(v['data'] for v in read(capture)['reports'].values() if v['data']['phase']=='kernel_context_captured')
 cr=dict(sample['crtc_kernel_reads']);assert [cr[i] for i in [3,2,0,4,5,0x11]]==[0x8c,0x9f,0xc8,0xa7,0x31,9]
 assert (cr[3]&0xe0)|((779//8-1)&31)==0x80
 body=(K/'probe.c').read_text();old=(O/'probe.c').read_text().replace('750','753')
 start=body.index(' /* Next original horizontal blank-end byte;');end=body.index(' o->forward_status=0x753;\nrestore:',start)
 removed=body[:start]+body[end:]
 for a,b in [
 (' o->c3_after=o->c3_restored=o->c0_after_c3=o->c2_after_c3=o->c4_after_c3=o->c5_after_c3=0xffffffff;\n',''),
 ('o->c2_before=cr(2);o->c3_before=cr(3);','o->c2_before=cr(2);'),
 (' || o->c3_before!=0x8c',''),
 (' if(o->c3_attempted)cw(3,(uint8_t)o->c3_before);\n',''),
 ('o->c2_restored=cr(2);o->c3_restored=cr(3);\n if(o->c3_restored!=o->c3_before)o->c3_cleanup_mask=1;','o->c2_restored=cr(2);'),
 (' && !o->c3_cleanup_mask',''),
 (' if(o->c3_cleanup_mask)o->code=0x75313;\n','')]:
  assert a in removed,a;removed=removed.replace(a,b)
 assert removed[removed.index('#include'):]==old[old.index('#include'):]
 for part in ['o->c3_target=(o->c3_before&0xe0)|(((779u/8u)-1u)&0x1f);','o->c3_attempted=1;cw(3,(uint8_t)o->c3_target);o->forward_status=0x75312;',
 'o->c3_after=cr(3);o->c0_after_c3=cr(0);o->c2_after_c3=cr(2);o->c4_after_c3=cr(4);o->c5_after_c3=cr(5);',
 'if(o->c3_after!=o->c3_target || o->c0_after_c3!=o->c0_target || o->c2_after_c3!=o->c2_target || o->c4_after_c3!=93 || o->c5_after_c3!=o->c5_target)goto restore;']:assert part in body
 order=['cw(3,(uint8_t)o->c3_before)','cw(2,(uint8_t)o->c2_before)','cw(0,(uint8_t)o->c0_before)','cw(5,(uint8_t)o->c5_before)','cw(4,(uint8_t)o->c4_before)','R32(horizontal[i-1][0])=o->h_before[i-1]','gate(4)']
 assert [body.index(t) for t in order]==sorted(body.index(t) for t in order)
 assert len(re.findall(r'cw\(3,',body))==2 and not re.search(r'cw\((?:0x1b|0x22|0x33|1),',body)
 assert len(re.findall(r'cw\(5,',body))==2,'No subsequent CR05-bit7 transaction allowed'
 expected=(O/'main.c').read_text().replace('750','753').replace('crtc_blank_start_control','crtc_blank_end_control').replace('words[133]','words[143]').replace('i<133','i<143').replace('result.c2_cleanup_mask){','result.c2_cleanup_mask || result.c3_cleanup_mask){').replace('result.code==0x75310)','result.code==0x75310 || result.code==0x75312)')
 assert (K/'main.c').read_text()==expected
 for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
 for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
 for n in ['model.py','layout_model.py']:assert "bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3')" in (K/n).read_text()
 cases=read(K/'model001.json')['cases'];assert len(cases)==138
 for case in cases:validate(case['raw_result'])
 mutations=[];base=cases[0]['raw_result']
 for i in [0,1,28,30,83,90,97,98,100,101]+list(range(104,143)):
  v=base.copy();v[i]^=1
  try:validate(v)
  except AssertionError:mutations.append(i)
  else:raise AssertionError(('schema accepted mutation',i))
 for name in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling','c5-drop-restore','c0-restore-read','c0-drop-restore','c2-restore-read','c2-drop-restore','c3-restore-read','c3-drop-restore']:
  v=next(c['raw_result'] for c in cases if c['name']==name).copy();v[101]=1
  try:validate(v)
  except AssertionError:mutations.append(name)
  else:raise AssertionError('schema admitted unsafe enable')
 table=struct.pack('<21I',*[v for a,t,b in zip([0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838],TARGET,BASELINE) for v in [a,t,b]])
 for n in ['main.exe','bin/default.xbe']:assert (P/n).read_bytes().count(table)==1
 schema={'words':143,'bytes':572,'inherited':'0..132 same750; namespace753','CR03_before':133,'CR03_target':134,'CR03_attempted':135,'CR03_after':136,'CR03_restored':137,'CR03_cleanup_mask':138,'CR00_after_CR03':139,'CR02_after_CR03':140,'CR04_after_CR03':141,'CR05_after_CR03':142,'new_statuses':{'75312':'CR03 forward or neighbor mismatch','75313':'CR03 recovery mismatch; output disabled'},'target_CR03':128,'scope':'kernel checkpoint only'}
 save('schema001.json',schema)
 save('source-review001.json',{'passed':True,'legacy_sha256':sha(legacy),'legacy_excerpt':excerpt,'baseline_capture_sha256':sha(capture),'kernel750_audit_sha256':sha(O/'audit001.json'),'native752_audit_sha256':sha(W/'outputs/native-crtc-blank752/audit001.json'),'prior_probe_exact750':True,'CR03_baseline':140,'CR03_target':128,'full_byte_readback_required':True,'restore_newest_first':True,'model_cases':138,'rejected_schema_mutations':mutations,'scope_document_sha256':sha(K/'SOURCE-REVIEW.md')})
 checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
 assert all(read(K/n)['passed'] for n in checks)
 checks+=['schema001.json','lineage001.json','SOURCE-REVIEW.md','FAILURES.md']
 r.update(passed=True,checks={n:sha(K/n) for n in checks},model_cases=138,layout_cases=2353,max_modeled_critical_instructions=max(c['critical_instructions'] for c in cases),physical_proof=False)
 save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes']})
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('review001.json',r)
print('PASS753 source, schema and linked-build review; no hardware claim')
