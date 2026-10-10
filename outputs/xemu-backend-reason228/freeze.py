"""Freeze unique prepared227 source/build/fixture/observer inputs before launch."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'emulator-frozen.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
pins=read(k.parent/'video-fifo-retirement224/emulator-frozen.json')
for n,h in pins.items():assert sha(ws/n)==h,n
b=read(k/'build002.json');assert b['passed'] and b['borrowed_sources_restored']
t=read(k/'terminal-test001.json');assert t['passed']
assert t['source_sha256']==sha(k/'test-terminal.py') and t['test_sha256']==sha(k/'test-terminal.c')
assert t['compiled_source_sha256']==sha(k/'artifacts/build002/source/hw/xbox/nv2a/nv2a.c')
assert sha(k/'build.py')==b['source_sha256'] and sha(k/'patch.py')==b['patch_generator_sha256']
assert sha(k/'candidate002-source-pins.json')==b['source_manifest_sha256']
manifest=read(k/'candidate002-source-pins.json')
for name in ['build005.json','candidate005-source-pins.json','preserve227-build005.patch','emulator-frozen.json','trace001/closure.json']:
 p=k.parent/'xemu-backend-preserve227'/name;pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
for n in b['changed_sources']:
 p=k/'artifacts/build002/source'/n;assert sha(p)==manifest[n];pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
p=k/'artifacts/build002/xemu-preserve227.exe';assert sha(p)==b['executable_sha256'];pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
f=read(k/'fixture-trace001.json');assert f['prepared'] and sha(Path(f['fixture_path_windows']))==f['seed_sha256']
assert not f['inherited_null_policy']
for n in ['inventory002.json']:
 p=k.parent/'video-loader-handoff225'/n;pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
for row in read(k.parent/'video-loader-handoff225/inventory002.json')['binaries'].values():
 p=ws/row['path'];assert sha(p)==row['sha256'];pins[row['path']]=sha(p)
for p in k.iterdir():
 if p.is_file() and p.suffix in ['.py','.ps1','.md','.json','.patch']:
  if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
  pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
assert 'video-loader-preserve227' not in (k/'run-emulator.py').read_text()
assert 'quarantined=True' in (k/'trace.py').read_text()
dest.write_text(json.dumps(pins,indent=2)+'\n');print('Frozen227 inputs',len(pins))

