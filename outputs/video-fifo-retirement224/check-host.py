"""Current authored source syntax and derivation review; no source replay or guest launch."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'host-review001.json';assert not dest.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
parsed=[]
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p));parsed.append(p.name)
for name,h in read(k/'runtime-derivation.json')['derived'].items():assert sha(k/name)==h,name
for name,h in read(k/'runtime-derivation.json')['parents'].items():assert sha(k.parent/'video-resident-context222'/name)==h,name
for name,h in read(k/'build002.json')['input_pins'].items():assert sha(k/name)==h,name
dest.write_text(json.dumps(dict(passed=True,python_syntax=parsed,runtime_derivation_exact=True,build002_inputs_exact=True,physical_access=False,guest_launch=False,source_sha256=sha(Path(__file__))),indent=2)+'\n');print('Current224 host source/pins PASS')
