"""Resume only a freshly verified exact prefix; no duplicate uncertain append."""
import importlib.util,io,json,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('recovery576',K/'controller002.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)

def append_tail(f,name,expected,prefix,deadline,journal):
 assert 0<len(prefix)<=len(expected) and prefix==expected[:len(prefix)]
 assert c.m.get(f,name)==prefix,'Prefix changed since read-only qualification'
 for offset in range(len(prefix),len(expected),32768):
  if time.monotonic()>deadline:raise TimeoutError('Recovery deadline')
  journal(offset)
  f.storbinary('APPE '+name,io.BytesIO(expected[offset:offset+32768]),1024)
 assert c.m.get(f,name)==expected

def run():
 q=c.verify();c.boot_work_closed();c.budget()
 old=c.read(K/'stage001.json');probe=c.read(K/'recovery-probe002.json');sup=c.read(K/'supervisor001-stage.json')
 assert not old['completed'] and not old['temporary_hook_installed'] and sup['closed'] and not sup['completed']
 assert probe['completed'] and probe['exact_prefix'] and probe['hook_absent']
 assert probe['failed_stage_sha256']==c.m.sha((K/'stage001.json').read_bytes())
 assert probe['failed_supervisor_sha256']==c.m.sha((K/'supervisor001-stage.json').read_bytes())
 assert not (K/'launch001.json').exists()
 out=K/'stage002.json';assert not out.exists()
 r=dict(completed=False,utc=c.m.utc(),before=old['before'],staged={},writes=[],console_C_accessed=False,temporary_hook_installed=False,mode='720p',startup_listing=old['startup_listing'],failed_stage_sha256=probe['failed_stage_sha256'],recovery_probe_sha256=c.m.sha((K/'recovery-probe002.json').read_bytes()),recovery_admission_sha256=c.m.sha((K/'recovery-admission002.json').read_bytes()))
 c.m.write_json(out,r);deadline=time.monotonic()+1100
 partial=probe['partial_path'];prefix=Path(probe['private_partial_path']).read_bytes()
 assert len(prefix)==probe['partial_bytes'] and c.m.sha(prefix)==probe['partial_sha256']
 dirs={c.KIT}|{c.KIT+'/'+d for d in q['directories']}
 existing=set(old['staged'])|{partial}
 with c.m.connect(timeout=30) as f:
  c.m.baseline(f,'720p');assert c.startup(f,False)==old['startup_listing']
  assert 'xwn575' not in {n.lower() for n in c.m.names(f,'/E')}
  assert c.m.get(f,c.HOOK,True) is None
  for directory in dirs:
   expected={n.rsplit('/',1)[1]:n in dirs for n in dirs|existing if n.rsplit('/',1)[0]==directory}
   rows=c.m.names(f,directory)
   assert {n:bool(row['directory']) for n,row in rows.items()}==expected,directory
  for name,row in old['before'].items():
   b=c.m.get(f,name);assert len(b)==row['bytes'] and c.m.sha(b)==row['sha256'],name
  for name,row in old['staged'].items():
   b=c.m.get(f,name);assert len(b)==row['bytes'] and c.m.sha(b)==row['sha256'],name
   r['staged'][name]=row
  for name,h in q['runtime_module_pins'].items():assert c.m.sha(c.m.get(f,'/E/winnt/system32/'+name))==h
  assert c.m.get(f,partial)==prefix
  r['existing_files_reverified']=len(r['staged']);c.m.write_json(out,r)
  for rel,row in q['files'].items():
   name=c.KIT+'/'+rel
   if name in r['staged']:continue
   b=Path(row['path']).read_bytes();assert c.m.sha(b)==row['sha256'] and len(b)==row['bytes']
   r['writes'].append(name);c.m.write_json(out,r)
   def progress(offset):
    r['current_upload']=dict(path=name,next_offset=offset,bytes=len(b));c.m.write_json(out,r)
   if name==partial:append_tail(f,name,b,prefix,deadline,progress)
   else:
    assert c.m.get(f,name,True) is None
    for offset in range(0,max(1,len(b)),32768):
     if time.monotonic()>deadline:raise TimeoutError('Recovery deadline')
     progress(offset);f.storbinary(('STOR ' if offset==0 else 'APPE ')+name,io.BytesIO(b[offset:offset+32768]),1024)
    assert c.m.get(f,name)==b
   r['staged'][name]=dict(bytes=len(b),sha256=c.m.sha(b));c.m.write_json(out,r)
  assert len(r['staged'])==len(q['files'])+1
  assert c.m.get(f,c.HOOK,True) is None
  r['writes'].append(c.HOOK);c.m.write_json(out,r);c.m.put(f,c.HOOK,c.hook());assert c.m.get(f,c.HOOK)==c.hook()
  r['temporary_hook_installed']=True;c.m.write_json(out,r)
  c.m.baseline(f,'720p');c.startup(f,True)
 r.update(completed=True,ended_utc=c.m.utc());c.m.write_json(out,r)

if __name__=='__main__':
 assert sys.argv[1:]==['stage'];run()
