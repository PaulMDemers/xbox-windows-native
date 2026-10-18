"""Closeout of scoped kernel-file observation, never physical boot promotion."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'final-review.json';assert not out.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
pins=json.loads((K/'emu001/frozen.json').read_text())
for p,h in pins.items():assert sha(W/p)==h and sha(Path('C:/xwn524/frozen001')/p)==h,p
external=json.loads((K/'emu001/host-dependencies.json').read_text())
for p,h in external.items():assert sha(Path(p))==h,p
t=json.loads((K/'emu001/trace.json').read_text());a=json.loads((K/'emu001/audit.json').read_text());p=json.loads((K/'emu001/protected.json').read_text());v=json.loads((K/'actual-review001.json').read_text())
assert t['passed'] and v['passed'] and p['passed']
assert json.loads((K/'trampoline-review001.json').read_text())['passed']
assert t.get('dashboard_return_observed') and t['terminal_status']==[0]*6
assert t['original_start_not_executed']
assert a['host_exit']['passed'] and a['host_exit']['closed'] and not a['host_exit']['fallback_kill']
assert a['receipts']['entry.bin']['memory_exact'] and all(not a['receipts'][n]['present'] for n in ['report.bin','witness.bin','handoff.bin','context.bin','refusal.bin'])
assert a['source_unchanged'] and a['eeprom_unchanged'] and a['allocation']['allocation_consistent']
assert not t['remaining_breakpoints'] and t['physical_mode_restored'] and not t.get('cleanup_error')
inventory=subprocess.run(['pwsh','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'xemu*' } | Select-Object ProcessId,Name,ExecutablePath) | ConvertTo-Json -Compress"],capture_output=True,text=True,check=True,timeout=30).stdout.strip()
assert inventory in ('','[]'),inventory
q=subprocess.run(['wsl','-d','Ubuntu','--','pgrep','-a','qemu'],capture_output=True,text=True,timeout=30);assert q.returncode==1 and not q.stdout.strip()
files={str(f):sha(f) for f in Path('C:/xwn524').rglob('*') if f.is_file()}
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='actual emulator entry-only LED/delay/file/firmware contract and new control-return/cold-content contract only',all_owned_processes_closed=True,windows_xemu_processes=[],wsl_qemu_processes=[],closed_sessions=[],frozen_inputs=len(pins),external_inputs=len(external),private_files_verified=len(files),private_files=files,actual_calls=12,actual_checkpoints=len(t['checkpoints']),actual_captures=len(t['reads']),cold_receipt_exact=True,allocation_consistent=True,strict_whole_disk_equal=a['strict_whole_disk_equal'],changed_bytes=a['changed_bytes'],physical_access=False,physical_failure_explained=False,windows_started=False,ordinary_boot_qualified=False,normal_guest_shutdown=False,next_physical_launch_queued=False,dashboard_return_observed=True,overall_runtime_passed=True,live_ftp_content_qualified=False,actual_led_visibility_qualified=False)
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print({k:v for k,v in r.items() if k!='private_files'})
