"""One bounded post-photo authenticated dashboard read; no launch/write."""
from pathlib import Path
import json,datetime,sys
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K));from physical009 import connect,names
out=K/'dashboard002.json';assert not out.exists()
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authenticated':False,'console_writes':False,'launch_requested':False}
try:
 with connect() as f:
  e=names(f,'/E');apps=names(f,'/E/Applications')
  assert 'XWNMode808' in apps
  r.update(authenticated=True,e_entries=len(e),application_entries=len(apps),report_entries=sorted(n for n in e if n.lower().startswith('xwn-mode808-')))
except BaseException as error:r['failure_type']=type(error).__name__;raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS dashboard authenticated after photo/reset workflow')
