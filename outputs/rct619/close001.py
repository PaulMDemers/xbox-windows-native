"""Seal a prelaunch failure after normal restart and cold cleanup."""
from pathlib import Path
import datetime,hashlib,json
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text())
s=read('ntfs-phase1.json');c=read('ntfs-cold1-002.json')
assert s['closed'] and s['exit_code']==0 and not any(s.get(n) for n in ['host_quit','host_terminate','host_kill','deadline','space_stop'])
assert c['complete'] and c['audit_unchanged'] and c['source_unchanged'] and c['normal_shutdown_delta']==1
assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in c['hives'])
assert read('process-review001.json')['passed'] and read('event-timestamps002.json')['passed']
m=json.loads(Path('C:/xwn619/pc001/cold1-002/manifest.json').read_text())
assert not any(n.startswith(('xwn619/','xwn619-kit/')) for n in m)
assert not read('prelaunch-failure001.json')['workload_launched']
out.write_text(json.dumps(dict(closed=True,passed=False,cleanup_passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),workload_launched=False,physical_access=False,
 reason='Host serial parser case boundary failed prelaunch review. No sampler or game outcome.',
 normal_shutdown_delta=1,pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
