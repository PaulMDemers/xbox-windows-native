"""MIT. Read-only final host/automation state; no console operation."""
import datetime,json,shutil,subprocess,tomllib
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'closeout001.json';assert not out.exists()
state=json.loads((K.parent/'rct586/final002.json').read_text());assert state['closed'] and state['passed']
ps=subprocess.run(['wsl','-d','Ubuntu','-u','paul','--','ps','-eo','pid,comm,args'],capture_output=True,text=True,timeout=20,check=True)
owned=[]
for line in ps.stdout.splitlines():
 bits=line.strip().split(None,2)
 if len(bits)==3 and (bits[1].startswith(('qemu','xemu')) or bits[1].startswith('python') and any(x in bits[2] for x in ['/rct586/','/delivery587/'])):
  owned.append(dict(pid=int(bits[0]),name=bits[1]))
win=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object {($_.Name -match '^(qemu|xemu)') -or ($_.Name -match '^python' -and $_.CommandLine -match '(rct586|xwn586|xwn587|delivery587)' -and $_.CommandLine -notmatch 'closeout001.py')} | Select-Object ProcessId,Name) | ConvertTo-Json -Compress"],capture_output=True,text=True,timeout=30,check=True)
wp=json.loads(win.stdout) if win.stdout.strip() else []
auto=Path('C:/Users/Paul/.codex/automations/xbox-emulator-development-until-10am/automation.toml')
status=tomllib.loads(auto.read_text())['status']
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),owned_wsl_processes=owned,owned_windows_processes=wp,
 automation_status=status,console_access=False,console_last_observation='Dashboard FTP during read-only delivery capture; ordinary startup and protected720p verified',
 outstanding_owned_hook=False,pc586_closed=True,capacity={drive:shutil.disk_usage(drive).free for drive in ['C:/','E:/']})
r['passed']=not owned and not wp and status=='PAUSED'
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));assert r['passed']
