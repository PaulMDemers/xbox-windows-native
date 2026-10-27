"""Frozen private nxdk build; must run inside the shared build lease."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn694/build001')
sys.path.insert(0,str(K.parents[1]/'tools'))
from build_space import require_space
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not P.exists() and not (K/'build001.json').exists()
r={'passed':False,'scope':'kernel-checked owned-page native checkpoint; deliberate hold, not Xcalibur initialization','space':require_space(P,20.1)}
P.mkdir(parents=True)
try:
 r['sdk_commit']=subprocess.check_output(['git','-C','C:/nxdk','rev-parse','HEAD'],text=True).strip()
 assert r['sdk_commit']=='58427c078b4ccb0121f359b6b6c536b3b2914976'
 for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page.c','page.h','stub.S','Makefile']:(P/n).write_bytes((K/n).read_bytes())
 cmd=['powershell','-NoProfile','-File','C:/Homebrew/Invoke-Console.ps1','-Console','xbox','-WorkingDirectory',str(P),'-Command','make -j4']
 r['command']=cmd
 with (P/'build.log').open('wb') as log:
  cp=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=180)
 r['exit_code']=cp.returncode
 assert cp.returncode==0
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['files']={n:{'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest(),'bytes':(P/n).stat().st_size} for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page.c','page.h','stub.S','Makefile','main.obj','layout.obj','plan.obj','page.obj','stub.obj','main.exe','bin/default.xbe','build.log'] if (P/n).exists()}
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
print('Build passed')
