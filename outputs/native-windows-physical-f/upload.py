"""Resumable file-only install in newly reserved roots, with byte readback."""
import pathlib,ftplib,io,json,hashlib,os,datetime,time,socket
class FTP(ftplib.FTP):
 def ntransfercmd(self,*args,**kwargs):
  s,n=super().ntransfercmd(*args,**kwargs)
  s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
  return s,n
k=pathlib.Path(__file__).resolve().parent;manifest=json.loads((k/'package-manifest.json').read_text());state=k/'upload.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
identity={'package_sha256':sha((k/'package-manifest.json').read_bytes()),'purpose':'XWN physical F native test v1'};marker=json.dumps(identity,sort_keys=True).encode()
r=json.loads(state.read_text()) if state.exists() else {'started_utc':now(),'host':'192.168.50.242','files':{},'launched':False,'package_sha256':identity['package_sha256']}
assert r['package_sha256']==identity['package_sha256']
def save():
 tmp=state.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(state)
def get(f,name,optional=False):
 b=io.BytesIO()
 try:f.retrbinary('RETR '+name,b.write)
 except ftplib.error_perm as e:
  if optional and str(e).startswith('550'):return None
  raise
 return b.getvalue()
def names(f,path):
 f.cwd(path);rows=[];f.retrlines('LIST',rows.append);return {s.split(maxsplit=8)[-1].lower() for s in rows}
def mkdirs(f,path):
 f.cwd('/')
 for part in path.strip('/').split('/'):
  try:f.cwd(part)
  except ftplib.error_perm as e:
   if not (str(e).startswith('550') or 'Directory not found' in str(e)):raise
   f.mkd(part);f.cwd(part)
save()
try:
 with FTP() as f:
  f.connect(r['host'],21,timeout=30);f.login('xbox',os.environ['XWN_FTP_PASSWORD']);f.cwd('/F')
  existing=get(f,'xwn-deploy-v1.json',True)
  if existing is None:
   assert not r.get('reserved'), 'Deployment marker disappeared'
   roots=names(f,'/F');assert not roots&{'winnt','documents and settings','program files','xwnphysical.exe','xwn-physical.bin','xwn-physical.log','xwn-physical-write.bin'}
   assert 'xwnfboot' not in names(f,'/E/Applications')
   f.cwd('/F');f.storbinary('STOR xwn-deploy-v1.json',io.BytesIO(marker));assert get(f,'xwn-deploy-v1.json')==marker
  else:assert existing==marker,'Destination owned by another package'
  r['reserved']=True;save()
  dirs=set(manifest['directories'])|{str(pathlib.PurePosixPath(v['path']).parent) for v in manifest['files']}
  for directory in sorted(dirs,key=lambda p:(p.count('/'),p)):mkdirs(f,'/'+directory)
  current=None;last=time.monotonic()
  for index,item in enumerate(manifest['files']):
   rel=item['path'];data=(k/'package'/rel).read_bytes();assert sha(data)==item['sha256']
   parent,name=rel.rsplit('/',1)
   if name=='default.xbe':name='launch-held.xbe'
   # UnleashX rejects this existing informational COM+ text log's plus sign.
   # Preserve its bytes under an accepted archival name; no executable changes.
   if rel=='F/winnt/com+.log':name='com-plus.log'
   if parent!=current:f.cwd('/'+parent);current=parent
   old=get(f,name,True)
   if old is not None:
    assert len(old)<=len(data) and data.startswith(old),'Unexpected destination bytes: '+rel
    at=len(old)
   else:at=0
   if not data and old is None:f.storbinary('STOR '+name,io.BytesIO(data))
   while at<len(data):
    block=data[at:at+32768];f.storbinary(('STOR ' if at==0 else 'APPE ')+name,io.BytesIO(block),blocksize=1024);at+=len(block)
    if time.monotonic()-last>20:
     r['current_transfer']={'path':rel,'sent_bytes':at,'total_bytes':len(data)};save();print('Staging',rel,at,'/',len(data),flush=True);last=time.monotonic()
   if old!=data:assert get(f,name)==data,'Readback mismatch: '+rel
   r['files'][rel]={'sha256':item['sha256'],'bytes':len(data),'readback_verified':True,'remote_name':name}
   if index%25==0 or time.monotonic()-last>20:
    save();print('Verified',index+1,'/',len(manifest['files']),rel,flush=True);last=time.monotonic()
  r.update(completed_utc=now(),all_files_verified=True,launcher_held=True);r.pop('error',None);save()
except Exception as e:r['error']=repr(e);save();raise
