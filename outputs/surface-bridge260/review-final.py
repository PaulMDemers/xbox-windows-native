"""Close260 without promoting the failed live attestation to a renderer result."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for manifest in ['emulator-frozen.json','emulator-frozen002.json']:
 for name,digest in read(k/manifest).items():assert sha(ws/name)==digest,name
build=read(k/'renderer-build001.json');assert build['passed'] and build['borrowed_sources_restored']
assert sha(Path('E:/Codex-archive/xbox-windows-native/bridge260-build001/xemu-bridge260.exe'))==build['executable_sha256']
for name in ['callback-review001.json','attestation-review002.json','kernel-discovery-review.json']:
 j=read(k/name);assert j['passed']
 for p,h in j['inputs'].items():assert sha(k/p)==h,p
trace=read(k/'emu002/trace.json');audit=read(k/'emu002/audit.json')
assert trace['closed'] and not trace['passed'] and trace['error']=="AssertionError('E14')"
assert not trace['remaining_breakpoints'] and trace['physical_mode_restored'] and not trace['guest_resumed']
assert not trace['checkpoints'] and not trace.get('frontend_close_requested')
assert not any('xwn-pattern260 ' in v['command'] for v in trace['monitor'])
assert audit['normal_shutdown_count']==0 and not audit['integrity_passed'] and not audit['strict_qualification_passed']
allocation=read(k/'emu002/allocation.json');assert allocation['orphan_cluster_count']==13 and len(allocation['errors'])==4
for case in ['emu001','emu002']:
 assert read(k/case/'host-state.json')['closed'] and read(k/case/'closure.json')['closed']
assert not Path('E:/Codex-private-artifacts/xbox-windows-feasibility/bridge260/runs/nt5-bridge260-emu001').exists()
assert not (k/'emu001/runner-start.json').exists()
for name in ['portable-260.json','portable-260c.json']:
 manifest=read(ws/'outputs/task-storage-offload'/name);assert manifest['closed']
 for entry in manifest['entries']:
  assert entry['original_path_preserved'] and not entry['disk_backing_chains_moved']
  for row in entry['files']:
   for root in [entry['source'],entry['target']]:assert sha(Path(root)/row['path'])==row['sha256']
f=read(k/'emu002/fixture.json')
r=dict(passed=True,review_only=True,guest_diagnostic_passed=False,gl_executed=False,
 cpu_callback_coverage=False,pixel_preservation_proved=False,ordinary_qualified=False,
 native_gpu_ownership=False,physical_access=False,renderer_sha256=build['executable_sha256'],
 frozen_inputs002=len(read(k/'emulator-frozen002.json')),source_sha256=sha(Path(__file__)),
 cases=dict(emu001='closed host capacity refusal; no xemu',emu002='closed E14 attestation failure; no renderer request; cold integrity failed'),
 closed_sessions=[63709,8634,48075,5809],
 next='Fresh actual-IDTR/kernel discovery, partial read/pin logging and completed ownership attestation before any renderer stage',
 lineage_corrections={n:dict(frozen_value=f.get(n),actual=v) for n,v in {
  'emulator_source_changed':True,'emulator_source_changed_only':build['changed_sources'],
  'paired_inventory':False,'matched_control_scope':'No paired runtime control; one failed debugger attempt before new operation',
  'compiled_emulator_from':'E:/Codex-archive/xbox-windows-native/bridge260-build001'}.items()})
dest.write_text(json.dumps(r,indent=2)+'\n');print('260 reviewed: compiled bridge, CLOSED failed live attestation, no renderer/physical promotion')
