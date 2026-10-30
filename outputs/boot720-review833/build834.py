import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
W=Path(__file__).resolve().parents[2];K=W/'outputs/boot720-capacity834';P=Path('C:/xwn834/build001')
sys.path.insert(0,str(W/'tools'));from build_space import require_space
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists()
r={'passed':False,'space':require_space(P,20.05),'physical_access':False};P.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
try:
 r['sdk_commit']=subprocess.check_output(['git','-C','C:/nxdk','rev-parse','HEAD'],text=True).strip()
 assert r['sdk_commit']=='58427c078b4ccb0121f359b6b6c536b3b2914976'
 for n in ['main.c','report-path.h','Makefile']:(P/n).write_bytes((K/n).read_bytes())
 args=['powershell','-NoProfile','-File','C:/Homebrew/Invoke-Console.ps1','-Console','xbox','-WorkingDirectory',str(P),'-Command','make -j4'];r['command']=args
 with (P/'build.log').open('wb') as f:cp=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 assert cp.returncode==0
 r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:
 r['files']={n:{'bytes':(P/n).stat().st_size,'sha256':sha(P/n)} for n in ['main.c','report-path.h','Makefile','main.exe','bin/default.xbe','build.log'] if (P/n).exists()}
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
