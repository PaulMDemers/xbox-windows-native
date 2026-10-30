"""One authenticated E-only dashboard read; unique receipt, no launch."""
from pathlib import Path
import datetime,json,sys
from physical009 import connect,names
K=Path(__file__).resolve().parent
assert len(sys.argv)==2 and sys.argv[1] in ['001','002','003']
out=K/('dashboard'+sys.argv[1]+'.json');assert not out.exists()
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reachable=False,authenticated=False,console_writes=False,launch_requested=False)
try:
 with connect() as f:
  e=names(f,'/E');apps=names(f,'/E/Applications')
  r.update(reachable=True,authenticated=True,e_entries=len(e),application_entries=len(apps),report_entries=sorted(n for n in e if n.lower().startswith('xwn-mode817-')))
except BaseException as error:r['failure_type']=type(error).__name__;raise
finally:
 with out.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print('PASS817 authenticated dashboard; no console writes')
