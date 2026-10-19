"""MIT. Remove only two identified completed partial probe files, never game data."""
import importlib.util,json,time
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('clean565',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.verify();assert not (K/'launch001.json').exists();out=K/'probe-cleanup001.json';assert not out.exists()
r=dict(utc=c.m.utc(),removed=[],completed=False,correction='Earlier timed-out probes reported immediate RETR absence, but subsequent LIST still showed partial files. Preserve that premature cleanup result; verify LIST after removal now.')
c.m.write_json(out,r)
with c.m.connect(timeout=5) as f:
 c.startup(f,False)
 for name in ['transport-probe2.bin','transport-probe4.bin']:
  n=c.KIT+'/'+name;b=c.m.get(f,n);assert (bytes(range(256))*16384).startswith(b) and len(b)>0
  r['removed'].append(dict(path=n,bytes=len(b),sha256=c.m.sha(b)));c.m.write_json(out,r);f.delete(n)
 for _ in range(2):
  time.sleep(3);assert set(c.m.names(f,c.KIT))=={'owner.json','game'}
r.update(completed=True,ended_utc=c.m.utc(),twice_listed_absent=True);c.m.write_json(out,r);print('Two owned partial probes removed; directory listing confirms twice')
