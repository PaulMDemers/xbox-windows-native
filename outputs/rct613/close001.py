"""Close only with exact original counter evidence and durable normal shutdown."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
host=lambda p:Path(p.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
r=read('review001.json')
assert r['passed'] and r['cleanup_passed']
for n in ['binary-review001.json','media-review001.json','oracle-tests001.json','process-review001.json','event-timestamps002.json']:
 assert read(n)['passed'],n
prep=read('ntfs-preparation001.json')
for p,h in prep['inputs'].items():assert sha(host(p))==h,p
assert sha(K/'sampler-build001.c')==read('build001.json')['source_sha256']
assert sha(K/'sampler.c')==read('build002.json')['source_sha256']
for p,v in read('build002.json')['files'].items():assert sha(host(p))==v['sha256'],p
state=read('ntfs-phase1.json');assert state['closed'] and state['exit_code']==0
out.write_text(json.dumps(dict(closed=True,passed=True,cleanup_passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 evidence=r,capture_errors=state.get('capture_errors',[]),physical_access=False,
 scope='Original PC TCG guest counter consistency and sampling-cost control. No game performance, host-clock calibration, Xbox result or instrumentation-overhead comparison.',
 console_state='Untouched; last dashboard/no owned hook.596 SOFTWARE cleanup remains cold-only.',
 pins={p.name:sha(p) for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
print('613 CLOSED PASS')
