"""One new499 entry observation; no Windows workload or startup-hook writes."""
import ftplib,importlib.util,json,shutil,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn500/physical001')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
B=module('baseline500',W/'outputs/field-scanout428/physical.py')
D=module('entrydecode500',W/'outputs/entry-receipt498/decode.py')
connect=B.connect;get=B.get;put=B.put;names=B.names;baseline=B.baseline
sha=B.sha;utc=B.utc;write_json=B.write_json;ticket=B.ticket
START=B.START;NORMAL=B.NORMAL;TARGET=B.TARGET
REMOTE='/E/Applications/XWNBoot499a';BUILD=Path('C:/xwn499/build001/default.xbe')
RECEIPTS=('entry.bin','report.bin','refusal.bin','handoff.bin','context.bin')
MUTABLE=['/E/winnt/system32/config/'+n for n in ('system','software','sam','security','default','sysevent.evt','appevent.evt')]+['/E/winnt/system32/xwn-video-trace.bin']
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def verify():
 ticket();p=read(K/'package001.json');assert p['passed']
 for name,h in p['dependencies'].items():assert sha(Path(name).read_bytes())==h,name
 b=BUILD.read_bytes();assert sha(b)==p['candidate_sha256']=='22d3a9224965159a53cb188be9530f1b211aff8480d3d5773405d7e2974cf6d9'
 return b
def startup(f):
 assert sha(get(f,TARGET))=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
 assert sha(get(f,NORMAL))=='da47fdf32e29b81ba9f5148d86f291ed708c9432c268b1682668c5b50883aa43'
 rows=names(f,START);assert {n.lower() for n in rows}<={'desktop.ini','xwnsetup.cmd'}
 return rows
def keep(root,name,data):
 p=root/name.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True)
 assert not p.exists();p.write_bytes(data)
 return dict(path=str(p),bytes=len(data),sha256=sha(data))
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
 try:r=D.decode(data)
 except ValueError as e:return dict(entry_state='malformed',entry_execution=False,error=str(e),absence_proves_no_entry=False)
 return dict(entry_state='complete',entry_execution=True,decoded=r,
             final_close_proved=False,preparation_proved=False,windows_boot_proved=False)
def stage():
 out=K/'physical001-stage.json';assert not out.exists() and not P.exists()
 b=verify();assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
 P.mkdir(parents=True)
 r=dict(utc=utc(),completed=False,before={},staged={},writes=[],console_C_accessed=False,
        temporary_hook_installed=False,automatic_restart_installed=False,
        return_plan='Windows may remain running; operator normal restart required',remote=REMOTE)
 write_json(out,r)
 with connect(timeout=15) as f:
  baseline(f,'720p');r['startup_listing']=startup(f)
  assert REMOTE.rsplit('/',1)[1].lower() not in {x.lower() for x in names(f,'/E/Applications')}
  for n in [NORMAL,TARGET]+MUTABLE:
   b0=get(f,n);assert get(f,n)==b0;r['before'][n]=keep(P/'before',n,b0);write_json(out,r)
  r['writes'].append(REMOTE);write_json(out,r);f.mkd(REMOTE)
  owner=json.dumps(dict(project='xbox-windows-native',case='500physical001',binary_attempt=499,
                       candidate_sha256=sha(b),purpose='early-entry diagnostic; no Windows workload hook'),sort_keys=True).encode()
  for name,data in [('owner.json',owner),('default.xbe',b)]:
   n=REMOTE+'/'+name;r['writes'].append(n);write_json(out,r);put(f,n,data)
   assert get(f,n)==data;r['staged'][n]=dict(bytes=len(data),sha256=sha(data));write_json(out,r)
  assert set(listing(f))=={'owner.json','default.xbe'};baseline(f,'720p');startup(f)
 r.update(completed=True,ended_utc=utc());write_json(out,r)
