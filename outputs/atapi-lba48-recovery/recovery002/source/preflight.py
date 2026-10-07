"""Freeze the unique recovery child and all exact input identities."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];assert sys.argv[1]=='recovery002';out=k/'recovery002'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda s:Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
f=read(k/'fixture-recovery002.json')
assert not (out/'preflight.json').exists()
assert not (ws/'work/runs/nt5-atapi-lba48-recovery-recovery002').exists()
assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
assert sha(ws/'work/atapi-lba48-recovery-recovery002-seed.qcow2')==f['seed_sha256']
for row in f['parents']:assert sha(host(row['path']))==row['sha256']
assert read(k.parent/'atapi-lba48-crash/payload-verification.json')['passed']
assert sha(k.parent/'atapi-lba48-crash/payload-verification.json')==f['high_lba_gate_sha256']
assert read(out/'before-configuration.json')['expected_configuration']
review=read(k/'toolchain-review.json');assert sha(k/'artifacts/recovery-probe.exe')==review['recovery_helper_sha256']
for n,h in review['recovery_sources'].items():assert sha(k/n)==h
names=['helper-review.json','recovery-probe.c','Build-Recovery.ps1','toolchain-review.json','dumps.py','prepare.py','preflight.py',
       'common.py','atomic_json.py','configuration.py','cold-map.py','Run.ps1','supervise.py','audit.py',
       'record-closure.py','DESIGN.md','setup-origin.py','fixture-recovery002.json']
snapshot=out/'source';snapshot.mkdir(exist_ok=False)
for n in names:(snapshot/n).write_bytes((k/n).read_bytes())
(out/'preflight.json').write_text(json.dumps(dict(passed=True,physical_access=False,debugger=False,
    sources={n:sha(k/n) for n in names},helper_sha256=review['recovery_helper_sha256']),indent=2)+'\n')
print('Pinned one recovery boot; no crash trigger invocation')
