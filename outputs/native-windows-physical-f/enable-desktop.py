"""After cycle009 PASS, restore the normal miniport and leave Windows running."""
import pathlib,json,hashlib,ftplib,io,os,datetime
k=pathlib.Path(__file__).resolve().parent
proof=json.loads((k/'physical-cycle-009.json').read_text())
assert proof.get('native_probe_passed') and proof.get('trace_collected') and proof.get('payload_bytes')==65537
validation=json.loads((k/'desktop-emulator-validation.json').read_text());assert validation['passed']
record=k/'physical-desktop-001.json';assert not record.exists(),'Do not repeat an uncertain deployment/launch'
old=b'@echo off\r\nC:\\xwnphys2.exe\r\n'
new=b'@echo off\r\nrem Physical storage probe passed; leave Windows running for display/input testing.\r\nexit\r\n'
driver=(k/'package/F/winnt/system32/drivers/xboxvnt5.sys').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(driver)==validation['miniport_sha256'] and sha(new)==validation['startup_sha256'] and proof['hal_sha256']==validation['hal_sha256']
def get(f,name,optional=False):
 b=io.BytesIO()
 try:f.retrbinary('RETR '+name,b.write)
 except ftplib.error_perm as e:
  if optional and str(e).startswith('550'):return None
  raise
 return b.getvalue()
r={'scope':__doc__,'host':proof['host'],'launch_attempted':False,'hal_sha256':proof['hal_sha256'],'miniport_sha256':sha(driver),'startup_sha256':sha(new)}
def save():record.write_text(json.dumps(r,indent=2)+'\n')
with ftplib.FTP() as f:
 f.connect(r['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
 f.cwd('/E/Applications/XWNFBoot/loader');assert sha(get(f,'halxboxnt5.dll'))==proof['hal_sha256']
 f.cwd('/F');assert sha(get(f,'xwn-report-v2.txt'))==proof['report_sha256'] and sha(get(f,'xwn-create-v2.bin'))==proof['payload_sha256']
 backup=get(f,'xwn-startup-v2.bak',True);assert backup in (None,old)
 f.cwd('/F/documents and settings/all users/start menu/programs/startup');assert get(f,'xwnsetup.cmd')==old
 f.cwd('/F/winnt/system32');assert sha(get(f,'xwn-video-trace.bin'))==proof['trace_sha256']
 f.cwd('/F/winnt/system32/drivers');assert sha(get(f,'xboxvnt5.sys'))==proof['miniport_sha256']
 assert get(f,'xboxvnt5.xwn-trace9',True) is None and get(f,'xboxvnt5.xwn-normal',True) is None
 r.update(status='preconditions_verified',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
 try:
  f.storbinary('STOR xboxvnt5.xwn-normal',io.BytesIO(driver),blocksize=1024);assert get(f,'xboxvnt5.xwn-normal')==driver
  f.rename('xboxvnt5.sys','xboxvnt5.xwn-trace9');r['status']='trace_driver_backed_up';save()
  f.rename('xboxvnt5.xwn-normal','xboxvnt5.sys');assert get(f,'xboxvnt5.sys')==driver
  f.cwd('/F')
  if backup is None:f.storbinary('STOR xwn-startup-v2.bak',io.BytesIO(old),blocksize=1024)
  assert get(f,'xwn-startup-v2.bak')==old
  f.cwd('/F/documents and settings/all users/start menu/programs/startup')
  f.storbinary('STOR xwnsetup.cmd',io.BytesIO(new),blocksize=1024);assert get(f,'xwnsetup.cmd')==new
  f.cwd('/E/Applications/XWNFBoot');initial=json.loads((k/'physical-cycle-001.json').read_text())
  for name,key in [('default.xbe','launcher_sha256'),('freeldr.sys','loader_sha256')]:assert sha(get(f,name))==initial[key]
  r.update(launch_attempted=True,launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='awaiting_desktop_photo',startup_restart_disabled=True,command=proof['command']);save()
  try:r['reply']=f.sendcmd(r['command'])
  except (OSError,EOFError) as e:r['uncertain_reply']=repr(e)
  save();print(r)
 except Exception as e:r['error']=repr(e);save();raise