def launch():
 out=K/'physical001-launch.json';assert not out.exists()
 verify();s=read(K/'physical001-stage.json');assert s['completed'] and not s['temporary_hook_installed']
 with connect(timeout=15) as f:
  baseline(f,'720p');startup(f)
  assert set(listing(f))=={'owner.json','default.xbe'},'preexisting receipt'
  for n,v in {**s['before'],**s['staged']}.items():assert sha(get(f,n))==v['sha256'],n
  r=dict(utc=utc(),requested=True,command=r'SITE EXEC E:\Applications\XWNBoot499a\default.xbe',
         automatic_restart_installed=False,return_plan=s['return_plan'],console_C_accessed=False)
  # Persist BEFORE send; uncertainty can never authorize a second request.
  write_json(out,r);f.sock.settimeout(20)
  try:r['reply']=f.sendcmd(r['command'])
  except Exception as e:r['reply_uncertain']=type(e).__name__
  write_json(out,r)
def observe():
 out=K/'physical001-observation.json';assert not out.exists()
 verify();assert read(K/'physical001-launch.json')['requested']
 r=dict(started_utc=utc(),completed=False,observations=[],windows_boot_proved=False);write_json(out,r)
 deadline=time.monotonic()+180
 while time.monotonic()<deadline:
  time.sleep(5)
  try:
   with connect(timeout=3) as f:
    rows=listing(f);data=receipt(f,'entry.bin',rows)
   row=dict(utc=utc(),dashboard=True,listing=rows,entry=classify(data))
   r['observations'].append(row)
   if data is not None:
    row['entry_file']=keep(P/'observed',REMOTE+'/entry.bin',data)
    r.update(completed=True,ended_utc=utc(),needs_cold_collection=True);write_json(out,r);return
  except (OSError,EOFError,ftplib.Error,ValueError,AssertionError) as e:
   r['observations'].append(dict(utc=utc(),dashboard_unknown=True,error_type=type(e).__name__))
  write_json(out,r)
 r.update(completed=True,ended_utc=utc(),deadline_reached=True,console_state='requires current observation; do not infer shutdown');write_json(out,r)
def pair(name,r,out,is_receipt=False):
 for attempt in range(2):
  try:
   with connect(timeout=15) as f:
    if is_receipt:
     a=receipt(f,name,listing(f));b=receipt(f,name,listing(f))
    else:a=get(f,name);b=get(f,name)
   assert a==b,'paired read changed'
   return a
  except (OSError,EOFError,ftplib.error_temp,ftplib.error_perm) as e:
   code=str(e)[:3]
   r.setdefault('read_failures',[]).append(dict(path=name,attempt=attempt+1,error_type=type(e).__name__,reply_code=code if code.isdecimal() else None));write_json(out,r)
   if attempt==1:raise
 raise AssertionError('read bound')
def collect():
 out=K/'physical001-collection.json';assert not out.exists()
 verify();assert read(K/'physical001-launch.json')['requested'];s=read(K/'physical001-stage.json')
 r=dict(utc=utc(),completed=False,files={},remote_writes=[],console_C_accessed=False,
        owned_hook_never_installed=True,normal_windows_shutdown_proved=False,full_allocation_audit=False);write_json(out,r)
 with connect(timeout=15) as f:
  baseline(f,'720p');r['startup_listing']=startup(f);r['listing']=listing(f);write_json(out,r)
 for n in [NORMAL,TARGET]+MUTABLE+list(s['staged']):
  data=pair(n,r,out);row=keep(P/'after',n,data)
  row['unchanged']=row['sha256']==(s['before'].get(n) or s['staged'][n])['sha256']
  r['files'][n]=row;write_json(out,r)
 for name in RECEIPTS:
  data=pair(name,r,out,True);n=REMOTE+'/'+name
  r['files'][n]=None if data is None else keep(P/'after',n,data)
  if name=='entry.bin':r['entry']=classify(data)
  write_json(out,r)
 r.update(completed=True,ended_utc=utc());write_json(out,r)
if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ('stage','launch','observe','collect')
 globals()[sys.argv[1]]()
