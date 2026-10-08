"""Open cold collection only after both timed guests and leases are closed."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'audit-start.json';assert not dest.exists()
rows={}
for case in ['control001','candidate001']:
    p=ws/('work/runs/nt5-vtime156-'+case+'/cleanup.json');assert p.exists()
    assert json.loads((k/case/'performance-lease.json').read_text())['finished']
    assert not (k/case/'audit.json').exists()
    rows[case]=hashlib.sha256(p.read_bytes()).hexdigest()
dest.write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cleanup_sha256=rows),indent=2)+'\n')
print('Both guests closed before cold collection')
