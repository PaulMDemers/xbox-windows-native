"""Freeze all new inputs plus unchanged238 compiled inputs before launch."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'emulator-frozen.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((k.parent/'gpu-preserve-entry240/emulator-frozen.json').read_text(encoding='utf-8'))
for path,digest in pins.items():assert sha(ws/path)==digest,path
for p in k.rglob('*'):
 if p.is_file() and 'artifacts' not in p.parts and p.suffix in ['.py','.ps1','.md','.json','.c']:
  if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
  pins[p.relative_to(ws).as_posix()]=sha(p)
for root in ['source','artifacts/inputs','artifacts/ram-source','artifacts/build001']:
 for p in (k/root).rglob('*'):
  if p.is_file():pins[p.relative_to(ws).as_posix()]=sha(p)
dest.write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8');print('239 frozen',len(pins))
