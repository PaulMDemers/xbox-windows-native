"""One owned pass-through diagnostic; no original boot/startup/driver changes."""
import json,shutil,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn467/physical001')
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from physical import baseline,connect as connect_base,get,names,sha,utc,write_json,START,NORMAL,TARGET,protected,ticket,put
from decode import decode
from refusal_decode import decode_refusal
REMOTE='/E/Applications/XWNBoot466a';BUILD=Path('C:/xwn466/build001/default.xbe')
MUTABLE=['/E/winnt/system32/config/'+n for n in ['system','software','sam','security','default','sysevent.evt','appevent.evt']]+['/E/winnt/system32/xwn-video-trace.bin']
def connect(timeout=45):return connect_base(timeout=timeout)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def local(s):
 if s.startswith('/mnt/'):return Path(s[5].upper()+':/'+s[7:])
 return Path(s)
def verify():
 ticket();q=K.parent/'marker-handoff466'
 assert read(q/'final-review.json')['passed']
 assert read(q/'source-review002.json')['passed']
 t=read(q/'emu003/trace.json');assert t['passed'] and not t.get('cleanup_error')
 assert t['physical_mode_restored'] and not t['remaining_breakpoints']
 assert read(q/'emu003/audit.json')['host_exit']['passed']
 assert read(q/'emu003/actual-controls.json')['passed']
 for n in ['host001','stub-host001']:
  h=read(q/(n+'.json'));assert h['status']=='passed'
  for p,v in h['files'].items():assert sha(local(p).read_bytes())==v['sha256'],p
 b=read(q/'build001.json');assert b['status']=='compiled'
 for p,v in b['files'].items():assert sha(local(p).read_bytes())==v['sha256'],p
 data=BUILD.read_bytes();assert sha(data)==b['sha256']=='74a479078f378b8f02c54d4bd146765a7d860031116f636a3658a6616c2bedf5'
 return data

def startup(f):
 assert sha(get(f,TARGET))=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
 listing=names(f,START);assert {n.lower() for n in listing}<={'xwnsetup.cmd','desktop.ini'}
 assert sha(get(f,NORMAL))=='da47fdf32e29b81ba9f5148d86f291ed708c9432c268b1682668c5b50883aa43'
 return listing
def keep(folder,n,b):
 p=folder/n.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_bytes(b)
 return dict(path=str(p),bytes=len(b),sha256=sha(b))
def stage():
 b=verify();out=K/'stage001.json';assert not out.exists() and not P.exists()
 assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
 P.mkdir(parents=True)
 r=dict(completed=False,utc=utc(),physical_writes=[],before={},console_C_accessed=False,original_launcher_changed=False,startup_changed=False,mode='720p',remote=REMOTE)
 r['source_pins']={str(p):sha(p.read_bytes()) for p in [K/'physical.py',K/'decode.py',K/'refusal_decode.py',W/'outputs/field-scanout428/physical.py',W/'outputs/demo-audio-level256/common001.py',W/'outputs/surface-bridge260/atomic_json.py',W/'tools/configure-e-display.py',W/'tools/e-display-policy.json']}
 write_json(out,r)
 with connect() as f:
  baseline(f,'720p');r['startup_listing']=startup(f)
  assert REMOTE.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/E/Applications')}
  for n in [NORMAL,TARGET]+MUTABLE:
   data=get(f,n);assert data==get(f,n);r['before'][n]=keep(P/'before',n,data);write_json(out,r)
  r['physical_writes'].append(REMOTE);write_json(out,r);f.mkd(REMOTE)
  owner=json.dumps(dict(project='xbox-windows-native',case='467physical001',cookie='46600101',purpose='two bounded SMC markers then original handoff',sha256=sha(b)),sort_keys=True).encode()
  for name,data in [('owner.json',owner),('default.xbe',b)]:
   n=REMOTE+'/'+name;r['physical_writes'].append(n);write_json(out,r);put(f,n,data)
   assert get(f,n)==data;r.setdefault('staged',{})[n]=dict(bytes=len(data),sha256=sha(data));write_json(out,r)
  baseline(f,'720p');startup(f)
 r.update(completed=True,ended_utc=utc());write_json(out,r);print('New diagnostic staged/readback verified; original launcher/startup unchanged',flush=True)
