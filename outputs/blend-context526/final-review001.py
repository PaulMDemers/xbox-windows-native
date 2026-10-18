"""Independent failure closeout: immutable bytes, absent results and process closure."""
import datetime,hashlib,json,subprocess,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
js=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=js(K/'physical-final001.json');pkg=js(K/'package001.json');c=js(K/'physical001-collection.json')
assert r['closed'] and not r['result_namespace_present'] and not r['arithmetic_characterization_passed'] and not r['register_observation_passed']
assert r['all_collected_mutable_files_unchanged'] and r['temporary_hook_removed'] and r['original_launcher_startup_and_720p_unchanged']
assert all(v['normal_shutdown_delta']==0 and not v['new_records'] and v['byte_identical_before_after'] for v in r['events'].values())
assert all(c['files']['/E/Applications/XWNBoot526a/'+n] is None for n in ['report.bin','refusal.bin','handoff.bin','context.bin'])
for n,h in pkg['dependencies'].items():assert sha(Path(n))==h,n
for row in pkg['files'].values():assert sha(Path(row['path']))==row['sha256']
for manifest in ['source-copy001.json','source-copy-closeout001.json']:
 for n,row in js(K/manifest).items():
  b=Path(row['parent']).read_bytes();assert hashlib.sha256(b).hexdigest()==row['parent_sha256']
  for a,z in row['substitutions']:b=b.replace(a.encode(),z.encode())
  assert b==(K/n).read_bytes()
s={n:js(K/('supervisor-'+n+'.json')) for n in ['stage','launch','observe','collect']};assert all(v['closed'] for v in s.values())
assert all(s[n]['completed'] for n in ['stage','launch','collect']) and not s['observe']['completed']
stop=js(K/'observer-stop001.json');assert stop['intentional_host_observer_stop'] and stop['hook_removed_first'] and stop['pid']==s['observe']['pid']
ids=[x['pid'] for x in s.values()];cmd='Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Id -in @('+','.join(map(str,ids))+') -or $_.ProcessName -like "xemu*" -or $_.ProcessName -like "qemu*" } | Select-Object Id,ProcessName | ConvertTo-Json -Compress'
p=subprocess.run(['pwsh','-NoProfile','-Command',cmd],capture_output=True,text=True,timeout=20,check=True);assert not p.stdout.strip(),p.stdout
p=subprocess.run(['wsl','-d','Ubuntu','--','ps','-eo','pid=,comm='],capture_output=True,text=True,timeout=20,check=True);assert not p.stderr.strip()
assert not any(row.split()[-1].startswith(('qemu','xemu','nbdfuse')) for row in p.stdout.splitlines() if row.split())
files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path('C:/xwn526').rglob('*') if p.is_file()}
for n,row in r['private_files'].items():
 p=Path(n.replace('/mnt/c/','C:/',1));assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
obs=js(K/'physical001-observation.json');dash=sum(v['dashboard'] for v in obs['observations']);timeouts=len(obs['observations'])-dash
z=dict(review_passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_workload_passed=False,closed=True,physical_launches=1,all_owned_processes_closed=True,supervisors=s,observer_intentionally_stopped=True,observer_completed=False,observation_dashboard_count=dash,observation_transport_timeout_count=timeouts,transport_timeouts_overlap_collection='may reflect concurrent FTP, not evidence of Windows/crash',hook_removed=True,original_launcher_startup_720p_unchanged=True,console_last_observed=c['ended_utc'],frozen_dependencies=len(pkg['dependencies']),private_files_verified=len(files),private_files=files,console_C_accessed=False,queued_launch=False,physical_boot_failure_cause_unknown=True,absence_proves_no_entry=False,capacity_free_bytes={d:shutil.disk_usage(d+':/').free for d in ['C','E']},source_sha256=sha(Path(__file__)))
out.write_bytes((json.dumps(z,indent=2)+'\n').encode());print({n:z[n] for n in ['review_passed','physical_workload_passed','all_owned_processes_closed','observation_dashboard_count','observation_transport_timeout_count','frozen_dependencies','private_files_verified']})
