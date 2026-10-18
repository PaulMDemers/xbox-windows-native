"""Rehash closed prototype and record its limited host-only scope."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
h=json.loads((K/'host001.json').read_text());v=json.loads((K/'review001.json').read_text());assert h['passed'] and h['closed'] and v['passed']
for n,d in h['files'].items():assert sha(Path(n.replace('/mnt/c/','C:/',1)))==d['sha256']
for n,d in h['source_pins'].items():assert sha(K/n)==d
identity=json.loads((K/'kernel-identity001.json').read_text())
for n,d in identity['pins'].items():assert sha(Path(n))==d
actual=json.loads(subprocess.check_output(['wsl','-d','Ubuntu','--','python3','-c','import hashlib,json,sys;from pathlib import Path;print(json.dumps({p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sys.argv[1:]}))',*h['tool_pins']],timeout=30))
assert actual==h['tool_pins']
ps=subprocess.run(['pwsh','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'xemu*' } | Select-Object ProcessId,Name) | ConvertTo-Json -Compress"],capture_output=True,text=True,check=True,timeout=30);assert ps.stdout.strip() in ('','[]')
q=subprocess.run(['wsl','-d','Ubuntu','--','pgrep','-a','qemu'],capture_output=True,text=True,timeout=30);assert q.returncode==1 and not q.stdout.strip()
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),closed_sessions=[99426],all_owned_processes_closed=True,private_files_verified=len(h['files']),source_pins_verified=len(h['source_pins']),compiler_tool_pins_verified=len(actual),identity_inputs_verified=len(identity['pins']),actual_host_cases=h['case_count'],reentries=h['case_count'],kernel_LED_delay_file_firmware_MODELED=True,physical_access=False,XBE_built=False,guest_prepared=False,guest_launched=False,SDK_or_shared_change=False,no_startup_hook=True,no_physical_launch_queued=True,scope='Host-only proposed kernel-API entry indicator; no hardware visibility or return proof')
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
