"""Rehash frozen artifacts and close actual owned lifetimes without qualification inflation."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda n:Path(n.replace('/mnt/c/','C:/'))
p=read('package001.json');cold=read('physical-final001.json');assert cold['closed'] and not cold['combined_scene_passed']
assert cold['temporary_hook_removed'] and cold['all_collected_mutable_files_unchanged']
for n,h in p['dependencies'].items():assert sha(Path(n))==h,n
for n,v in cold['private_files'].items():assert sha(host(n))==v['sha256'] and host(n).stat().st_size==v['bytes'],n
supervisors={n:read('supervisor-'+n+'.json') for n in ['stage','launch','observe','collect']}
assert all(v['closed'] and v['completed'] and not v['deadline_reached'] for v in supervisors.values())
assert read('physical001-observation.json')['deadline_reached']
assert read('process-closeout001.json')['passed']
pids=[str(v['pid']) for v in supervisors.values()]
command='$ids=@('+','.join(pids)+'); $rows=@(Get-Process -Id $ids -ErrorAction SilentlyContinue); if ($rows.Count) { $rows | Select-Object Id,ProcessName | ConvertTo-Json -Compress; exit 1 }; Write-Output "owned children absent"; exit 0'
q=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,timeout=20);assert q.returncode==0,q.stdout
r=dict(closed=True,review_passed=True,qualification_passed=False,actual_entry_proved=False,actual_Windows_result=False,
 original_720p_launcher_startup_unchanged=True,hook_removed=True,physical_requests=1,all_owned_processes_closed=True,
 frozen_dependencies=len(p['dependencies']),private_files_rehashed=len(cold['private_files']),
 pending_screen_observation=True,no_next_launch_queued=True,supervisor_child_pids=pids,
 created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),host_interfaces_modeled=True,
 failures_preserved=['entry-host001 offline fixture activated too early','physical001 missing all five native receipts and Windows namespace'],
 source_hashes={str(f):sha(f) for f in K.glob('*.py')})
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(r))
