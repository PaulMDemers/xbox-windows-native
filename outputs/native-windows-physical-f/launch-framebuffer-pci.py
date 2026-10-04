"""Back up and readback-verify the validated framebuffer HAL, then launch once."""
import pathlib,ftplib,io,json,os,hashlib,datetime,socket
k=pathlib.Path(__file__).resolve().parent;record=k/'physical-cycle-009.json'
assert not record.exists(),'One-shot deployment record exists; inspect it instead of retrying'
sha=lambda b:hashlib.sha256(b).hexdigest()
new=(k/'artifacts/halxboxnt5-framebuffer.dll').read_bytes();digest=sha(new)
tests=json.loads((k/'framebuffer-pci-tests.json').read_text())
validation=json.loads((k/'framebuffer-pci-validation.json').read_text())
assert tests['passed'] and tests['hal_sha256']==digest
assert validation['passed'] and validation['hal_sha256']==digest
assert json.loads((k/'patch-check-0074.json').read_text())['clean_index_replay_verified']
old_hash='59c889e177cee82e34c8ded326bffc33a659881031d3e0f7a9616d69c77447eb'
previous=json.loads((k/'physical-cycle-001.json').read_text())
cycle8=json.loads((k/'physical-cycle-008.json').read_text());assert cycle8['trace_collected']
trace=(k/'artifacts/physical-video-trace-008.bin').read_bytes();assert sha(trace)==cycle8['trace_sha256']
trace_seed=b'XWN-VID-TRACE01\n'+bytes(4080)
r={'host':previous['host'],'scope':__doc__,'launch_attempted':False,'hal_sha256':digest,'original_hal_sha256':old_hash,'miniport_sha256':cycle8['miniport_sha256'],'backup':'/E/Applications/XWNFBoot/loader/halxboxnt5.xwn-v8','trace_seed_sha256':sha(trace_seed),'emulator_run':validation['run']}
def save():record.write_text(json.dumps(r,indent=2)+'\n')
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
with FTP() as f:
 f.connect(r['host'],timeout=20);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
 f.cwd('/F');assert get(f,'xwn-report-v2.txt')==b'XWN-V2-PENDING-20261004\r\n'.ljust(4096,b' ') and get(f,'xwn-create-v2.bin',True) is None
 f.cwd('/F/winnt/system32');assert get(f,'xwn-video-trace.bin')==trace
 f.cwd('/F/winnt/system32/drivers');assert sha(get(f,'xboxvnt5.sys'))==r['miniport_sha256']
 f.cwd('/E/Applications/XWNFBoot')
 for name,key in [('default.xbe','launcher_sha256'),('freeldr.sys','loader_sha256')]:assert sha(get(f,name))==previous[key]
 f.cwd('loader');old=get(f,'halxboxnt5.dll');assert sha(old)==old_hash
 assert get(f,'halxboxnt5.xwn-v8',True) is None and get(f,'halxboxnt5.xwn-new9',True) is None
 r.update(status='uploading_candidate',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
 try:
  for at in range(0,len(new),32768):f.storbinary(('STOR ' if at==0 else 'APPE ')+'halxboxnt5.xwn-new9',io.BytesIO(new[at:at+32768]),blocksize=1024)
  assert get(f,'halxboxnt5.xwn-new9')==new
  f.rename('halxboxnt5.dll','halxboxnt5.xwn-v8');r['status']='original_backed_up';save()
  f.rename('halxboxnt5.xwn-new9','halxboxnt5.dll');assert get(f,'halxboxnt5.dll')==new
  r['status']='candidate_readback_verified';save()
  f.cwd('/F/winnt/system32');assert get(f,'xwn-video-trace.bin')==trace
  f.storbinary('STOR xwn-video-trace.bin',io.BytesIO(trace_seed),blocksize=1024);assert get(f,'xwn-video-trace.bin')==trace_seed
  r.update(launch_attempted=True,launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=previous['command'],status='awaiting_physical_result');save()
  try:r['reply']=f.sendcmd(r['command'])
  except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
  save();print(r)
 except Exception as e:
  r['error']=repr(e);save();raise
