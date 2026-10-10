"""Freeze reviewed pair only after both unique preparations; guards prohibit reuse."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'emulator-frozen.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert read(k/'build-review002.json')['passed'] and read(k/'parser-tests001.json')['passed']
pins=read(k.parent/'video-resident-context222/emulator-frozen.json')
for name,h in pins.items():assert sha(ws/name)==h,name
for p in k.rglob('*'):
    if p.is_file() and not any(part in ['artifacts','__pycache__','control001','candidate001'] for part in p.relative_to(k).parts) and p.suffix in ['.py','.ps1','.h','.c','.json','.md']:
        pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
for case in ['control001','candidate001']:
    f=read(k/('fixture-'+case+'.json'));assert f['prepared'] and not f['inherited_null_policy'] and not f['guest_launch']
    assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
    p=k/'artifacts/build002'/case/'resident.sys';assert sha(p)==read(k/'build-review002.json')['binaries'][case]['sha256']
    pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
for p in [k/'artifacts/build002/probe.exe',k.parent/'xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe']:
    pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
for row in read(k/'build-review002.json')['providers'].values():
    assert sha(ws/row['path'])==row['sha256'];pins[row['path'].replace('\\','/')]=row['sha256']
dest.write_text(json.dumps(pins,indent=2)+'\n');print('Frozen224 inputs',len(pins))
