"""One owned pass-through diagnostic; no original boot/startup/driver changes."""
import ftplib,json,shutil,struct,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn494/physical001')
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from physical import baseline,connect as connect_base,get,names,sha,utc,write_json,START,NORMAL,TARGET,protected,ticket,put
from primary_decode import decode
from witness_decode import decode_witness
from receipts import decode_refusal
from decode import decode as decode_context
REMOTE='/E/Applications/XWNBoot494a';BUILD=Path('C:/xwn494/build002/default.xbe')
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

KITROOT='/E/xwn494-kit';RESULT='/E/xwn494';HOOK=START+'/xwn494.cmd'
def hook():
 return b'@echo off\r\nif exist C:\\xwn494 goto done\r\nC:\\xwn494-kit\\run494.exe\r\n:done\r\nexit\r\n'


def startup(f,armed=False):
 assert sha(get(f,TARGET))=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
 listing=names(f,START);assert {n.lower() for n in listing}<=({'xwnsetup.cmd','desktop.ini','xwn494.cmd'} if armed else {'xwnsetup.cmd','desktop.ini'})
 assert sha(get(f,NORMAL))=='da47fdf32e29b81ba9f5148d86f291ed708c9432c268b1682668c5b50883aa43'
 if armed:assert get(f,HOOK)==hook()
 return listing
def keep(folder,n,b):
 p=folder/n.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_bytes(b)
 return dict(path=str(p),bytes=len(b),sha256=sha(b))
def stage():
 b=verify();out=K/'physical001-stage.json';assert not out.exists() and not P.exists()
 assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
 P.mkdir(parents=True)
 r=dict(completed=False,utc=utc(),physical_writes=[],before={},console_C_accessed=False,original_launcher_changed=False,normal_startup_changed=False,temporary_startup_added=False,mode='720p',remote=REMOTE)
 r['source_pins']={str(p):sha(p.read_bytes()) for p in [K/'physical.py',K/'decode.py',K/'witness_decode.py',K/'legacy_refusal_decode.py',K/'failure_marker.py',K/'package001.json',W/'outputs/field-scanout428/physical.py',W/'outputs/demo-audio-level256/common001.py',W/'outputs/surface-bridge260/atomic_json.py',W/'tools/configure-e-display.py',W/'tools/e-display-policy.json']}
 write_json(out,r)
 with connect() as f:
  baseline(f,'720p');r['startup_listing']=startup(f)
  assert REMOTE.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/E/Applications')}
  assert not {'xwn494','xwn494-kit'} & {n.lower() for n in names(f,'/E')}
  package=read(K/'package001.json')
  for name,h in package['runtime_module_pins'].items():assert sha(get(f,'/E/winnt/system32/'+name))==h,name
  for n in [NORMAL,TARGET]+MUTABLE:
   data=get(f,n);assert data==get(f,n);r['before'][n]=keep(P/'before',n,data);write_json(out,r)
  r['physical_writes'].append(REMOTE);write_json(out,r);f.mkd(REMOTE)
  owner=json.dumps(dict(project='xbox-windows-native',case='494physical001',diagnostic_schema=490,cookie='49000101',purpose='493 matched XYZ transform sample; inherited490 read-only CPU capture; diagnostic intervention',sha256=sha(b)),sort_keys=True).encode()
  for name,data in [('owner.json',owner),('default.xbe',b)]:
   n=REMOTE+'/'+name;r['physical_writes'].append(n);write_json(out,r);put(f,n,data)
   assert get(f,n)==data;r.setdefault('staged',{})[n]=dict(bytes=len(data),sha256=sha(data));write_json(out,r)
  r['physical_writes'].append(KITROOT);write_json(out,r);f.mkd(KITROOT)
  for name,row in package['files'].items():
   if name=='default.xbe':continue
   data=Path(row['path']).read_bytes();n=KITROOT+'/'+name
   r['physical_writes'].append(n);write_json(out,r);put(f,n,data)
   assert get(f,n)==data;r['staged'][n]=dict(bytes=len(data),sha256=sha(data));write_json(out,r)
  assert get(f,HOOK,True) is None
  r['physical_writes'].append(HOOK);write_json(out,r);put(f,HOOK,hook());assert get(f,HOOK)==hook()
  r['temporary_startup_added']=True;r['hook_sha256']=sha(hook());baseline(f,'720p');startup(f,True)
 r.update(completed=True,ended_utc=utc());write_json(out,r);print('New diagnostic staged/readback verified; original launcher/startup unchanged',flush=True)
