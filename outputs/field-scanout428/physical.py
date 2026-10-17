"""One new user-mode pattern observation; preserves existing startup and drivers."""
import hashlib,importlib.util,json,os,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('E:/xwn428')
sys.path.insert(0,str(W/'outputs/demo-audio-level256'))
from common001 import connect,get,put,names,sha,ticket,utc
sys.path.insert(0,str(W/'outputs/surface-bridge260'));from atomic_json import write_json
s=importlib.util.spec_from_file_location('selector428',W/'tools/configure-e-display.py');selector=importlib.util.module_from_spec(s);s.loader.exec_module(selector)
START='/E/documents and settings/all users/start menu/programs/startup'
NORMAL=START+'/xwnsetup.cmd';HOOK=START+'/xwn428.cmd';TARGET='/E/Applications/XWNEBoot/default.xbe'
policy=json.loads((W/'tools/e-display-policy.json').read_text())
def protected():
 r=json.loads((W/'outputs/demo-integration399/accepted-state.json').read_text())
 return {p:h for p,h in r['verified_files'].items() if p.startswith('/E/') and '/config/' not in p.lower()}
def baseline(f,mode):
 assert selector.inspect(f,policy)[0]==mode
 for p,h in protected().items():
  if p!=TARGET:assert sha(get(f,p))==h,p
def script(case):
 return ('@echo off\r\ncd /d C:\\xwn428\\'+case+'\r\nif exist result.log goto done\r\nC:\\xwn428\\probe.exe\r\n:done\r\nexit\r\n').encode('ascii')
def stage(case,mode):
 out=K/(case+'-stage.json');assert not out.exists()
 r=json.loads((K/'review001.json').read_text());assert r['passed']
 exe=(P/'build001/probe.exe').read_bytes();assert sha(exe)==r['binary_sha256']
 rec=dict(utc=utc(),completed=False,case=case,mode=mode,writes=[],console_C_accessed=False,launch_requested=False)
 private=P/case;assert not private.exists();private.mkdir()
 write_json(out,rec)
 with connect() as f:
  baseline(f,mode);assert get(f,HOOK,True) is None
  for p in [NORMAL,TARGET,'/E/winnt/system32/config/sysevent.evt','/E/winnt/system32/config/appevent.evt']:
   b=get(f,p);assert b==get(f,p);name=p.rsplit('/',1)[1];(private/name).write_bytes(b)
   rec.setdefault('before',{})[p]=dict(sha256=sha(b),bytes=len(b),path=str(private/name))
  listing=names(f,'/E')
  if case=='control001':assert 'xwn428' not in {n.lower() for n in listing};f.mkd('/E/xwn428');put(f,'/E/xwn428/probe.exe',exe)
  else:assert get(f,'/E/xwn428/probe.exe')==exe
  assert case not in names(f,'/E/xwn428');f.mkd('/E/xwn428/'+case)
  rec['writes'].append(HOOK);write_json(out,rec);put(f,HOOK,script(case))
  assert sha(get(f,NORMAL))==rec['before'][NORMAL]['sha256'];baseline(f,mode)
  rec.update(completed=True,ended_utc=utc(),hook_sha256=sha(script(case)),probe_sha256=sha(exe))
 write_json(out,rec);print('New one-shot pattern staged; original startup and drivers unchanged')
def launch(case,mode):
 out=K/(case+'-launch.json');assert not out.exists()
 stage=json.loads((K/(case+'-stage.json')).read_text());assert stage['completed'] and stage['mode']==mode
 with connect() as f:
  baseline(f,mode);assert get(f,HOOK)==script(case)
  assert get(f,'/E/xwn428/'+case+'/result.log',True) is None
  rec=dict(utc=utc(),requested=True,command=r'SITE EXEC E:\Applications\XWNEBoot\default.xbe',reply=None)
  write_json(out,rec);f.sock.settimeout(20)
  try:rec['reply']=f.sendcmd(rec['command'])
  except Exception as e:rec['uncertain_reply']=type(e).__name__
  write_json(out,rec)
 print('One launch request recorded; never retry this case')
if __name__=='__main__':
 action,case,mode=sys.argv[1:];assert case in ('control001','interlace001') and mode in ('720p','1080i')
 assert action in ('stage','launch');globals()[action](case,mode)
