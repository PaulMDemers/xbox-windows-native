"""Freeze unique matched video mapping case; refuse reuse."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['trace002'];out=k/case
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
host=lambda s:Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
f=read(k/('fixture-'+case+'.json'));b=read(k/'build-review.json')
assert not (out/'preflight.json').exists() and not (ws/('work/runs/nt5-vsharetrace2-'+case)).exists()
assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
assert sha(ws/('work/video-shared-trace2-'+case+'-seed.qcow2'))==f['seed_sha256']
assert b['passed'] and sha(k/'build-review.json')==f['build_review_sha256']
assert sha(k/'probe.c')==b['source_sha256'] and sha(k/'artifacts/probe.exe')==b['probe_sha256']
for row in f['parents']:assert sha(host(row['path']))==row['sha256']
assert read(out/'before-configuration.json')['expected_configuration']
assert sha(k/'pe-review.json')==f['pe_review_sha256'] and read(k/'pe-review.json')['passed']
assert sha(out/'build.json')==f['case_build_sha256']
for row in read(out/'build.json')['files']:assert sha(out/'artifacts'/row['name'])==row['sha256']
patch=read(k/'patch-review.json');assert sha(k/'0106-shared-uc-framebuffer.patch')==patch['patch_sha256']
for n,h in patch['authored_sources'].items():assert sha(k/n)==h
names=[p.name for p in k.iterdir() if p.is_file() and p.suffix in ['.py','.ps1','.c','.h','.md','.patch','.json'] and not p.name.startswith('fixture-')]+['fixture-'+case+'.json']
snapshot=out/'source';snapshot.mkdir(exist_ok=False)
for n in names:(snapshot/n).write_bytes((k/n).read_bytes())
(out/'preflight.json').write_text(json.dumps(dict(passed=True,physical_access=False,debugger=True,ordinary_qualified=False,sources={n:sha(k/n) for n in names},probe_sha256=b['probe_sha256']),indent=2)+'\n')
print('Pinned matched video mapping experiment; no physical access')
