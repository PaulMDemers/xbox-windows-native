"""Closeout rehash of the isolated capture test and the resumed work window."""
import hashlib,json,subprocess,tomllib
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'closeout001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
code=r'''import hashlib,json
from pathlib import Path
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/cpu-context489')
b=json.loads((k/'build001.json').read_text());r=json.loads((k/'run001.json').read_text())
assert r['closed'] and r['passed']
for p,h in b['inputs'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
for rows in (b['files'],r['files']):
 for p,h in rows.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h['sha256'],p
alive=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:s=p.read_bytes()
 except (FileNotFoundError,PermissionError,ProcessLookupError):continue
 if b'qemu-system-i386' in s.split(b'\0')[0] and b'xwn-cpu-context489-' in s:alive.append(int(p.parent.name))
assert not alive
print(json.dumps(dict(passed=True,input_pins=len(b['inputs']),private_files=len(b['files'])+len(r['files']),owned_qemu_alive=alive)))
'''
r=subprocess.run(['wsl','-d','Ubuntu','--','python3','-B','-c',code],capture_output=True,text=True,timeout=60);assert r.returncode==0,r.stderr
a=tomllib.loads(Path('C:/Users/Paul/.codex/automations/xbox-emulator-development-until-10am/automation.toml').read_text(encoding='utf-8-sig'))
assert a['status']=='ACTIVE' and '14:00 UTC' in a['prompt']
record=dict(passed=True,physical_access=False,review_sha256=sha(K/'final-review.json'),source_sha256=sha(Path(__file__)),rehash=json.loads(r.stdout),automation=dict(id=a['id'],status=a['status'],cutoff_utc='2026-10-18T14:00:00Z',closeout_only_from_utc='2026-10-18T13:50:00Z',timezone='America/New_York'))
out.write_text(json.dumps(record,indent=2)+'\n')