def launch():
 verify();s=read(K/'physical001-stage.json');assert s['completed'];out=K/'physical001-launch.json';assert not out.exists()
 for p,h in s['source_pins'].items():assert sha(Path(p).read_bytes())==h,p
 with connect() as f:
  baseline(f,'720p');startup(f,True)
  assert 'xwn494' not in {n.lower() for n in names(f,'/E')}
  for n,v in s['before'].items():assert sha(get(f,n))==v['sha256'],n
  for n,v in s['staged'].items():assert sha(get(f,n))==v['sha256'],n
  assert get(f,REMOTE+'/report.bin',True) is None
  assert get(f,REMOTE+'/refusal.bin',True) is None
  assert get(f,REMOTE+'/handoff.bin',True) is None
  assert get(f,REMOTE+'/context.bin',True) is None
  r=dict(utc=utc(),requested=True,command=r'SITE EXEC E:\Applications\XWNBoot494a\default.xbe',windows_boot_intended=True,automatic_restart_installed=True,console_C_accessed=False)
  write_json(out,r);f.sock.settimeout(20)
  try:r['reply']=f.sendcmd(r['command'])
  except Exception as e:r['reply_uncertain']=repr(e)
  write_json(out,r)
 print('One pass-through diagnostic launch recorded; never repeat accepted or uncertain request',flush=True)
def observe():
 assert read(K/'physical001-launch.json')['requested'];out=K/'physical001-observation.json';assert not out.exists()
 r=dict(started_utc=utc(),completed=False,observations=[]);write_json(out,r);deadline=time.monotonic()+486
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
def cold_pair(path,record,out):
 # Read-only retry on a NEW connection, at most two attempts. Never a SITE retry.
 for attempt in range(2):
  try:
   with connect(timeout=15) as reader:
    first=get(reader,path,True);second=get(reader,path,True)
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
 r=dict(completed=False,utc=utc(),files={},console_C_accessed=False,remote_writes=[],mode='720p');write_json(out,r)
 with connect() as f:
  assert get(f,HOOK)==hook()
  used=KITROOT+'/startup-used.cmd';assert get(f,used,True) is None
  r['remote_writes'].append(dict(action='rename-owned-hook',source=HOOK,destination=used));write_json(out,r)
  f.rename(HOOK,used);assert get(f,HOOK,True) is None and get(f,used)==hook();r['hook_removed']=True;write_json(out,r)
  baseline(f,'720p');r['startup_listing']=startup(f);r['protected_code_exact']=True
  extra=[used]
  if 'xwn494' in {n.lower() for n in names(f,'/E')}:
   listing=names(f,RESULT);r['result_directory']=listing;assert len(listing)<=22
   for name,item in listing.items():
    assert not item['directory'] and '/' not in name and chr(92) not in name
    extra.append(RESULT+'/'+name)
  for n in extra+[NORMAL,TARGET]+MUTABLE+list(s['staged'])+[REMOTE+'/report.bin',REMOTE+'/refusal.bin',REMOTE+'/handoff.bin',REMOTE+'/context.bin']:
   b=cold_pair(n,r,out)
   if b is None:r['files'][n]=None;write_json(out,r);continue
   row=keep(P/'after',n,b)
   prior=s['before'].get(n) or s['staged'].get(n)
   if prior:row['unchanged']=row['sha256']==prior['sha256']
   r['files'][n]=row;write_json(out,r)
  b=r['files'].get(REMOTE+'/report.bin')
  if b:
   try:r['decoded']=decode(Path(b['path']).read_bytes())
   except ValueError as e:r['decode_error']=str(e)
  witness=r['files'].get(REMOTE+'/handoff.bin')
  if witness and b:
   try:r['witness_decoded']=decode_witness(Path(witness['path']).read_bytes(),Path(b['path']).read_bytes())
   except ValueError as e:r['witness_decode_error']=str(e)
  context=r['files'].get(REMOTE+'/context.bin')
  if context and witness and b:
   try:
    primary=Path(r['files'][REMOTE+'/report.bin']['path']).read_bytes()
    witness_bytes=Path(witness['path']).read_bytes();decode_witness(witness_bytes,primary)
    syms=read(K/'build002.json')['wrapper_symbols'];frame=struct.unpack_from('<9I',witness_bytes,160)
    r['context_decoded']=decode_context(Path(context['path']).read_bytes(),witness_address=syms['witness_record'],frame_address=frame[3]-32,return_eips=[syms['context490_pre_return'],syms['context490_post_return']])
   except (ValueError,struct.error) as e:r['context_decode_error']=str(e)
  refusal=r['files'].get(REMOTE+'/refusal.bin')
  if refusal:
   try:r['refusal_decoded']=decode_refusal(Path(refusal['path']).read_bytes())
   except ValueError as e:r['refusal_decode_error']=str(e)
 r.update(completed=True,ended_utc=utc(),normal_windows_shutdown_proved=False,full_allocation_audit=False);write_json(out,r)
 print(json.dumps(dict(completed=True,files=len(r['files']),decoded=r.get('decoded'))),flush=True)
if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ('stage','launch','observe','collect');globals()[sys.argv[1]]()
