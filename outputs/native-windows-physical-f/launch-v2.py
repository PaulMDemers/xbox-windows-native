"""Deploy the emulator-validated explicit-error probe and launch once."""
import pathlib,json,hashlib,ftplib,io,os,datetime,socket
k=pathlib.Path(__file__).resolve().parent;record=k/'physical-cycle-002.json';assert not record.exists()
audit=json.loads((k.parent/'native-windows-extended-storage/nt5-physical-f-probe-v2-001-cold-audit.json').read_text())
assert audit['passed'] and b'XWN-V2-PASS' in audit['native_probe']['log'].encode()
previous=json.loads((k/'physical-cycle-001.json').read_text())
new=(k/'artifacts/xwnphys2.exe').read_bytes();fixture=json.loads((k/'emulator-fixture-v2.json').read_text())
assert hashlib.sha256(new).hexdigest()==next(v['sha256'] for v in fixture['files'] if v['path']=='xwnphys2.exe')
seed=b'XWN-V2-PENDING-20261004\r\n'.ljust(4096,b' ')
oldcmd=b'@echo off\r\nC:\\xwnphysical.exe\r\n';newcmd=b'@echo off\r\nC:\\xwnphys2.exe\r\n'
def get(f,name,optional=False):
 b=io.BytesIO()
 try:f.retrbinary('RETR '+name,b.write)
 except ftplib.error_perm as e:
  if optional and str(e).startswith('550'):return None
  raise
 return b.getvalue()
class FTP(ftplib.FTP):
 def ntransfercmd(self,*args,**kwargs):
  s,n=super().ntransfercmd(*args,**kwargs);s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return s,n
r={'host':previous['host'],'scope':'Physical pre-created report and explicit Win32 errors, v2','launch_attempted':False}
with FTP() as f:
 f.connect(r['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD']);f.cwd('/F')
 assert get(f,'xwn-create-v2.bin',True) is None
 settings=json.loads((k/'crash-restart-setting.json').read_text());system=(k/'artifacts/physical-system-no-auto-reboot').read_bytes()
 assert hashlib.sha256(system).hexdigest()==settings['target_sha256']
 f.cwd('/F/winnt/system32/config');original=get(f,'system',True);backup=get(f,'system.xwn-v1',True)
 assert original is None or hashlib.sha256(original).hexdigest() in (settings['source_sha256'],settings['target_sha256'])
 if backup is not None:assert hashlib.sha256(backup).hexdigest()==settings['source_sha256']
 if original is None or hashlib.sha256(original).hexdigest()!=settings['target_sha256']:
  assert original is not None or backup is not None
  for at in range(0,len(system),32768):f.storbinary(('STOR ' if at==0 else 'APPE ')+'system.xwn-v2',io.BytesIO(system[at:at+32768]),blocksize=1024)
  assert get(f,'system.xwn-v2')==system
  if original is not None:
   assert backup is None;f.rename('system','system.xwn-v1')
  f.rename('system.xwn-v2','system')
 assert get(f,'system')==system;r['crash_auto_restart_disabled']=True;r['system_sha256']=settings['target_sha256']
 f.cwd('/F')
 for name,data in [('xwnphys2.exe',new),('xwn-report-v2.txt',seed),('xwn-startup-v1.bak',oldcmd)]:
  existing=get(f,name,True);assert existing is None or (len(existing)<=len(data) and data.startswith(existing))
  f.storbinary('STOR '+name,io.BytesIO(data),blocksize=1024);assert get(f,name)==data
 f.cwd('/F/documents and settings/all users/start menu/programs/startup');assert get(f,'xwnsetup.cmd') in (oldcmd,newcmd)
 f.storbinary('STOR xwnsetup.cmd',io.BytesIO(newcmd),blocksize=1024);assert get(f,'xwnsetup.cmd')==newcmd
 f.cwd('/E/Applications/XWNFBoot')
 for name,digest in [('default.xbe',previous['launcher_sha256']),('freeldr.sys',previous['loader_sha256'])]:assert hashlib.sha256(get(f,name)).hexdigest()==digest
 r.update(launch_attempted=True,launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=previous['command'],probe_sha256=hashlib.sha256(new).hexdigest(),report_seed_sha256=hashlib.sha256(seed).hexdigest(),fresh_create_path_absent=True)
 record.write_text(json.dumps(r,indent=2)+'\n')
 try:r['reply']=f.sendcmd(r['command'])
 except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
 record.write_text(json.dumps(r,indent=2)+'\n');print(r)
