"""Audit installed payload after dashboard return; close835 without relaunch."""
import json
from pathlib import Path
import physical as h
K=h.K; out=K/'audit001.json'
assert not out.exists() and h.read(K/'collection001.json')['completed']
r={'utc':h.utc(),'passed':False,'critical_payload':{},'hook':'none installed','relaunch':False}
h.save(out,r)
try:
 with h.connect() as f:
  s=h.read(K/'stage001.json')
  assert h.sha(h.get(f,h.R+'/owner835.json'))==s['staged'][h.R+'/owner835.json']['sha256']
  for p,v in h.critical().items():
   b=h.get(f,p); match=len(b)==v['bytes'] and h.sha(b)==v['sha256']
   r['critical_payload'][p]={'bytes':len(b),'sha256':h.sha(b),'matches_installed':match}
   if not match:
    dest=h.P/'changed001'/p.removeprefix('/E/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
   h.save(out,r)
  r['e_root_live_entries']=len(h.names(f,'/E'))
 assert all(v['matches_installed'] for v in r['critical_payload'].values())
 c=h.read(K/'collection001.json')
 r['preparation_phases']=[v['data']['phase'] for v in c['reports'].values()]
 last=list(c['reports'].values())[-1]['data']
 r['last_preparation']=last
 assert last['sdk_mode']==[1280,720,32,60] and last['framebuffer']['admitted']
 r['passed']=True
except BaseException as e:
 r['error']=repr(e);raise
finally:h.save(out,r)
closed={'utc':h.utc(),'state':'CLOSED','boot_result':'FAIL: FreeLoader SYSTEM.ALT error before Windows kernel entry',
 'display_result':'Readable loader dialog at retained720p; repetitive background glyphs, not a desktop',
 'audit':'audit001.json','collection':'collection001.json','photo':'screen001.json',
 'console':'Dashboard independently authenticated; cause of return not established',
 'host_runtime':'none owned','hook':'none installed','next':'Fresh836 FATX root chain fix; source-only reuse with pins; never relaunch or recollect835'}
h.save(K/'closed001.json',closed)
print(json.dumps({'closed':closed,'critical_files':len(r['critical_payload']),'phases':r['preparation_phases']},indent=2))