def launch():
 verify();s=read(K/'stage001.json');assert s['completed'];out=K/'launch001.json';assert not out.exists()
 for p,h in s['source_pins'].items():assert sha(Path(p).read_bytes())==h,p
 with connect() as f:
  baseline(f,'720p');startup(f)
  for n,v in s['before'].items():assert sha(get(f,n))==v['sha256'],n
  for n,v in s['staged'].items():assert sha(get(f,n))==v['sha256'],n
  assert get(f,REMOTE+'/report.bin',True) is None
  assert get(f,REMOTE+'/refusal.bin',True) is None
  r=dict(utc=utc(),requested=True,command=r'SITE EXEC E:\Applications\XWNBoot466a\default.xbe',windows_boot_intended=True,automatic_restart_installed=False,console_C_accessed=False)
  write_json(out,r);f.sock.settimeout(20)
  try:r['reply']=f.sendcmd(r['command'])
  except Exception as e:r['reply_uncertain']=repr(e)
  write_json(out,r)
 print('One pass-through diagnostic launch recorded; never repeat accepted or uncertain request',flush=True)
def observe():
 assert read(K/'launch001.json')['requested'];out=K/'observation001.json';assert not out.exists()
 r=dict(started_utc=utc(),completed=False,observations=[]);write_json(out,r);deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  time.sleep(5)
  try:
   with connect(timeout=3) as f:b=get(f,REMOTE+'/report.bin',True)
   r['observations'].append(dict(utc=utc(),dashboard=True,report_bytes=None if b is None else len(b)))
   if b is not None:
    r['report']=keep(P/'observed',REMOTE+'/report.bin',b)
    try:r['decoded']=decode(b)
    except ValueError as e:r['decode_error']=str(e)
    r['ended_utc']=utc();r['completed']=True;write_json(out,r);print(json.dumps(r),flush=True);return
  except (OSError,EOFError) as e:r['observations'].append(dict(utc=utc(),dashboard=False,error=type(e).__name__))
  write_json(out,r)
 r.update(completed=True,ended_utc=utc(),deadline_reached=True);write_json(out,r);print('Observation deadline; screen confirmation needed',flush=True)
def collect():
 verify();s=read(K/'stage001.json');assert read(K/'launch001.json')['requested']
 out=K/'collection001.json';assert not out.exists()
 r=dict(completed=False,utc=utc(),files={},console_C_accessed=False,remote_writes=[],mode='720p');write_json(out,r)
 with connect() as f:
  baseline(f,'720p');r['startup_listing']=startup(f)
  for n in [NORMAL,TARGET]+MUTABLE+list(s['staged'])+[REMOTE+'/report.bin',REMOTE+'/refusal.bin']:
   b=get(f,n,True);assert b==get(f,n,True)
   if b is None:r['files'][n]=None;write_json(out,r);continue
   row=keep(P/'after',n,b)
   prior=s['before'].get(n) or s['staged'].get(n)
   if prior:row['unchanged']=row['sha256']==prior['sha256']
   r['files'][n]=row;write_json(out,r)
  b=r['files'].get(REMOTE+'/report.bin')
  if b:
   try:r['decoded']=decode(Path(b['path']).read_bytes())
   except ValueError as e:r['decode_error']=str(e)
  refusal=r['files'].get(REMOTE+'/refusal.bin')
  if refusal:
   try:r['refusal_decoded']=decode_refusal(Path(refusal['path']).read_bytes())
   except ValueError as e:r['refusal_decode_error']=str(e)
 r.update(completed=True,ended_utc=utc(),normal_windows_shutdown_proved=False,full_allocation_audit=False);write_json(out,r)
 print(json.dumps(dict(completed=True,files=len(r['files']),decoded=r.get('decoded'))),flush=True)
if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ('stage','launch','observe','collect');globals()[sys.argv[1]]()
