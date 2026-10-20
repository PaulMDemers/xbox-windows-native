"""Close only after actual control, cleanup and exact-source gates."""
from pathlib import Path
import datetime,hashlib,json
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
r=read('review001.json');assert not r['passed'] and r['error']=='AssertionError()'
c=read('ntfs-cold1-002.json');assert c['complete'] and c['normal_shutdown_delta']==1 and c['source_unchanged'] and c['audit_unchanged']
assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in c['hives'])
assert len(r['cases'])==4
for n in ['host-tests001.json','binary-review001.json','media-review001.json','event-timestamps002.json','process-review001.json']:assert read(n)['passed'],n
s=read('ntfs-phase1.json');assert s['closed'] and s['exit_code']==0
for path,h in read('ntfs-preparation001.json')['inputs'].items():assert sha(Path(path.replace('/mnt/c/','C:/')))==h,path
for path,v in read('build001.json')['files'].items():
 p=Path(path.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256']
 if p.suffix in ['.c','.h','.S'] and (K/p.name).exists():assert p.read_bytes()==(K/p.name).read_bytes()
out.write_text(json.dumps(dict(closed=True,passed=False,cleanup_passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,game_launched=False,
 scope='Original busy/paced timer controls; full-subject call counts and separate sampled-window CPU. Not game CPU attribution, FPS or Xbox performance.',evidence=r,failure='Observed subject count window exceeded unchanged1s post-measurement allowance during log flushing.',
 pins={p.name:sha(p) for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
