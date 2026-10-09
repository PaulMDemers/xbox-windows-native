"""Bind closed diagnostic and current startup-only hardware protocol; no network/launch."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'evidence-review.json';assert not dest.exists()
f=read(k/'frozen-inputs.json')
for name,digest in f.items():assert sha(ws/name)==digest,name
o=read(k/'emulator001/observation.json');a=read(k/'emulator001/audit.json');closed=read(k/'emulator001/closure.json')
assert closed['closed'] and a['diagnostic_usable'] and not a['ordinary_qualified'] and not a['strict_qualification_passed']
assert len(o['samples'])==5 and o['elapsed_ms']>=120000
late=o['samples'][1:]
assert all(s['install_state_begin']==258 and s['install_state_end']==258 for s in late)
assert all(any('newdev.dll,DevInstall PCI\\VEN_10DE&DEV_01B0' in p.get('command_utf16','') for p in s['processes']) for s in late)
assert all(any(w.get('window_text')=='Multimedia Audio Controller' for w in s['windows']) for s in late)
assert all(all(v.get('free_apis_agree') for v in s['volumes']) for s in o['samples'])
assert a['normal_shutdown_count']==0 and not a['strict_events_passed']
ready=read(k/'physical-ready.json')
for name,digest in ready['pins'].items():assert sha(ws/name)==digest,name
assert not (k/'physical.json').exists()
run=ws/'work/runs/nt5-observe188-emulator001';assert (run/'cleanup.json').exists()
r=dict(passed=True,physical_access=False,physical_launch_performed=False,ordinary_qualified=False,strict_qualification_passed=False,
       observation_sha256=sha(k/'emulator001/observation.json'),audit_sha256=sha(k/'emulator001/audit.json'),closure_sha256=sha(k/'emulator001/closure.json'),
       emulator_source_inputs_checked=len(f),physical_protocol_inputs_checked=len(ready['pins']),actual_owner='rundll32 newdev.dll,DevInstall PCI10DE:01B0',
       late_samples=4,late_window_records=sum(len(s['windows']) for s in late),elapsed_ms=o['elapsed_ms'],
       screenshot_sha256=sha(k/'emulator001/artifacts/observation-framebuffer.png'),
       warning='Inherited Ftdisk49 remains strict failure; bounded host closure is not normal shutdown. Emulated volume free space is not physical capacity.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Closed diagnostic and current',len(ready['pins']),'physical protocol inputs reviewed; no hardware boot')
