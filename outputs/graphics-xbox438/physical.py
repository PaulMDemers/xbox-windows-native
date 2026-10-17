"""One scoped physical sample run; credentials supplied in environment, never saved."""
import json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=W/'work/graphics438'
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from physical import baseline,connect,get,put,names,sha,utc,write_json,START,NORMAL,TARGET,protected
REMOTE='/E/xwn438-kit';RESULT='/E/xwn438';HOOK=START+'/xwn438.cmd'
def hook():
 return b'@echo off\r\nif exist C:\\xwn438 goto done\r\nC:\\xwn438-kit\\run438.exe\r\n:done\r\nexit\r\n'
def stage():
 out=K/'physical001-stage.json';assert not out.exists()
 package=json.loads((K/'package001.json').read_text());assert package['passed']
 pc=json.loads((K.parent/'graphics-nt5437/runtime-review002.json').read_text());assert pc['all_allowed_cases_passed']
 private=P/'physical001';assert not private.exists();private.mkdir()
 r=dict(utc=utc(),completed=False,writes=[],before={},console_C_accessed=False,launch_requested=False)
 write_json(out,r)
 try:
  with connect() as f:
   baseline(f,'720p');listing=names(f,START)
   assert set(n.lower() for n in listing)<={'xwnsetup.cmd','desktop.ini'},'Unknown startup entry; inspect before staging'
   root=names(f,'/E');assert not {'xwn438','xwn438-kit'}&{n.lower() for n in root}
   for path in [NORMAL,TARGET]+['/E/winnt/system32/config/'+n for n in ['system','software','sam','security','default','sysevent.evt','appevent.evt']]:
    data=get(f,path);assert data==get(f,path)
    dest=private/'before'/path.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    r['before'][path]=dict(path=str(dest),bytes=len(data),sha256=sha(data));write_json(out,r)
   modules=json.loads((W/'outputs/crypto-path425/modules001.json').read_text())['modules']
   for name in ['kernel32.dll','user32.dll','advapi32.dll','gdi32.dll']:
    assert sha(get(f,'/E/winnt/system32/'+name))==modules[name],name
   r['protected_files']=protected();r['startup_listing']=listing;write_json(out,r)
   f.mkd(REMOTE)
   for name,row in package['files'].items():
    data=Path(row['path']).read_bytes();assert sha(data)==row['sha256']
    put(f,REMOTE+'/'+name,data);r['writes'].append(REMOTE+'/'+name);write_json(out,r)
   assert get(f,HOOK,True) is None
   r['writes'].append(HOOK);write_json(out,r);put(f,HOOK,hook())
   assert sha(get(f,NORMAL))==r['before'][NORMAL]['sha256'];baseline(f,'720p')
   r.update(completed=True,hook_sha256=sha(hook()),mode='720p',ended_utc=utc());write_json(out,r)
 except BaseException as e:r['failure']=repr(e);write_json(out,r);raise
 print('438 staged with exact readback; no launch yet.')
def launch():
 out=K/'physical001-launch.json';assert not out.exists()
 stage=json.loads((K/'physical001-stage.json').read_text());assert stage['completed']
 with connect() as f:
  baseline(f,'720p');assert get(f,HOOK)==hook()
  assert 'xwn438' not in {n.lower() for n in names(f,'/E')}
  for name,row in json.loads((K/'package001.json').read_text())['files'].items():assert sha(get(f,REMOTE+'/'+name))==row['sha256']
  r=dict(utc=utc(),requested=True,command=r'SITE EXEC E:\Applications\XWNEBoot\default.xbe')
  write_json(out,r);f.sock.settimeout(20)
  try:r['reply']=f.sendcmd(r['command'])
  except Exception as e:r['uncertain_reply']=type(e).__name__
  write_json(out,r)
 print('One launch request recorded. Do not retry this attempt.')
def collect():
 out=K/'physical001-collection.json';assert not out.exists()
 stage=json.loads((K/'physical001-stage.json').read_text());assert stage['completed']
 assert json.loads((K/'physical001-launch.json').read_text())['requested']
 private=P/'physical001/after';assert not private.exists();private.mkdir()
 r=dict(utc=utc(),completed=False,hook_removed=False,files={},console_C_accessed=False)
 write_json(out,r)
 try:
  with connect() as f:
   assert get(f,HOOK)==hook()
   used=REMOTE+'/startup-used.cmd';assert get(f,used,True) is None
   f.rename(HOOK,used);assert get(f,HOOK,True) is None and get(f,used)==hook()
   r['hook_removed']=True;write_json(out,r)
   baseline(f,'720p');assert sha(get(f,NORMAL))==stage['before'][NORMAL]['sha256']
   assert sha(get(f,TARGET))==stage['before'][TARGET]['sha256']
   for name,row in json.loads((K/'package001.json').read_text())['files'].items():assert sha(get(f,REMOTE+'/'+name))==row['sha256']
   root=names(f,'/E');paths=[REMOTE+'/startup-used.cmd']
   if 'xwn438' in {n.lower() for n in root}:
    listing=names(f,RESULT);r['result_directory']=listing
    for name,item in listing.items():
     assert not item['directory'] and '/' not in name and '\\' not in name;paths.append(RESULT+'/'+name)
   for name in ['system','software','sam','security','default','sysevent.evt','appevent.evt']:paths.append('/E/winnt/system32/config/'+name)
   for path in paths:
    data=get(f,path);assert data==get(f,path)
    dest=private/path.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    r['files'][path]=dict(path=str(dest),bytes=len(data),sha256=sha(data));write_json(out,r)
   r.update(completed=True,protected_code_exact=True,mode='720p',full_allocation_audit=False,ended_utc=utc());write_json(out,r)
 except BaseException as e:r['failure']=repr(e);write_json(out,r);raise
 print('438 collected; temporary startup disabled; results not yet qualified.')
if __name__=='__main__':
 action=sys.argv[1];assert action in ['stage','launch','collect'];globals()[action]()
