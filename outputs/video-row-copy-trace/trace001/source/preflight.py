"""Freeze video measurement inputs; refusing reuse is part of the protocol."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];assert sys.argv[1]=='trace001';out=k/'trace001'
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
host=lambda s:Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
f=read(k/'fixture-trace001.json');b=read(k/'build-review.json')
assert not (out/'preflight.json').exists() and not (ws/'work/runs/nt5-vrow-trace001').exists()
assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
assert sha(ws/'work/video-row-copy-trace-trace001-seed.qcow2')==f['seed_sha256']
assert b['passed'] and sha(k/'build-review.json')==f['build_review_sha256']
assert sha(k/'probe.c')==b['source_sha256'] and sha(k/'artifacts/probe.exe')==b['probe_sha256'] and sha(k/'Build.ps1')==b['build_script_sha256']
for row in f['parents']:assert sha(host(row['path']))==row['sha256']
assert read(out/'before-configuration.json')['expected_configuration']
names=['probe.c','Build.ps1','review.py','build-review.json','common.py','prepare.py','preflight.py','atomic_json.py','configuration.py','cold-map.py','Run.ps1','supervise.py','audit.py','record-closure.py','DESIGN.md','SHADOW-DESIGN.md','trace.py','review-sites.py','sites.json','layouts.json','fixture-trace001.json']
snapshot=out/'source';snapshot.mkdir(exist_ok=False)
for n in names:(snapshot/n).write_bytes((k/n).read_bytes())
(out/'preflight.json').write_text(json.dumps(dict(passed=True,physical_access=False,debugger=True,ordinary_qualified=False,sources={n:sha(k/n) for n in names},probe_sha256=b['probe_sha256']),indent=2)+'\n')
print('Pinned fixed-driver video profile; no mode/driver/cache change')
