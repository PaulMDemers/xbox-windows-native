# SPDX-License-Identifier: MIT
"""Closed host/build/review input rehash and process inventory."""
import datetime,hashlib,json,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=K/'final-review.json';assert not O.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();js=lambda p:json.loads(p.read_bytes())
def mapped(n):return Path(n.replace('/mnt/c/','C:/',1))
h=js(K/'host001.json');b=js(K/'build001.json');r=js(K/'review001.json')
assert h['passed'] and h['closed'] and b['status']=='compiled' and r['passed'] and not r['deployed']
pins={}
for n,v in h['inputs'].items():pins[str(mapped(n))]=v
for n,v in b['inputs'].items():
    if n.startswith('/usr/'):
        actual=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum',n],text=True,timeout=20).split()[0];assert actual==v
    else:pins[str(mapped(n))]=v
for n,v in r['inputs'].items():pins[str(mapped(n))]=v['sha256']
for n,v in pins.items():assert sha(Path(n))==v,n
for record in [b['files'],r['private_files']]:
    for n,v in record.items():p=mapped(n);assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes']
files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path('C:/xwn520').rglob('*') if p.is_file()}
live=subprocess.check_output(['pwsh','-NoProfile','-Command','Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like "xemu*" -or $_.ProcessName -like "qemu*" } | Select-Object Id,ProcessName | ConvertTo-Json -Compress'],text=True,timeout=20).strip();assert not live
q=subprocess.run(['wsl','-d','Ubuntu','--','pgrep','-a','^qemu-system'],capture_output=True,text=True,timeout=20);assert q.returncode==1 and not q.stdout.strip()
capacity={d:shutil.disk_usage(d+':/').free for d in ['C','E']}
result=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='host byte contract and actual built artifact only; never launched',candidate_path='C:/xwn520/build001/default.xbe',candidate_sha256=b['sha256'],candidate_bytes=b['bytes'],inputs_rehashed=len(pins),private_files_rehashed=len(files),private_files=files,all_owned_processes_closed=True,closed_sessions=['62494 exit0','build synchronous exit0','review synchronous exit0'],physical_access=False,emulator_preparation=False,guest_launch=False,deployed=False,temporary_hook=False,queued_launch=False,capacity_free_bytes=capacity,existing_768MiB_emulator_guard_passes=capacity['C']-768*1024**2>=20*1024**3,source_sha256=sha(Path(__file__)))
O.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({n:result[n] for n in ['passed','inputs_rehashed','private_files_rehashed','existing_768MiB_emulator_guard_passes']}))
