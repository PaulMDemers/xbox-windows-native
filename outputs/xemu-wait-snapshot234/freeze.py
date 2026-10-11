"""Freeze unique229 source and exact228 compiled-byte inputs before launch."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'emulator-frozen.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
pins=read(k.parent/'xemu-wait-lifecycle233/emulator-frozen.json')
for name,digest in pins.items():assert sha(ws/name)==digest,name
f=read(k/'fixture-trace002.json');assert f['prepared'] and not f['inherited_null_policy'] and sha(Path(f['fixture_path_windows']))==f['seed_sha256']
b=read(k/'build001.json');assert b['passed'] and b['borrowed_sources_restored']
for p in (k/'artifacts/build001').rglob('*'):
 if p.is_file():pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
for p in k.iterdir():
 if p.is_file() and p.suffix in ['.py','.ps1','.md','.json']:
  if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
  pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
assert 'credentials required BEFORE instance creation' in (k/'run-emulator.py').read_text()
dest.write_text(json.dumps(pins,indent=2)+'\n');print('Frozen229 pins',len(pins))
