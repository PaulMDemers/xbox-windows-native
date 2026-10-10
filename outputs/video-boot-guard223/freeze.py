"""Freeze both prepared223 seeds and exact executable/source dependencies once."""
import ast,hashlib,json,pathlib,sys
k=pathlib.Path(__file__).resolve().parent;ws=k.parents[1]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
dest=k/'emulator-frozen.json';assert not dest.exists()
for p in k.glob('*.py'):ast.parse(p.read_text())
pins=read(k.parent/'video-resident-context222/emulator-frozen.json')
for p,h in pins.items():assert sha(ws/p)==h,p
extra=[*k.glob('*.py'),*k.glob('*.ps1'),k/'DESIGN.md',k/'preflight.json',k/'preflight002.json',
       k.parent/'video-reset-guard221/review.json',
       k.parent/'video-boot-layout219/build-review.json',
       k.parent/'native-windows-nt5-kernel/trace-entry.py',
       k.parent/'native-windows-prebuild/monitor_capture.py']
for case in ['control001','candidate001']:
    fixture=k/('fixture-'+case+'.json');f=read(fixture)
    assert f['prepared'] and not f['physical_access'] and f['inherited_null_policy'] is False
    assert sha(pathlib.Path(f['fixture_path_windows']))==f['seed_sha256']
    extra += [fixture,k.parent/'video-boot-layout219/artifacts/build001'/case/'xboxbvid.dll']
for p in extra:pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
dest.write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=True,frozen_inputs=len(pins),physical_access=False,launches=0)))
