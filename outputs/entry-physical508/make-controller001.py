"""Derive new entry-only physical controller; old executed source stays immutable."""
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
s=(K.parent/'entry-scene501/physical.py').read_text(encoding='utf-8')
def part(a,b):return s[s.index(a):s.index(b)]
head=part('import ftplib', 'from primary_decode')
head=head.replace("import ftplib,json,shutil,struct,sys,time", "import ftplib,json,shutil,sys,time")
head=head.replace('C:/xwn501/physical001','C:/xwn508/physical001')
head+='from entry_decode import decode as decode_entry\n'
head+="REMOTE='/E/Applications/XWNBoot504a';BUILD=Path('C:/xwn504/build001/default.xbe')\n"
head+=part('MUTABLE=', 'KITROOT=')
startup=part('def startup(', 'def keep(')
startup=startup.replace('def startup(f,armed=False):','def startup(f):')
startup=startup.replace("({'xwnsetup.cmd','desktop.ini','xwn501.cmd'} if armed else {'xwnsetup.cmd','desktop.ini'})", "{'xwnsetup.cmd','desktop.ini'}")
startup=startup.replace(' if armed:assert get(f,HOOK)==hook()\n','')
common=part('def keep(', 'def stage():').replace("'context.bin')", "'context.bin','witness.bin')")
stage='''def stage():
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
  owner=json.dumps(dict(project='xbox-windows-native',case='508physical001',purpose='504 entry-only LED/file/return diagnostic; no Windows',sha256=sha(b)),sort_keys=True).encode()
  for name,data in [('owner.json',owner),('default.xbe',b)]:
   n=REMOTE+'/'+name;r['physical_writes'].append(n);write_json(out,r);put(f,n,data)
   assert get(f,n)==data;r.setdefault('staged',{})[n]=dict(bytes=len(data),sha256=sha(data));write_json(out,r)
  assert set(listing(f))=={'owner.json','default.xbe'}
  baseline(f,'720p');assert startup(f)==r['startup_listing']
 r.update(completed=True,ended_utc=utc());write_json(out,r);print('Entry-only staged; no hook or Windows runner',flush=True)

'''
launch=part('def launch():','def observe():')
launch=launch.replace('startup(f,True)','startup(f)')
launch=launch.replace("  assert 'xwn501' not in {n.lower() for n in names(f,'/E')}\n",'')
launch=launch.replace('XWNBoot499a','XWNBoot504a').replace('windows_boot_intended=True,automatic_restart_installed=True','windows_boot_intended=False,automatic_restart_installed=False')
observe='''def observe():
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

'''
cold=part('def cold_pair(', 'def collect():')
collect='''def collect():
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
'''
dest=K/'physical.py';assert not dest.exists();dest.write_bytes(('"""One entry-only test. No Windows startup hook; no ordinary launcher changes."""\n'+head+startup+common+stage+launch+observe+cold+collect).encode())
(K/'entry_decode.py').write_bytes((K.parent/'entry-scene501/entry_decode.py').read_bytes())
t=(K.parent/'entry-scene501/supervise.py').read_text(encoding='utf-8').replace('atomic501','atomic508').replace('C:/xwn501/supervisor002','C:/xwn508/supervisor001').replace('observe=540','observe=150')
(K/'supervise.py').write_bytes(t.encode())
(K/'.gitattributes').write_bytes(b'* -text whitespace=cr-at-eol\n')
