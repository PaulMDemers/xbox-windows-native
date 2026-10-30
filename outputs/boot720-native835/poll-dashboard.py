"""One read-only authentication attempt; never sends SITE or retries a launch."""
import json,sys
from pathlib import Path
import physical as h
K=Path(__file__).resolve().parent;assert len(sys.argv)==2
p=K/sys.argv[1];assert p.parent==K and p.name.startswith('poll') and p.suffix=='.json' and not p.exists()
r={'utc':h.utc(),'dashboard_authenticated':False,'launch_requested':False,'windows_boot_proved':False}
try:
 with h.connect(timeout=3) as f:
  owner=h.get(f,h.R+'/owner835.json');s=h.read(K/'stage001.json')
  assert h.sha(owner)==s['staged'][h.R+'/owner835.json']['sha256']
  r['entries']=h.names(f,h.R);r['dashboard_authenticated']=True
except Exception as e:r['unavailable_type']=type(e).__name__
h.save(p,r);print(json.dumps(r))
