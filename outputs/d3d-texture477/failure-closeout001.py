"""Preserve the malformed-floppy attempt and normal UI-requested shutdown."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
out=K/'final-review.json';assert not out.exists()
s=read(K/'ntfs-phase1.json');c=read(K/'ntfs-cold1-002.json');prep=read(K/'ntfs-preparation001.json')
P=Path(prep['path']);manifest=read(Path(c['private_path'])/'manifest.json')
assert s['closed'] and s['exit_code']==0 and not s['deadline'] and not any(s.get(k) for k in ['host_quit','host_terminate','host_kill'])
assert c['complete'] and c['normal_shutdown_delta']==1 and c['source_unchanged'] and c['audit_unchanged']
assert not any(n.startswith('xwn477/') for n in manifest)
assert sha(P/'probe.img')==prep['floppy_sha256'] and (P/'probe.img').stat().st_size==1477560
pins=read(K/'preflight001.json')['files'];pins.update({str(p):sha(p) for p in K.glob('*.py')})
capsule=Path('/home/paul/xbox-windows-native/d3d-texture477-failed-inputs001');assert not capsule.exists();capsule.mkdir()
archived={}
for i,(name,h) in enumerate(sorted(pins.items())):
    p=Path(name);assert sha(p)==h;dest=capsule/f'{i:03d}-{p.name}';dest.write_bytes(p.read_bytes());assert sha(dest)==h
    archived[name]=dict(path=str(dest),sha256=h)
assert not list(P.glob('phase*/qmp.sock'))
r=dict(closed=True,scoped_texture_passed=False,sample_executed=False,normal_restart=True,
    restart_origin='Manually selected Restart through owned guest Windows Security UI',
    failure='Namespace generator replaced 1474560 with1477560; malformed floppy; guest DIR A: showed no files',
    input_timing_change='Added explicit20ms key holds/200ms spacing. It did not repair the malformed floppy and is not proved causal.',
    cold_files=c['files'],cold_directories=c['directories'],normal_shutdown_delta=c['normal_shutdown_delta'],
    source_unchanged=c['source_unchanged'],floppy_unchanged=s['floppy_unchanged'],frozen_inputs=archived,
    new_system_events=c['new_system_events'],hives=c['hives'],physical_access=False,
    private_files={str(p):sha(p) for folder in (P,capsule) for p in folder.rglob('*') if p.is_file()},
    limitations=['No texture test or process result','No full NTFS allocation audit','No independent second filesystem reader for this failed attempt'])
out.write_text(json.dumps(r,indent=2)+'\n');print('477 failed boot-control closed; no sample results, normal restart and cold audit preserved')
