"""Rehash a local-only watched comparison, leaving the console untouched."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'readiness-review001.json';assert not out.exists()
p=json.loads((K/'package001.json').read_text())
for name,h in p['dependencies'].items():assert sha(Path(name))==h,name
for row in p['files'].values():assert sha(Path(row['path']))==row['sha256']
free={d:shutil.disk_usage(d+':/').free for d in ['C','E']}
reserve=32*1024**2
assert all(n-reserve>=20*1024**3 for n in free.values())
assert not (K/'physical001-stage.json').exists()
r=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),dependencies=len(p['dependencies']),payloads=len(p['files']),
 free_bytes=free,collection_reserve_bytes=reserve,uploaded=False,launched=False,
 hardware_observation_needed='Watch Xromwell / Windows startup / desktop or black-return sequence on one fresh launch',
 next='Refresh capacity/pins, stage/readback once, then launch once when user is watching; never rerun456')
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r))
