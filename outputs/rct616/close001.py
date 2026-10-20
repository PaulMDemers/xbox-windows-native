"""Close after actual NT5 data, clock alignment and cold-cleanup review."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
r=read('review001.json');assert r['passed']
for n in ['host-tests001.json','inheritance-review002.json','binary-review001.json',
 'media-review001.json','process-review001.json','event-timestamps002.json']:
 assert read(n)['passed'],n
s=read('ntfs-phase1.json');assert s['closed'] and s['exit_code']==0
h=read('serial-host001.json');assert h['closed'] and not h.get('error')
raw=read('raw-control-logs001.json');finish=int(raw['subjects'][1].split()[7])
stamps=[line.split() for line in raw['trace'].splitlines()
 if line.startswith(('COST_CALL ','COST_RETURN '))]
assert len(stamps)==128
assert all(int(p[3],16)<=finish for p in stamps if int(p[2],16)==1)
assert 'OWNED_TERMINATE' not in raw['sampler']
out.write_text(json.dumps(dict(closed=True,passed=True,cleanup_passed=True,
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,game_launched=False,
 evidence=r,all_phase1_returns_before_subject_done=True,
 scope='Original pixel-checked workload measurement coordination. CPU increments below coarse resolution; no RCT or zero-overhead conclusion.',
 console_state='Untouched; last dashboard/no owned hook.596 SOFTWARE cleanup cold-only.',
 pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
