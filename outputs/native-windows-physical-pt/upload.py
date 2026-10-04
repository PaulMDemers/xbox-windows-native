"""Stage and read back the isolated diagnostic; switch the loader last."""
from pathlib import Path
import ftplib,io,hashlib,json,datetime,os,time
kit=Path(__file__).resolve().parent
old=kit.parent/'native-windows-physical-size/package'
remote='/E/Applications/XWNLoader'
sha=lambda b:hashlib.sha256(b).hexdigest()
r={'host':'192.168.50.242','destination':remote,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'launched':False,'files':[]}
def save(): (kit/'ftp-upload.json').write_text(json.dumps(r,indent=2)+'\n')
def get(f,p):
 b=io.BytesIO();f.retrbinary('RETR '+p,b.write);return b.getvalue()
def maybe(f,p):
 try:return get(f,p)
 except ftplib.error_perm as e:
  if str(e).startswith('550'):return None
  raise
def ensure_dir(f,p):
 current=f.pwd()
 try:
  try:f.cwd(p)
  except ftplib.error_perm as e:
   missing=str(e).startswith('550') or (str(e).startswith('553') and 'Directory not found' in str(e))
   if not missing:raise
   f.mkd(p);f.cwd(p)
 finally:f.cwd(current)
assert json.loads((kit/'validation.json').read_text())['ready_for_physical_upload']
files=sorted(p for p in (kit/'package').rglob('*') if p.is_file())
unchanged=[p.relative_to(kit/'package').as_posix() for p in files if p.read_bytes()==(old/p.relative_to(kit/'package')).read_bytes()]
replaced=[n for n in ['loader/halxboxnt5.dll','freeldr.ini','README.txt','rosload.exe','freeldr.sys'] if n not in unchanged]
assert set(p.relative_to(kit/'package').as_posix() for p in files)==set(unchanged)|set(replaced)
backups={'loader/halxboxnt5.dll':'loader/hal-xwnq90.dll','rosload.exe':'rosload-xwnq90.exe','freeldr.ini':'freeldr-xwnq90.ini','README.txt':'README-xwnq90.txt','freeldr.sys':'freeldr-xwnq90.sys'}
try:
 with ftplib.FTP() as f:
  f.connect(r['host'],21,timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD']);f.cwd(remote)
  for name in unchanged:assert get(f,name)==(kit/'package'/name).read_bytes(),name
  originals={name:get(f,name) for name in replaced}
  for name,data in originals.items():
   assert data==(old/name).read_bytes(),'Unexpected installed file: '+name
   assert maybe(f,backups[name]) is None,'Backup exists: '+backups[name]
  save()
  directories=sorted({p.parent.relative_to(kit/'package').as_posix() for p in files if p.parent!=kit/'package'},key=lambda n:(n.count('/'),n))
  for directory in directories:
   parts=directory.split('/')
   for n in range(1,len(parts)+1):ensure_dir(f,'/'.join(parts[:n]))
  for p in files:
   name=p.relative_to(kit/'package').as_posix();data=p.read_bytes()
   if name in unchanged:continue
   if name not in replaced:
    previous=maybe(f,name)
    assert previous is None or previous==data,'Destination collision: '+name
   temporary=name+'.xwn-new';staged=maybe(f,temporary)
   offset=0
   if staged is not None:
    if staged==data:offset=len(data)
    else:
     # The only interrupted staging file belongs to our previous HAL transfer.
     assert name=='loader/halxboxnt5.dll' and len(staged)<len(data) and data.startswith(staged), 'Mismatched staging file: '+temporary
     offset=len(staged);r['resumed_hal_prefix_bytes']=offset;save()
   if offset<len(data):
    print('Uploading '+name+' ('+str(offset)+'/'+str(len(data))+' bytes staged)',flush=True)
    last=time.monotonic()
    for at in range(offset,len(data),32768):
     # Short data connections avoid the measured UnleashX large-upload slowdown.
     verb='STOR' if at==0 else 'APPE'
     f.storbinary(verb+' '+temporary,io.BytesIO(data[at:at+32768]),blocksize=1024)
     if time.monotonic()-last>=10:
      print(name+': staged '+str(min(at+32768,len(data)))+'/'+str(len(data)),flush=True);last=time.monotonic()
   else:print('Reusing verified staging file '+name,flush=True)
   assert get(f,temporary)==data,'Readback mismatch: '+name
   r['files'].append({'name':name,'bytes':len(data),'sha256':sha(data),'staging_readback_equal':True});save()
  for item in r['files']:
   name=item['name']
   if name not in replaced:
    if maybe(f,name) is None:f.rename(name+'.xwn-new',name)
    else:f.delete(name+'.xwn-new')
    item['final_name_verified']=True
  switched=[]
  try:
   for name in replaced:
    assert get(f,name)==originals[name]
    f.rename(name,backups[name])
    try:f.rename(name+'.xwn-new',name)
    except Exception:
     f.rename(backups[name],name);raise
    switched.append(name)
   for name in replaced:assert get(f,name)==(kit/'package'/name).read_bytes()
  except Exception:
   for name in reversed(switched):
    f.rename(name,name+'.xwn-new');f.rename(backups[name],name)
   raise
  for item in r['files']:item['final_name_verified']=True
  r.update(completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),backups={n:backups[n] for n in replaced},unchanged_files_verified=unchanged,launcher_unchanged=True,probe_unchanged=True)
  save();print('Upload complete; loader switched last; Xbox was not launched.',flush=True)
except Exception as e:
 r['error']=type(e).__name__+': '+str(e);save();raise
