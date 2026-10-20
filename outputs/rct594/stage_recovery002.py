"""MIT. Validate partial staging without replaying its move or config writes."""
import importlib.util,json,time
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('recover594',K/'controller002.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
m=c.m
def run():
 q=c.verify();c.boot_work_closed();c.budget();old=c.read(K/'stage001.json');sup=c.read(K/'supervisor001-stage.json')
 assert not old['completed'] and not old['temporary_hook_installed'] and sup['closed'] and not sup['completed']
 assert not (K/'launch001.json').exists()
 out=K/'stage002.json';assert not out.exists()
 r=dict(completed=False,utc=m.utc(),before={},staged={},writes=[],console_C_accessed=False,temporary_hook_installed=False,mode='720p',recovery_of_failed_stage_sha256=m.sha((K/'stage001.json').read_bytes()),prior_move_not_replayed=True)
 m.write_json(out,r)
 with m.connect(timeout=15) as f:
  m.baseline(f,'720p');r['startup_listing']=c.startup(f,False)
  assert 'xwn593' not in {n.lower() for n in m.names(f,'/E')}
  assert 'game' not in m.names(f,'/E/xwn586-kit')
  assert set(m.names(f,c.KIT))=={'owner.json','game'}
  assert m.sha(m.get(f,c.KIT+'/owner.json'))==old['staged'][c.KIT+'/owner.json']['sha256']
  assert m.get(f,c.USED,True) is None and set(c.inventory(f,c.KIT+'/game'))==set(q['reuse_expected'])
 deadline=time.monotonic()+600
 for n,row in old['before'].items():
  b=m.cold_pair(n,r,out);assert b is not None and m.sha(b)==row['sha256'],n
  r['before'][n]=m.keep(c.P/'before2',n,b);m.write_json(out,r)
 r['staged'][c.KIT+'/owner.json']=old['staged'][c.KIT+'/owner.json']
 for name,row in q['files'].items():
  if not name.startswith('game/'):continue
  assert time.monotonic()<deadline
  n=c.KIT+'/'+name;b=m.cold_pair(n,r,out)
  assert b is not None and len(b)==row['bytes'] and m.sha(b)==row['sha256'],n
  r['staged'][n]=dict(bytes=len(b),sha256=m.sha(b));m.write_json(out,r)
 with m.connect(timeout=15) as f:
  m.baseline(f,'720p');assert c.startup(f,False)==r['startup_listing']
  assert 'xwn593' not in {n.lower() for n in m.names(f,'/E')}
  assert set(m.names(f,c.KIT))=={'owner.json','game'}
  assert set(c.inventory(f,c.KIT+'/game'))==set(q['reuse_expected'])
  assert m.sha(m.get(f,c.KIT+'/owner.json'))==r['staged'][c.KIT+'/owner.json']['sha256']
  for n,row in r['before'].items():assert m.sha(m.get(f,n))==row['sha256']
  name=c.KIT+'/run593.exe';b=Path(q['files']['run593.exe']['path']).read_bytes()
  assert m.get(f,name,True) is None
  r['writes'].append(dict(action='put-new-helper-once',path=name));m.write_json(out,r);m.put(f,name,b)
  assert m.get(f,name)==b;r['staged'][name]=dict(bytes=len(b),sha256=m.sha(b));m.write_json(out,r)
  for name,h in q['runtime_module_pins'].items():assert m.sha(m.get(f,'/E/winnt/system32/'+name))==h
  assert m.get(f,c.HOOK,True) is None
  r['writes'].append(dict(action='install-hook-last',path=c.HOOK));m.write_json(out,r);m.put(f,c.HOOK,c.hook())
  assert m.get(f,c.HOOK)==c.hook();r['temporary_hook_installed']=True;m.write_json(out,r)
  m.baseline(f,'720p');c.startup(f,True)
 r.update(completed=True,ended_utc=m.utc());m.write_json(out,r)
if __name__=='__main__':run()
