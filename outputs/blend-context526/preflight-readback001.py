import hashlib,json,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'preflight-readback001.json';assert not out.exists();r=json.loads((K/'preflight001.json').read_bytes())
for n,h in r['inputs'].items():assert hashlib.sha256(Path(n).read_bytes()).hexdigest()==h,n
out.write_bytes((json.dumps(dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prebuild_inputs_rehashed=len(r['inputs']),physical_access=False),indent=2)+'\n').encode());print('PASS',len(r['inputs']),'prebuild inputs remain exact')
