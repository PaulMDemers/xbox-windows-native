"""After physical probe PASS, disable its startup restart and launch once for viewing."""
import pathlib,json,hashlib,ftplib,io,os,datetime
k=pathlib.Path(__file__).resolve().parent
proof=json.loads((k/'physical-cycle-001.json').read_text())
assert proof.get('native_storage_passed') and proof.get('fresh_native_report_retrieved')
record=k/'physical-desktop-001.json';assert not record.exists(),'Do not repeat an uncertain launch'
old=b'@echo off\r\nC:\\xwnphysical.exe\r\n'
new=b'@echo off\r\nrem Physical storage probe passed; leave Windows running for display/input testing.\r\nexit\r\n'
def get(f,name,optional=False):
 b=io.BytesIO()
 try:f.retrbinary('RETR '+name,b.write)
 except ftplib.error_perm as e:
  if optional and str(e).startswith('550'):return None
  raise
 return b.getvalue()
r={'scope':'Physical desktop viewing launch after successful native storage test','host':proof['host'],'launch_attempted':False}
with ftplib.FTP() as f:
 f.connect(r['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD']);f.cwd('/F')
 log=get(f,'xwn-physical.log');assert hashlib.sha256(log).hexdigest()==proof['log_sha256']
 backup=get(f,'xwn-physical-startup.bak',True);assert backup in (None,old)
 if backup is None:f.storbinary('STOR xwn-physical-startup.bak',io.BytesIO(old),blocksize=1024)
 assert get(f,'xwn-physical-startup.bak')==old
 f.cwd('/F/documents and settings/all users/start menu/programs/startup')
 assert get(f,'xwnsetup.cmd') in (old,new)
 f.storbinary('STOR xwnsetup.cmd',io.BytesIO(new),blocksize=1024);assert get(f,'xwnsetup.cmd')==new
 f.cwd('/E/Applications/XWNFBoot')
 for name,digest in [('default.xbe',proof['launcher_sha256']),('freeldr.sys',proof['loader_sha256'])]:
  assert hashlib.sha256(get(f,name)).hexdigest()==digest
 r.update(launch_attempted=True,launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),startup_restart_disabled=True,startup_sha256=hashlib.sha256(new).hexdigest(),command=proof['command'])
 record.write_text(json.dumps(r,indent=2)+'\n')
 try:r['reply']=f.sendcmd(r['command'])
 except (OSError,EOFError) as e:r['uncertain_reply']=repr(e)
 record.write_text(json.dumps(r,indent=2)+'\n');print(r)
