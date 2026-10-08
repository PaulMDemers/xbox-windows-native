"""Freeze one fresh ordinary emulator attempt; no repeat launch."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['candidate001'];out=k/case
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
host=lambda s:Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
assert not (out/'preflight.json').exists() and not (ws/('work/runs/nt5-vtransfer-'+case)).exists()
f=read(k/('fixture-'+case+'.json'));r=read(k/'pe-review.json');assert r['passed'] and sha(k/'pe-review.json')==f['pe_review_sha256']
assert sha(k/'probe.c')==r['probe_source_sha256'] and sha(k/'artifacts/probe.exe')==r['probe_sha256']
assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
assert sha(ws/('work/video-transfer-cost-'+case+'-seed.qcow2'))==f['seed_sha256']
for row in f['parents']:assert sha(host(row['path']))==row['sha256']
assert read(out/'before-configuration.json')['expected_configuration']
assert read(k/'oracle-tests.json')['passed']
assert read(k/'protocol-tests.json')['passed']
for n,h in read(k/'protocol-tests.json')['pins'].items():assert sha(k/n)==h
assert sha(k/'Invoke-Exclusive.ps1')==read(k/'runner-review.json')['local_sha256']
for n,h in read(k/'oracle-tests.json')['pins'].items():assert sha(k/n)==h
paths=[p for p in k.iterdir() if p.is_file() and p.suffix in ['.py','.ps1','.c','.md','.json']]
snapshot=out/'source';snapshot.mkdir(exist_ok=False);pins={}
for p in paths:
 (snapshot/p.name).write_bytes(p.read_bytes());pins[p.name]=sha(p)
(out/'preflight.json').write_text(json.dumps(dict(passed=True,physical_access=False,debugger=False,sources=pins,probe_sha256=r['probe_sha256'],display_sha256=r['display_sha256'] if case=='candidate001' else r['control_display_sha256']),indent=2)+'\n',encoding='utf-8')
print('Frozen unique clipping probe and reviewed display payload')
