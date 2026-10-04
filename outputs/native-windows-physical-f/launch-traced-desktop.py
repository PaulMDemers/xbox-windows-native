"""One-shot desktop isolation: restore the exact cycle009 trace driver, no auto restart."""
import pathlib,ftplib,io,json,os,hashlib,datetime
k=pathlib.Path(__file__).resolve().parent;record=k/'physical-cycle-010.json'
assert not record.exists(),'Inspect the existing one-shot record before any retry'
sha=lambda b:hashlib.sha256(b).hexdigest()
good=json.loads((k/'physical-cycle-009.json').read_text());failed=json.loads((k/'physical-desktop-001.json').read_text())
assert good['native_probe_passed'] and failed['status']=='physical_b4_normal_miniport_desktop_run'
driver=(k/'artifacts/xboxvnt5-trace.sys').read_bytes();assert sha(driver)==good['miniport_sha256']
old_trace=(k/'artifacts/physical-video-trace-009.bin').read_bytes();assert sha(old_trace)==good['trace_sha256']
seed=b'XWN-VID-TRACE01\n'+bytes(4080)
r={'host':good['host'],'scope':__doc__,'launch_attempted':False,'hal_sha256':good['hal_sha256'],'miniport_sha256':sha(driver),'startup_sha256':failed['startup_sha256'],'trace_seed_sha256':sha(seed),'startup_restart_disabled':True,'prior_passing_probe_cycle':9}
def save():record.write_text(json.dumps(r,indent=2)+'\n')
def get(f,name,optional=False):
 b=io.BytesIO()
 try:f.retrbinary('RETR '+name,b.write)
 except ftplib.error_perm as e:
  if optional and str(e).startswith('550'):return None
  raise
 return b.getvalue()
with ftplib.FTP() as f:
 f.connect(r['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
 f.cwd('/E/Applications/XWNFBoot/loader');assert sha(get(f,'halxboxnt5.dll'))==r['hal_sha256']
 f.cwd('/F/documents and settings/all users/start menu/programs/startup');assert sha(get(f,'xwnsetup.cmd'))==r['startup_sha256']
 f.cwd('/F');assert sha(get(f,'xwn-report-v2.txt'))==good['report_sha256']
 f.cwd('/F/winnt/system32');assert get(f,'xwn-video-trace.bin')==old_trace
 f.cwd('/F/winnt/system32/drivers');assert sha(get(f,'xboxvnt5.sys'))==failed['miniport_sha256'];assert get(f,'xboxvnt5.xwn-trace9')==driver
 assert get(f,'xboxvnt5.xwn-new10',True) is None and get(f,'xboxvnt5.xwn-normal10',True) is None
 r.update(status='preconditions_verified',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
 try:
  f.storbinary('STOR xboxvnt5.xwn-new10',io.BytesIO(driver),blocksize=1024);assert get(f,'xboxvnt5.xwn-new10')==driver
  f.rename('xboxvnt5.sys','xboxvnt5.xwn-normal10');r['status']='normal_driver_backed_up';save()
  f.rename('xboxvnt5.xwn-new10','xboxvnt5.sys');assert get(f,'xboxvnt5.sys')==driver
  f.cwd('/F/winnt/system32');assert get(f,'xwn-video-trace.bin')==old_trace
  f.storbinary('STOR xwn-video-trace.bin',io.BytesIO(seed),blocksize=1024);assert get(f,'xwn-video-trace.bin')==seed
  f.cwd('/E/Applications/XWNFBoot');initial=json.loads((k/'physical-cycle-001.json').read_text())
  for name,key in [('default.xbe','launcher_sha256'),('freeldr.sys','loader_sha256')]:assert sha(get(f,name))==initial[key]
  r.update(status='awaiting_traced_desktop_photo',launch_attempted=True,launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=good['command']);save()
  try:r['reply']=f.sendcmd(r['command'])
  except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
  save();print(r)
 except Exception as e:r['error']=repr(e);save();raise
