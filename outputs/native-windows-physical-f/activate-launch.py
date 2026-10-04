"""Enable the fully verified new launcher, then send exactly one launch."""
import pathlib,json,hashlib,ftplib,io,os,datetime,socket
k=pathlib.Path(__file__).resolve().parent;record=k/'physical-cycle-001.json'
assert not record.exists(),'Never repeat an uncertain launch'
upload=json.loads((k/'upload.json').read_text());manifest=json.loads((k/'package-manifest.json').read_text());emulator=json.loads((k/'emulator-cycle.json').read_text())
assert upload['all_files_verified'] and len(upload['files'])==len(manifest['files']) and emulator['passed']
sha=lambda b:hashlib.sha256(b).hexdigest()
def get(f,name,optional=False):
 b=io.BytesIO()
 try:f.retrbinary('RETR '+name,b.write)
 except ftplib.error_perm as e:
  if optional and str(e).startswith('550'):return None
  raise
 return b.getvalue()
r={'host':'192.168.50.242','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'launch_attempted':False,'command':'SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe'}
class FTP(ftplib.FTP):
 def ntransfercmd(self,*args,**kwargs):
  s,n=super().ntransfercmd(*args,**kwargs);s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return s,n
with FTP() as f:
 f.connect(r['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD']);f.cwd('/F')
 assert get(f,'xwn-physical.log',True) is None and get(f,'xwn-physical-write.bin',True) is None
 assert get(f,'xwn-physical.bin')==(k/'package/F/xwn-physical.bin').read_bytes()
 f.cwd('/E/Applications/XWNFBoot');new=(k/'artifacts/freeldr.sys').read_bytes();old=(k/'package/E/Applications/XWNFBoot/freeldr.sys').read_bytes()
 fixture=json.loads((k/'emulator-fixture-003.json').read_text())
 expected=next(v['sha256'] for v in fixture['files'] if v['path']=='E/Applications/XWNFBoot/freeldr.sys');assert sha(new)==expected
 current=get(f,'freeldr.sys',True);assert current in (None,old,new)
 if current!=new:
  backup=get(f,'freeldr-dvd.sys',True);assert backup in (None,old)
  assert current==old or backup==old,'No validated original loader remains'
  pending=get(f,'freeldr-f.sys',True)
  assert pending is None or (len(pending)<=len(new) and new.startswith(pending))
  for at in range(0,len(new),32768):f.storbinary(('STOR ' if at==0 else 'APPE ')+'freeldr-f.sys',io.BytesIO(new[at:at+32768]),blocksize=1024)
  assert get(f,'freeldr-f.sys')==new
  if current==old:
   assert backup is None,'Unexpected duplicate original loader'
   f.rename('freeldr.sys','freeldr-dvd.sys')
  f.rename('freeldr-f.sys','freeldr.sys')
 assert get(f,'freeldr.sys')==new
 xbe=(k/'artifacts/default.xbe').read_bytes();active=get(f,'default.xbe',True)
 if active is None:
  assert get(f,'launch-held.xbe')==xbe;f.rename('launch-held.xbe','default.xbe')
 else:assert active==xbe
 assert get(f,'default.xbe')==xbe
 r.update(launcher_sha256=sha(xbe),loader_sha256=sha(new),fresh_report_required=True,launch_attempted=True,launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 record.write_text(json.dumps(r,indent=2)+'\n')
 try:r['reply']=f.sendcmd(r['command'])
 except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
 record.write_text(json.dumps(r,indent=2)+'\n');print(r)
