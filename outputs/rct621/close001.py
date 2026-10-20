"""Close only after actual control, cleanup and exact-source gates."""
from pathlib import Path
import datetime,hashlib,json
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
r=read('review001.json');assert r['passed'] and r['cleanup_passed']
for n in ['host-tests002.json','binary-review001.json','media-review002.json','copy-contract-tests003.json','scene-tests001.json','visual-review001.json','event-timestamps002.json','process-review001.json','seed-symbols001.json','site-symbols001.json']:assert read(n)['passed'],n
s=read('ntfs-phase1.json');assert s['closed'] and s['exit_code']==0
for path,h in read('ntfs-preparation001.json')['inputs'].items():assert sha(Path(path.replace('/mnt/c/','C:/')))==h,path
for path,v in read('build002.json')['files'].items():
 p=Path(path.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256']
 if p.suffix in ['.c','.h','.S'] and (K/p.name).exists():assert p.read_bytes()==(K/p.name).read_bytes()
out.write_text(json.dumps(dict(closed=True,passed=True,cleanup_passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,game_launched=True,
 scope='Matched paused PC RCT saved-user-instruction locations and separate process/main-thread/observer CPU. Not CPU-time sample percentages, kernel attribution, FPS or Xbox performance.',evidence=r,
 pins={p.name:sha(p) for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
