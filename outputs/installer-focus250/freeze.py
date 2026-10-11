"""Freeze fresh child and unchanged complete248 inputs before one launch."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'emulator-frozen.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((k.parent/'installer-focus249/emulator-frozen.json').read_text())
for name,digest in pins.items():assert sha(ws/name)==digest,name
assert json.loads((k/'diagnostic-test003.json').read_text())['passed']
assert json.loads((k/'source-review001.json').read_text())['passed']
for p in k.rglob('*'):
 if p.is_file() and ('artifacts' in p.parts or p.suffix in ['.py','.ps1','.md','.json','.c','.h']):
  if p.suffix=='.py':ast.parse(p.read_text())
  pins[p.relative_to(ws).as_posix()]=sha(p)
dest.write_text(json.dumps(pins,indent=2)+'\n');print('249 frozen',len(pins))
