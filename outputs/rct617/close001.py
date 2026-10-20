"""Freeze qualified continuous-work evidence; do not reopen the runtime."""
import hashlib,json,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda p:Path(p.replace('/mnt/c/','C:/'))
for n in ['review001.json','host-tests002.json','binary-review001.json','media-review001.json',
          'event-timestamps002.json','process-review001.json']:
 assert read(n)['passed'],n
for p,h in read('ntfs-preparation001.json')['inputs'].items():assert sha(host(p))==h,p
for n,h in read('host-tests002.json')['sources'].items():assert sha(K/n)==h,n
for p,v in read('build001.json')['files'].items():
 path=host(p);assert sha(path)==v['sha256']
 if path.suffix in ['.c','.h'] and path.name!='target_iat.h':assert path.read_bytes()==(K/path.name).read_bytes()
raw=read('raw-control-logs001.json');assert 'OWNED_TERMINATE' not in raw['sampler']
state=read('ntfs-phase1.json');assert state['closed'] and state['exit_code']==0
assert read('serial-host001.json')['closed']
out.write_text(json.dumps(dict(closed=True,passed=True,cleanup_passed=True,
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,game_launched=False,
 evidence=read('review001.json'),scope='Continuously running original workload timing/identity control, not retail performance.',
 pins={p.name:sha(p) for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
