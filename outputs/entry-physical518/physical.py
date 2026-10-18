"""One entry-only test. No Windows startup hook; no ordinary launcher changes."""
import ftplib,json,shutil,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn518/physical001')
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from physical import baseline,connect as connect_base,get,names,sha,utc,write_json,START,NORMAL,TARGET,protected,ticket,put
from entry_decode import decode as decode_entry
REMOTE='/E/Applications/XWNBoot516a';BUILD=Path('C:/xwn516/build001/default.xbe')
MUTABLE=['/E/winnt/system32/config/'+n for n in ['system','software','sam','security','default','sysevent.evt','appevent.evt']]+['/E/winnt/system32/xwn-video-trace.bin']
def connect(timeout=45):return connect_base(timeout=timeout)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def local(s):
 if s.startswith('/mnt/'):return Path(s[5].upper()+':/'+s[7:])
 return Path(s)
def verify():
 ticket();q=K/'package001.json';v=read(q);assert v['passed']
 for p,h in v['dependencies'].items():assert sha(Path(p).read_bytes())==h,p
 for row in v['files'].values():assert sha(Path(row['path']).read_bytes())==row['sha256']
 return BUILD.read_bytes()

def startup(f):
 assert sha(get(f,TARGET))=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
 listing=names(f,START);assert {n.lower() for n in listing}<={'xwnsetup.cmd','desktop.ini'}
 assert sha(get(f,NORMAL))=='da47fdf32e29b81ba9f5148d86f291ed708c9432c268b1682668c5b50883aa43'
 return listing
def keep(folder,n,b):
 p=folder/n.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_bytes(b)
 return dict(path=str(p),bytes=len(b),sha256=sha(b))
RECEIPTS=('entry.bin','report.bin','refusal.bin','handoff.bin','context.bin','witness.bin')
def listing(f):
 rows=names(f,REMOTE)
 assert set(rows)<={'owner.json','default.xbe',*RECEIPTS},'unexpected owned-directory contents'
 assert all(not v['directory'] for v in rows.values())
 return rows
def receipt(f,name,rows):
 assert name in RECEIPTS
 if name not in rows:return None
 assert 0<=rows[name]['bytes']<=4096,'oversized receipt listing'
 chunks=[];total=0
 def receive(b):
  nonlocal total
  total+=len(b)
  if total>4096:raise ValueError('oversized receipt transfer')
  chunks.append(b)
 # A listed-but-unreadable file is a read FAILURE, never absence.
 f.retrbinary('RETR '+REMOTE+'/'+name,receive,1024)
 data=b''.join(chunks);assert len(data)==rows[name]['bytes'],'receipt changed since listing'
 return data
def classify(data):
 if data is None:return dict(entry_state='absent_in_listing',entry_execution=False,absence_proves_no_entry=False)
 try:r=decode_entry(data)
 except ValueError as e:return dict(entry_state='malformed',entry_execution=False,error=str(e),absence_proves_no_entry=False)
 return dict(entry_state='complete',entry_execution=True,decoded=r,
             final_close_proved=False,preparation_proved=False,windows_boot_proved=False)
def stage():
 b=verify();out=K/'physical001-stage.json';assert not out.exists() and not P.exists()
 assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
 P.mkdir(parents=True)
 r=dict(completed=False,utc=utc(),physical_writes=[],before={},console_C_accessed=False,
        original_launcher_changed=False,normal_startup_changed=False,temporary_startup_added=False,
        windows_boot_intended=False,mode='720p',remote=REMOTE)
 r['source_pins']={str(p):sha(p.read_bytes()) for p in [K/'physical.py',K/'entry_decode.py',K/'package001.json']}
 write_json(out,r)
 with connect() as f:
  baseline(f,'720p');r['startup_listing']=startup(f)
  assert REMOTE.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/E/Applications')}
  for n in [NORMAL,TARGET]+MUTABLE:
   data=get(f,n);assert data==get(f,n);r['before'][n]=keep(P/'before',n,data);write_json(out,r)
  r['physical_writes'].append(REMOTE);write_json(out,r);f.mkd(REMOTE)
  owner=json.dumps(dict(project='xbox-windows-native',case='518physical001',purpose='516 co-located-data LED/file/return diagnostic; no Windows',sha256=sha(b)),sort_keys=True).encode()
  for name,data in [('owner.json',owner),('default.xbe',b)]:
   n=REMOTE+'/'+name;r['physical_writes'].append(n);write_json(out,r);put(f,n,data)
   assert get(f,n)==data;r.setdefault('staged',{})[n]=dict(bytes=len(data),sha256=sha(data));write_json(out,r)
  assert set(listing(f))=={'owner.json','default.xbe'}
  baseline(f,'720p');assert startup(f)==r['startup_listing']
 r.update(completed=True,ended_utc=utc());write_json(out,r);print('Entry-only staged; no hook or Windows runner',flush=True)

