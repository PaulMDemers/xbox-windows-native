"""Run one bounded test on an owned xemu snapshot; never connect to the console."""
from pathlib import Path
import argparse,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('--variant',choices=['good','bad-hal','bad-kernel'],default='good');p.add_argument('--normal',action='store_true');p.add_argument('--trace',action='store_true');p.add_argument('--corrupt',choices=['pfn','descriptor','free-link','system-pte','working-set','init-input','process-object','hash-page']);p.add_argument('--mapped-candidate',action='store_true');p.add_argument('--bad-profile',action='store_true');a=p.parse_args()
kit=Path(__file__).resolve().parent;root=kit.parent.parent;out=root/'work/runs'/a.run
assert not out.exists() and a.run.startswith('physical-processinit-') and '/' not in a.run and '\\' not in a.run
ps='C:/Users/Paul/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
cmd=[ps,'-NoProfile','-File',str(kit.parent/'native-windows-nt5-kernel/Invoke-Diagnostic.ps1'),'-RunId',a.run,'-Bios','C:/Emulators/xemu/system/bios/Complex_4627.bin','-Iso',str(kit.parent/'native-windows-build/artifacts/xwn-preflight-001.iso'),'-HddSource',str(root/f'work/physical-processinit-{a.variant}.qcow2'),'-FtpPort','4586','-MonitorPort','4584','-GdbPort','4585','-Seconds','150','-ManualCapture','-StopOnCaptureComplete']
if not a.normal:cmd+=['-EepromSource',str(root/'work/paging-v3-widescreen-eeprom.bin')]
with (root/'work'/f'{a.run}-harness.log').open('w') as log:
 proc=subprocess.Popen(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  time.sleep(40)
  negative=bool(a.corrupt or a.mapped_candidate or a.bad_profile)
  if a.trace or negative:
   script='test-mapped-candidate.py' if a.mapped_candidate or a.bad_profile else 'trace-early.py'
   args=[sys.executable,str(kit/script),'--gdb','4585','--monitor','4584','--ftp','4586','--reference',str(root/'work/runs/physical-processinit-wide-001/entry-check.json'),'--output',str(out/'entry-trace.json')]
   if a.corrupt:args+=['--corrupt',a.corrupt]
   if a.bad_profile:args+=['--bad-profile']
   subprocess.run(args,cwd=root,check=True)
  else:
   import ftplib,json,datetime
   with ftplib.FTP() as ftp:
    ftp.connect('127.0.0.1',4586,timeout=8);ftp.login('xbox','xbox');response=ftp.sendcmd(r'SITE EXEC E:\Applications\XWNLoader\default.xbe')
   (out/'launch.json').write_text(json.dumps({'emulator_only':True,'response':response})+'\n');time.sleep(18)
  if not negative:
   args=[sys.executable,str(kit/'capture-entry.py'),'--port','4584','--output',str(out/'entry-check.json')]
   if a.variant!='good':args+=['--unarmed' if a.variant=='bad-hal' else '--kernel-mismatch']
   subprocess.run(args,cwd=root,check=True)
  print('PASS '+a.run,flush=True)
 finally:
  if out.exists():(out/'capture-complete.signal').touch()
  code=proc.wait(timeout=200)
 assert code==0
