"""Disable only this one-shot hook, preserve all returned diagnostic evidence."""
import json,sys
from pathlib import Path
from physical import K,P,START,NORMAL,HOOK,TARGET,baseline,script,connect,get,names,sha,utc,write_json
from oracle import verify_log,verify_pixels
case,mode=sys.argv[1:];assert case in ('control001','interlace001') and mode in ('720p','1080i')
out=K/(case+'-collection.json');assert not out.exists()
stage=json.loads((K/(case+'-stage.json')).read_text());assert stage['completed']
private=P/case/'after';assert not private.exists();private.mkdir()
r=dict(utc=utc(),completed=False,hook_removed=False,files={},mode=mode,case=case,console_C_accessed=False)
write_json(out,r)
try:
 with connect() as f:
  # Preserve exact hook under owned evidence namespace before any interpretation.
  assert get(f,HOOK)==script(case)
  used='/E/xwn428/'+case+'/startup-used.cmd';assert get(f,used,True) is None
  f.rename(HOOK,used);assert get(f,HOOK,True) is None and get(f,used)==script(case)
  r['hook_removed']=True;write_json(out,r)
  baseline(f,mode);assert sha(get(f,NORMAL))==stage['before'][NORMAL]['sha256']
  r['directory']=names(f,'/E/xwn428/'+case)
  for name in r['directory']:
   assert not r['directory'][name]['directory'] and '/' not in name and '\\' not in name
   b=get(f,'/E/xwn428/'+case+'/'+name);assert b==get(f,'/E/xwn428/'+case+'/'+name)
   q=private/name;q.write_bytes(b);r['files'][name]=dict(bytes=len(b),sha256=sha(b),path=str(q))
   write_json(out,r)
  for name in ('sysevent.evt','appevent.evt'):
   b=get(f,'/E/winnt/system32/config/'+name);assert b==get(f,'/E/winnt/system32/config/'+name)
   q=private/name;q.write_bytes(b);r['files'][name]=dict(bytes=len(b),sha256=sha(b),path=str(q))
  assert sha(get(f,'/E/xwn428/probe.exe'))==stage['probe_sha256'];r['protected_code_exact']=True
 r['collection_complete']=True;write_json(out,r)
 verify_log((private/'result.log').read_text())
 r['pixels_verified']=sum(verify_pixels((private/('capture-%02d.bgrx'%i)).read_bytes(),i//2) for i in range(8))
 r.update(completed=True,scoped_pattern_and_scanout_passed=True,full_allocation_audit=False,signal_quality_qualified=False,ended_utc=utc())
except BaseException as exc:r['error']=repr(exc);raise
finally:write_json(out,r)
print(json.dumps({k:r[k] for k in ('completed','pixels_verified','scoped_pattern_and_scanout_passed')}))
