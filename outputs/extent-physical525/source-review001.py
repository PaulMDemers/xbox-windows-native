import hashlib,json,datetime
from pathlib import Path
K=Path('outputs/extent-physical525'); out=K/'source-review001.json'
assert not out.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((K/'source-copy001.json').read_text())
for name,row in manifest.items():
 b=Path(row['parent']).read_bytes(); assert sha(b)==row['parent_sha256']
 for a,c in row['substitutions']: b=b.replace(a.encode(),c.encode())
 assert b==(K/name).read_bytes() and sha(b)==row['sha256'],name
pkg=json.loads((K/'package001.json').read_text())
for n,h in pkg['dependencies'].items(): assert sha(Path(n).read_bytes())==h,n
fixture=Path('C:/xwn524/cold001/entry.bin'); assert fixture.stat().st_size==112
assert (K/'entry_decode.py').read_bytes()==Path('outputs/entry-receipt498/decode.py').read_bytes()
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reconstructed_sources=len(manifest),pinned_dependencies=len(pkg['dependencies']),fixture_sha256=sha(fixture.read_bytes()),fixture_bytes=112,physical_access=False)
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
