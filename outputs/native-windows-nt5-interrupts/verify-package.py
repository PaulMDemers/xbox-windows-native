"""Verify reports refer to the saved binaries, then regenerate the manifest."""
import datetime,hashlib,json,pathlib
out=pathlib.Path(__file__).resolve().parent
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(name):return json.loads((out/name).read_text())
hal=sha(out/'artifacts/halxboxnt5.dll');bootvid=sha(out/'artifacts/xboxbvid.dll')
routine=read('binary-unit-tests.json');boundary=read('boundary-tests.json')
assert routine['hal_sha256']==boundary['hal_sha256']==hal
assert len(routine['tests'])==11 and len(boundary['tests'])==8
assert all(t['passed'] for t in routine['tests']+boundary['tests'])
audit=read('installed-kernel-binding-audit.json')
assert audit['records']['hal.dll']['sha256']==hal
assert audit['records']['bootvid.dll']['sha256']==bootvid
assert audit['records']['ntoskrnl.exe']['sha256']==boundary['kernel_sha256']
missing={c['source']:c['missing'] for c in audit['checks'] if c.get('missing')}
assert missing=={'ntoskrnl.exe':['KdPortGetByte','KdPortInitialize','KdPortPollByte','KdPortPutByte','KdPortRestore','KdPortSave']}
layout=read('layout-comparison.json');assert len(layout['checked_offsets'])==55
assert all(c['matches'] for c in layout['checked_offsets'])
patch=read('patch-check.json');assert patch['current_tree_matches_full_patch_chain']
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'source_base':patch['base'],'patched_source_tree':patch['result_tree'],
 'hal_sha256':hal,'test_groups_passed':19,'selected_matching_offsets':55,
 'actual_kernel_paths_executed_under_unicorn':['IRQ0 clock handler through selected NT5 time-update path','EOI up to IRET'],
 'native_xbox_windows_boot':False,'xemu_or_pc_vm_started_this_checkpoint':False,
 'full_interrupt_or_scheduler_validation':False,'binding_gate_passed':False,
 'remaining':['Six legacy debugger-port exports','Remaining ABI, software-interrupt and BIOS/TSS audit','Native loader and installed-volume validation','Xbox storage driver selection and traced kernel handoff']}
(out/'checkpoint.json').write_text(json.dumps(record,indent=2)+'\n')
files={str(p.relative_to(out)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts}
(out/'manifest.json').write_text(json.dumps({'utc':record['utc'],'files':files},indent=2)+'\n')
print(json.dumps({'files_hashed':len(files),'test_groups':19,'matching_offsets':55,'hal_sha256':hal,'binding_gate':'expected failure: six legacy debugger-port exports'}))
