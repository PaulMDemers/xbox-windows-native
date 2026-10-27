from pathlib import Path
import re,json,hashlib,datetime
k=Path('outputs/native-630726');old=Path('outputs/native-prefix725')
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h']:
 a=(old/n).read_text().replace('725','726').replace('payload_reloc,11,','payload_reloc,1,').replace('count!=11','count!=1')
 assert clean(a)==clean((k/n).read_text()),n
a=(old/'bridge.S').read_text().replace('725','726');b=(k/'bridge.S').read_text()
assert a[:a.index('report_offsets:')]==b[:b.index('report_offsets:')]
assert a[a.index('bridge_code_end:'):]==b[b.index('bridge_code_end:'):]
a=(old/'transaction725.c').read_text();b=(k/'transaction726.c').read_text()
assert a[a.index('int bounds704'):a.index('int native_transaction704')]==b[b.index('int bounds704'):b.index('int native_transaction704')]
probe=(k/'probe.c').read_text()
assert 'cw(' not in probe and not re.search(r'R8\(0x6013d5\)\s*=',probe)
assert len(re.findall(r'R32\(0x680630\)\s*=',probe))==2
assert 'i<32' in probe and 'o->cr1b[5]==o->cr1b[0]' in probe
run=json.loads((k/'integration002.json').read_text());assert run['passed'] and len(run['cases'])==44
for c in run['cases']:
 assert c['CRTC_data_writes']==0 and c['all_pixels_and_guards_exact']
 assert c['MMIO_writes'] in ([],[[0x680630,2],[0x680630,3]])
variants={c['name']:c for c in run['cases']}
assert variants['behavior-coupled']['raw_result'][26:32]==[0x85,0x85,5,0x85,0x85,0x85]
assert variants['behavior-blank']['raw_result'][26:32]==[0x85,5,5,5,0x85,0x85]
assert variants['behavior-late']['raw_result'][39]==1
assert variants['behavior-oscillate']['raw_result'][39]==6
assert variants['wide2']['raw_result'][22]==0x10002 and variants['wide2']['raw_result'][34]==0xffffffff
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frontend_plan_layout_same_except_namespace_and_one_relocation':True,'bridge_same_except_namespace_and_report_offsets':True,'framebuffer_bounds_identical':True,'compiled_integration_write_allowlist':'only63032-bit2 then3; SEQ1 blank/restore; selector traffic; gates5/4; no CRTC data writes','full_byte_CR1b_restoration_checked':True,'full_width_630_checked_before_optical_packing':True,'late_pairs_bounded':32,'result_bytes':172,'hypotheses_independent_of_admission':True,'sources':{n:sha(k/n) for n in ['probe.c','probe.h','transaction726.c','transaction.h','main.c','bridge.S']},'limits':'Models validate instrumentation and guards, not physical coupling, write masks, timing or mode switching.'}
(k/'source-review001.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS reduced write surface, independent model vectors and retained handoff guards')