def launch():
 verify();s=read(K/'physical001-stage.json');assert s['completed'];out=K/'physical001-launch.json';assert not out.exists()
 for p,h in s['source_pins'].items():assert sha(Path(p).read_bytes())==h,p
 with connect() as f:
  baseline(f,'720p');startup(f)
  for n,v in s['before'].items():assert sha(get(f,n))==v['sha256'],n
  for n,v in s['staged'].items():assert sha(get(f,n))==v['sha256'],n
  assert set(listing(f))=={'owner.json','default.xbe'}
  assert get(f,REMOTE+'/report.bin',True) is None
  assert get(f,REMOTE+'/refusal.bin',True) is None
  assert get(f,REMOTE+'/handoff.bin',True) is None
  assert get(f,REMOTE+'/context.bin',True) is None
  r=dict(utc=utc(),requested=True,command=r'SITE EXEC E:\Applications\XWNBoot516a\default.xbe',windows_boot_intended=False,automatic_restart_installed=False,console_C_accessed=False)
  write_json(out,r);f.sock.settimeout(20)
  try:r['reply']=f.sendcmd(r['command'])
  except Exception as e:r['reply_uncertain']=repr(e)
  write_json(out,r)
 print('One pass-through diagnostic launch recorded; never repeat accepted or uncertain request',flush=True)
def observe():
 assert read(K/'physical001-launch.json')['requested'];out=K/'physical001-observation.json';assert not out.exists()
 r=dict(started_utc=utc(),completed=False,observations=[]);write_json(out,r);deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  time.sleep(5)
  try:
   with connect(timeout=3) as f:
    rows=listing(f);early=receipt(f,'entry.bin',rows)
   r['observations'].append(dict(utc=utc(),dashboard=True,entry=classify(early)))
   if early is not None:
    r['entry_file']=keep(P/'observed',REMOTE+'/entry.bin',early);r['entry']=classify(early)
    r.update(ended_utc=utc(),completed=True);write_json(out,r);print('Entry receipt captured',flush=True);return
  except (OSError,EOFError) as e:r['observations'].append(dict(utc=utc(),dashboard=False,error_type=type(e).__name__))
  except (AssertionError,ValueError,ftplib.Error) as e:
   r.update(completed=False,ended_utc=utc(),receipt_transport_failed=True,error_type=type(e).__name__)
   write_json(out,r);raise
  write_json(out,r)
 r.update(completed=True,ended_utc=utc(),deadline_reached=True);write_json(out,r);print('Observation deadline; entry unknown without receipt',flush=True)

def cold_pair(path,record,out):
 # Read-only retry on a NEW connection, at most two attempts. Never a SITE retry.
 for attempt in range(2):
  try:
   with connect(timeout=15) as reader:
    if path.startswith(REMOTE+'/') and path.rsplit('/',1)[1] in RECEIPTS:
     name=path.rsplit('/',1)[1];first=receipt(reader,name,listing(reader));second=receipt(reader,name,listing(reader))
    else:first=get(reader,path,True);second=get(reader,path,True)
   if first!=second:raise ValueError('cold read changed: '+path)
   return first
  except (OSError,EOFError,ftplib.error_temp,ftplib.error_perm) as e:
   code=str(e)[:3]
   if isinstance(e,ftplib.error_perm) and code not in ('500','502'):raise
   record.setdefault('read_failures',[]).append(dict(path=path,attempt=attempt+1,error_type=type(e).__name__,reply_code=code if code.isdecimal() else None))
   write_json(out,record)
   if attempt==1:raise
 raise AssertionError('bounded read exhausted')

def collect():
 verify();s=read(K/'physical001-stage.json');assert read(K/'physical001-launch.json')['requested']
 out=K/'physical001-collection.json';assert not out.exists()
 r=dict(completed=False,utc=utc(),files={},console_C_accessed=False,remote_writes=[],mode='720p',temporary_hook_installed=False);write_json(out,r)
 with connect() as f:
  baseline(f,'720p');r['startup_listing']=startup(f);assert r['startup_listing']==s['startup_listing'];r['protected_code_exact']=True
 for n in [NORMAL,TARGET]+MUTABLE+list(s['staged'])+[REMOTE+'/'+name for name in RECEIPTS]:
  b=cold_pair(n,r,out)
  if b is None:r['files'][n]=None;write_json(out,r);continue
  row=keep(P/'after',n,b);prior=s['before'].get(n) or s['staged'].get(n)
  if prior:row['unchanged']=row['sha256']==prior['sha256']
  r['files'][n]=row;write_json(out,r)
 entry=r['files'].get(REMOTE+'/entry.bin');r['entry']=classify(None if entry is None else Path(entry['path']).read_bytes())
 r.update(completed=True,ended_utc=utc(),normal_windows_shutdown_proved=False,full_allocation_audit=False);write_json(out,r)
 print(json.dumps(dict(completed=True,entry=r['entry'],files=len(r['files']))),flush=True)
if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ('stage','launch','observe','collect');globals()[sys.argv[1]]()
