"""MIT. New journal for verified recovery of an interrupted pre-hook upload."""
import importlib.util,io,json,time
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('resume565',K/'controller003.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
q=c.verify();c.boot_work_closed();c.budget()
old=c.read(K/'stage001.json');sup=c.read(K/'supervisor-stage.json')
assert sup['closed'] and not sup['completed'] and not old['completed'] and not old['temporary_hook_installed']
assert not (K/'launch001.json').exists() and c.read(K/'transport-probe005.json')['verified']
out=K/'stage003.json';assert not out.exists()
r=dict(completed=False,utc=c.m.utc(),before=old['before'],staged={},writes=[],console_C_accessed=False,temporary_hook_installed=False,mode='720p',recovered_from=c.m.sha((K/'stage001.json').read_bytes()),transport='1024-byte blocks, 1ms pacing, exact full readback',startup_listing=old['startup_listing'])
c.m.write_json(out,r);deadline=time.monotonic()+1750
with c.m.connect(timeout=15) as f:
 c.m.baseline(f,'720p');assert c.startup(f,False)==old['startup_listing']
 assert 'xwn565' not in {n.lower() for n in c.m.names(f,'/E')}
 assert set(c.m.names(f,c.KIT))=={'owner.json','game'}
 for n,row in old['before'].items():assert c.m.sha(c.m.get(f,n))==row['sha256'],n
 for name,h in q['runtime_module_pins'].items():assert c.m.sha(c.m.get(f,'/E/winnt/system32/'+name))==h
 for n,row in old['staged'].items():assert c.m.sha(c.m.get(f,n))==row['sha256'];r['staged'][n]=row
 seen=[];todo=[c.KIT+'/game'];dirs=set()
 while todo:
  d=todo.pop();assert d not in dirs;dirs.add(d)
  for name,row in c.m.names(f,d).items():
   assert name not in ('','.','..') and '/' not in name and chr(92) not in name
   n=d+'/'+name
   if row['directory']:todo.append(n)
   else:seen.append(n)
 assert dirs=={c.KIT+'/'+d for d in q['directories']}
 assert set(seen)=={n for n in old['writes'] if n.startswith(c.KIT+'/game/') and n not in dirs}
 partial=[n for n in seen if n not in r['staged']];assert partial==[old['writes'][-1]]
 for n in partial:
  b=c.m.get(f,n);expected=Path(q['files'][n[len(c.KIT)+1:]]['path']).read_bytes()
  assert expected.startswith(b)
  r['interrupted_file']=dict(path=n,bytes=len(b),sha256=c.m.sha(b),exact_expected_prefix=True)
 c.m.write_json(out,r)
 for name,row in q['files'].items():
  n=c.KIT+'/'+name
  if n in r['staged']:continue
  assert time.monotonic()<deadline
  b=Path(row['path']).read_bytes();r['writes'].append(n);c.m.write_json(out,r);start=time.monotonic()
  def pace(block):
   if time.monotonic()>deadline or time.monotonic()-start>180:raise TimeoutError('Bounded paced upload')
   time.sleep(.001)
  f.storbinary('STOR '+n,io.BytesIO(b),1024,callback=pace)
  assert c.m.get(f,n)==b
  r['staged'][n]=dict(bytes=len(b),sha256=c.m.sha(b));c.m.write_json(out,r)
 assert len(r['staged'])==len(q['files'])+1
 assert c.m.get(f,c.HOOK,True) is None
 r['writes'].append(c.HOOK);c.m.write_json(out,r);c.m.put(f,c.HOOK,c.hook());assert c.m.get(f,c.HOOK)==c.hook()
 r['temporary_hook_installed']=True;c.m.write_json(out,r)
 c.m.baseline(f,'720p');c.startup(f,True)
r.update(completed=True,ended_utc=c.m.utc());c.m.write_json(out,r)
print('Recovered stage complete; all package files exact, hook installed last')
