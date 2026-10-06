"""Read-only physical baseline availability check; no deployment or launch."""
import importlib.util,json,os,sys,datetime
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];target=k/'preflight.json';assert not target.exists()
spec=importlib.util.spec_from_file_location('soak_physical_read',k.parent/'fatx0098-soak3/physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=dict(scope=__doc__,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=True,remote_writes=False,windows_launch=False)
f=m.FTP()
try:
 f.connect(os.environ['XWN_FTP_HOST'],timeout=5);f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
 r['dashboard_ftp_available']=True;m.owner(f);r['ownership_verified']=True
 r['checks']=m.checks(f,True);r['startup_sha256']=m.sha(m.get(f,m.startup))
 r['passed']=m.passed(r['checks']) and r['startup_sha256']==m.baseline['startup_sha256']
except Exception as error:r.update(passed=False,error=type(error).__name__,detail=str(error))
finally:f.close();target.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['dashboard_ftp_available','ownership_verified','passed','error','detail'] if n in r},indent=2))
