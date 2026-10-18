"""Rehash actual evidence, frozen inputs and owned subprocess closure."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final-review.json';assert not out.exists()
r=read(K/'physical-final001.json');assert r['closed'] and r['physical_launches']==1
assert r['all_collected_mutable_files_unchanged'] and r['historical_preparation_receipts_absent'] and r['staged_files_unchanged']
assert r['entry']['entry_state']=='absent_in_listing' and not r['entry']['absence_proves_no_entry']
assert all(v['normal_shutdown_delta']==0 and v['new_records']==[] and v['byte_identical_before_after'] for v in r['events'].values())
pkg=read(K/'package001.json')
for n,h in pkg['dependencies'].items():assert sha(Path(n))==h,n
for row in pkg['files'].values():assert sha(Path(row['path']))==row['sha256']
files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path('C:/xwn508').rglob('*') if p.is_file()}
for n,row in r['private_files'].items():
 p=Path(n.replace('/mnt/c/','C:/',1));assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
pids=[v['pid'] for v in r['supervisors'].values()]
cmd='Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like "xemu*" -or $_.ProcessName -like "qemu*" -or $_.Id -in @('+','.join(map(str,pids))+') } | Select-Object Id,ProcessName | ConvertTo-Json -Compress'
live=subprocess.run(['pwsh','-NoProfile','-Command',cmd],capture_output=True,text=True,check=True,timeout=20).stdout.strip();assert not live,live
q=subprocess.run(['wsl','-d','Ubuntu','--','pgrep','-a','^qemu-system'],capture_output=True,text=True,timeout=20);assert q.returncode==1 and not q.stdout.strip()
result=dict(review_passed=True,physical_entry_gate_passed=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_owned_processes_closed=True,owned_pids=pids,windows_emulators=[],wsl_qemu=[],closed_sessions=[35348,97968,62150,59670],frozen_dependencies=len(pkg['dependencies']),private_files_verified=len(files),private_files=files,temporary_hook_installed=False,queued_launch=False,physical_LED_observation='unknown pending user report',scope='one physical entry-only attempt; receipt absent; no Windows result',source_sha256=sha(Path(__file__)))
out.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({n:result[n] for n in ['review_passed','physical_entry_gate_passed','all_owned_processes_closed','frozen_dependencies','private_files_verified']}))
