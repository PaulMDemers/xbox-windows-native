"""Pin the observed native display and retained failed build before game launch."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn603/pc001/phase1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
out=K/'setup-review001.json';assert not out.exists()
img=P/'screen-1792467845532203666.png';data=img.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(1024,768)
assert read(K/'build001.json')['status']=='failed' and read(K/'build002.json')['status']=='compiled'
assert read(K/'asset-header-review001.json')['passed'] and read(K/'scene-tests001.json')['passed']
assert read(K/'media-review001.json')['passed']
out.write_text(json.dumps(dict(passed=True,observed='Native Display Properties after confirmation:1024x768 HighColor16bit. Helper independently checks metrics before registry/game changes.',private_image=str(img),sha256=sha(img),
 preserved_failures=['Build001 misleading-indentation under -Werror;002 separates statements in new load_dialog002/input002/runner002 files, warning flags unchanged.'],
 media_warning='Original retail UDF File Set Terminator warning;503-file independent ISO/readback and exact media identity passed.',physical_access=False),indent=2)+'\n')
print('603 native display/setup recorded; game not yet launched')
