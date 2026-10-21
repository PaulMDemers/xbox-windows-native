"""One owned physical480p Windows trial; normal720p stays protected."""
import ast,importlib.util,json,os,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn642/physical001')
sys.path.insert(0,str(K.parent/'visible-dispatch528'))
spec=importlib.util.spec_from_file_location('scope642',K.parent/'visible-dispatch528/physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
REMOTE='/E/Applications/XWN480p642';PROBE='/E/xwn480p642';HOOK=m.START+'/xwn480p642.cmd'
COMMAND=r'SITE EXEC E:\Applications\XWN480p642\default.xbe'
HOOK_BYTES=b'@echo off\r\nC:\\xwn480p642\\probe.exe\r\nexit\r\n'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def session():
 source=ast.parse(Path('C:/xwn626/session.py').read_text())
 nodes=[n for n in source.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='os.environ.update']
 assert len(nodes)==1
 exec(compile(ast.Module(body=nodes,type_ignores=[]),'<private session environment>','exec'))
def verify():
 m.ticket();assert shutil.disk_usage('C:/').free-128*1024**2>=20*1024**3
 r=read(K.parent/'windows480p639/audit001.json');assert r['scoped_passed'] and r['cold_collection_complete'] and r['input_file_matches']
 assert read(K.parent/'windows480p639/closure001.json')['closed']
 assert read(K/'binary-review001.json')['passed']
 b=Path('C:/xwn633/build001/default.xbe').read_bytes();x=Path('C:/xwn642/build001/probe.exe').read_bytes()
 assert m.sha(b)=='a53a09427f80411efee73ef53da0ec9829f8af0d27d404f5a3ff818e96b4bde4'
 assert m.sha(x)==read(K.parent/'windows480p642/build001.json')['binary_sha256']
 tests=read(K/'host001.json');assert tests['passed'] and tests['controller_sha256']==m.sha(Path(__file__).read_bytes())
 return b,x
def protected():
 return ['/E/'+v['path'] for v in read(K.parent/'windows480p636/installed-inputs001.json')['files']]+[m.NORMAL,m.TARGET,'/E/winnt/system32/bootvid.dll','/E/winnt/system32/notepad.exe']
def startup(f,hook=False):
 names=m.names(f,m.START);allowed={'xwnsetup.cmd','desktop.ini'}|({'xwn480p642.cmd'} if hook else set())
 assert {v.lower() for v in names}<=allowed
 assert m.sha(m.get(f,m.NORMAL))=='da47fdf32e29b81ba9f5148d86f291ed708c9432c268b1682668c5b50883aa43'
 if hook:assert m.get(f,HOOK)==HOOK_BYTES
 return names
def stage():
 b,x=verify();out=K/'stage001.json';assert not out.exists() and not P.exists();P.mkdir(parents=True)
 r=dict(completed=False,utc=m.utc(),before={},staged={},writes=[],console_C_accessed=False,ordinary720p_unchanged=True)
 m.write_json(out,r)
 try:
  with m.connect(timeout=15) as f:
   m.baseline(f,'720p');r['startup']=startup(f)
   assert REMOTE.rsplit('/',1)[1].lower() not in {v.lower() for v in m.names(f,'/E/Applications')}
   assert 'xwn480p642' not in {v.lower() for v in m.names(f,'/E')}
   for n in protected()+m.MUTABLE:
    data=m.get(f,n);assert data==m.get(f,n);r['before'][n]=m.keep(P/'before',n,data);m.write_json(out,r)
   expected=read(K.parent/'windows480p636/installed-inputs001.json')['files']
   assert all(r['before']['/E/'+v['path']]['sha256']==v['sha256'] for v in expected)
   assert r['before']['/E/winnt/system32/notepad.exe']['sha256']==read(K.parent/'windows480p639/preparation001.json')['protected']['winnt/system32/notepad.exe']
   for directory in [REMOTE,PROBE]:r['writes'].append(directory);m.write_json(out,r);f.mkd(directory)
   owner=json.dumps(dict(attempt='642physical001',probe_case=642,mode='720x480p32',ordinary720p_preserved=True),sort_keys=True).encode()
   for n,data in [(REMOTE+'/owner.json',owner),(REMOTE+'/default.xbe',b),(PROBE+'/owner.json',owner),(PROBE+'/probe.exe',x),(HOOK,HOOK_BYTES)]:
    r['writes'].append(n);m.write_json(out,r);m.put(f,n,data);assert m.get(f,n)==data;r['staged'][n]=dict(bytes=len(data),sha256=m.sha(data));m.write_json(out,r)
   m.baseline(f,'720p');startup(f,True)
  r.update(completed=True,ended_utc=m.utc())
 except BaseException as e:r['failure_type']=type(e).__name__;raise
 finally:m.write_json(out,r)
def request_once(f,out):
 r=dict(requested=True,utc=m.utc(),command=COMMAND,automatic_retry=False,windows_launch=True)
 with out.open('x',encoding='utf-8') as stream:json.dump(r,stream,indent=2)
 f.sock.settimeout(20)
 try:r['reply']=f.sendcmd(COMMAND)
 except Exception as e:r['reply_uncertain']=type(e).__name__
 m.write_json(out,r)
def launch():
 verify();s=read(K/'stage001.json');assert s['completed']
 with m.connect(timeout=15) as f:
  m.baseline(f,'720p');startup(f,True)
  for n,v in {**s['before'],**s['staged']}.items():assert m.sha(m.get(f,n))==v['sha256'],n
  assert m.get(f,PROBE+'/result.txt',True) is None
  assert m.get(f,PROBE+'/input.txt',True) is None
  request_once(f,K/'launch001.json')
def collect():
 assert read(K/'launch001.json')['requested'];out=K/'collection001.json';assert not out.exists()
 s=read(K/'stage001.json');r=dict(completed=False,utc=m.utc(),after={},console_C_accessed=False,hook_removed=False)
 m.write_json(out,r)
 try:
  with m.connect(timeout=15) as f:
   # First filesystem operation after connection/ownership check removes our exact hook.
   assert m.get(f,HOOK)==HOOK_BYTES;f.delete(HOOK);assert m.get(f,HOOK,True) is None;r['hook_removed']=True;m.write_json(out,r)
   startup(f);m.baseline(f,'720p')
   data=m.get(f,PROBE+'/result.txt',True);r['probe_present']=data is not None
   if data is not None:
    assert len(data)<=16424 and data==m.get(f,PROBE+'/result.txt');r['probe']=m.keep(P/'after',PROBE+'/result.txt',data)
   data=m.get(f,PROBE+'/input.txt',True);r['input_present']=data is not None
   if data is not None:
    assert len(data)<=4096 and data==m.get(f,PROBE+'/input.txt');r['input']=m.keep(P/'after',PROBE+'/input.txt',data)
   for n in s['before']:
    data=m.get(f,n);assert data==m.get(f,n);r['after'][n]=m.keep(P/'after',n,data);m.write_json(out,r)
   r['protected_unchanged']=all(r['after'][n]['sha256']==s['before'][n]['sha256'] for n in protected())
  r.update(completed=True,ended_utc=m.utc(),dashboard_returned=True)
 except BaseException as e:r['failure_type']=type(e).__name__;raise
 finally:m.write_json(out,r)
if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ['stage','launch','collect'];session();globals()[sys.argv[1]]()
