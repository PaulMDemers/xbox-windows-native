"""Closeout verification, with no guest launch, collection or disk mutation."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn405')
assert not (K/'closure001.json').exists()
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
cases={};frozen=0
for name in ['emu001','emu002','emu004','emu005','emu006']:
    run=P/'runs'/('nt5-fresh405-'+name);exit=read(run/'host-exit.json');assert exit['closed'] and exit['passed'] and not exit['fallback_kill'] and exit['exit_code']==0
    assert (run/'cleanup.json').exists()
    audit=read(K/name/'audit.json');assert sha(run/'hdd.qcow2')==audit['disk_sha256']
    pins=read(K/name/'frozen.json')
    for path,h in pins.items():assert sha(W/path)==h,(name,path)
    frozen+=len(pins)
    cases[name]=dict(orderly_host=True,disk_sha256=audit['disk_sha256'],frozen_inputs=len(pins),normal_guest_restart=audit['checks']['normal_restart'],dashboard_return=audit['checks']['dashboard_return'],strict_qualification=False)
assert read(K/'emu003/capacity-refusal.json')['launch_sent'] is False
query="@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'xemu*' } | Select-Object ProcessId,Name) | ConvertTo-Json -Compress"
raw=subprocess.check_output(['pwsh','-NoProfile','-Command',query],text=True,timeout=30).strip()
processes=json.loads(raw) if raw else [];assert processes==[],processes
private={}
for p in P.rglob('*'):
    if p.is_file():private[p.relative_to(P).as_posix()]=dict(bytes=p.stat().st_size,sha256=sha(p))
with (K/'private-evidence001.json').open('x') as f:json.dump(dict(root=str(P),files=private,all_contents_private=True,credentials_not_for_distribution=True),f,indent=2);f.write('\n')
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_owned_emulators_closed=True,xemu_processes=processes,cases=cases,
       capacity_refused_case='emu003',total_frozen_checks=frozen,private_files_rehashed=len(private),physical_access=False,
       source404_unchanged=read(K/'installed-final001.json')['fresh404_source_unchanged'],
       final_normal_startup=read(K/'installed-final001.json')['normal_diagnostic_startup_absent'],
       final_disk='C:/xwn405/runs/nt5-fresh405-emu006/hdd.qcow2',
       final_disk_has_backing_chain=True,do_not_move_or_delete_backing_chain=True,
       functional_scoped_pass=read(K/'qualification001.json')['fresh_xbox_functional_scoped_pass'],strict_pass=False)
with (K/'closure001.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps(r))
