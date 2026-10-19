"""MIT. Check inherited readiness constants against independently derived record."""
import hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent;parent=K.parent/'rct570';out=K/'source-review001.json'
assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=(K/'title_signature.h').read_bytes();b=(parent/'title_signature.h').read_bytes()
assert a.replace(b'\r\n',b'\n')==b.replace(b'\r\n',b'\n')
reference=json.loads((parent/'title-reference001.json').read_text())
actual=[tuple(int(n,0) for n in row) for row in re.findall(r'\{(\d+),(\d+),(0x[0-9a-f]+)UL\}',a.decode())]
assert actual==[(r['x'],r['y'],r['fnv']) for r in reference['rectangles']]
out.write_text(json.dumps(dict(passed=True,initial_strict_byte_comparison_failed=a!=b,reason='Source copier normalized CRLF to LF; title coordinates and signatures are unchanged.',parent_reference_sha256=sha(parent/'title-reference001.json'),parent_header_sha256=sha(parent/'title_signature.h'),compiled_header_sha256=sha(K/'title_signature.h'),runtime_positive_unqualified=True,physical_access=False),indent=2)+'\n')
