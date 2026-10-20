"""Pin the observed native Settings confirmation, separately from game evidence."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent
p=Path('C:/xwn599/pc001/phase1/screen-1792463229171742514.png')
data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(1024,768)
out=K/'display-review001.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,private_image=str(p),sha256=hashlib.sha256(data).hexdigest(),desktop_pixels=[1024,768],observed='Native Display Properties Settings shows1024by768 and High Color16bit, with confirmation dialog dismissed by Yes. Source is ownedPC599QMP capture, not a physicalconsole.',scope='Native PC setup observation; helper independently checks desktop metrics before game startup.'),indent=2)+'\n')
