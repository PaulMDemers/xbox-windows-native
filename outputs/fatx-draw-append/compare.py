"""Summarize a completed control/load pair without inferring video speed or hardware stability."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text())
dest=k/'comparison.json';assert not dest.exists()
f=[read(k/('fixture-'+c+'.json')) for c in ['001','002']]
a=[read(k/c/'audit.json') for c in ['001','002']]
q=[read(k/c/'qualification.json') for c in ['001','002']]
assert all(v['passed'] for v in q)
assert f[0]['parent_fixture_sha256']==f[1]['parent_fixture_sha256']
p=[{v['path']:v['sha256'] for v in x['payloads']+x['preserved_payloads']} for x in f]
assert set(p[0])==set(p[1])
different=[n for n in p[0] if p[0][n]!=p[1][n]];assert different==['xwnidle/drawmode.txt']
assert p[0][different[0]]==hashlib.sha256(b'0').hexdigest() and p[1][different[0]]==hashlib.sha256(b'1').hexdigest()
assert f[0]['preserved_during_observer_staging']==f[1]['preserved_during_observer_staging']
files=[{v['id']:v['sha256'] for v in r['append_files']} for r in a];assert files[0]==files[1] and len(files[0])==16
r=dict(passed=True,physical_access=False,hardware_qualified=False,shared_parent_sha256=f[0]['parent_fixture_sha256'],staged_payload_differences=different,probe_sha256=read(k/'probe-review.json')['probe_sha256'],exact_files_total=32,append_operations_total=16384,exact_cold_bytes_total=sum(v['bytes'] for x in a for v in x['append_files']),drawing_total_frames=a[1]['drawing_end'][0][1],drawing_frames_overlapping_append_epochs=a[1]['drawing_end'][0][2],per_case_overlap=[row[4] for row in a[1]['drawing_records']],control_frames=a[0]['drawing_end'][0][1],elapsed_ms_observations=[v['elapsed_ms'] for v in a],qualification_sha256={c:hashlib.sha256((k/c/'qualification.json').read_bytes()).hexdigest() for c in ['001','002']},limits='One fresh control and one fresh GDI-load run; elapsed times are workload observations, not video throughput. Same cold file bytes do not exclude intermittent physical corruption. No first-install activity, direct GPU access or physical experiment.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
