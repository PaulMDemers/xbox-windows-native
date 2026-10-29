"""Bounded authenticated dashboard read, no launch or console writes."""
from pathlib import Path
import json,datetime,sys
K=Path(__file__).resolve().parent;P=Path('C:/xwn801')
sys.path.insert(0,str(K));from physical007 import connect,names
out=K/'dashboard001.json';assert not out.exists()
source=Path('C:/xwn800/connection.json');configuration=json.loads(source.read_text())
assert configuration['host']=='192.168.50.66'
target=P/'connection.json'
if target.exists():assert json.loads(target.read_text())==configuration
else:
 with target.open('x') as f:json.dump(configuration,f)
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authenticated':False,'console_writes':False,'launch_requested':False,'host':'192.168.50.66','configuration':'Active private session configuration; credentials omitted'}
try:
 with connect() as f:
  e=names(f,'/E');apps=names(f,'/E/Applications')
  assert not any(n.lower().startswith('xwn-mode801-') for n in e)
  assert not any(n.lower()=='xwnmode801' for n in apps)
  r.update(authenticated=True,fresh_owned_namespace_absent=True,e_entries=len(e),application_entries=len(apps))
except BaseException as error:r['failure_type']=type(error).__name__;raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS authenticated1.6 dashboard;801 namespace absent; no launch or write')
