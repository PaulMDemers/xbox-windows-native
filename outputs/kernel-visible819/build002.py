"""Build unique kernel-only819. Does not stage or launch hardware."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn819/build002')
sys.path.insert(0,str(K.parents[1]/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists()
r={'passed':False,'physical_access':False,'space':require_space(P,20.15)};P.mkdir(parents=True)
names=['main.c','layout.c','layout.h','combined.c','transaction819.c','transaction.h','encoder.c','xcal_bus.c','xcal_bus.h','xcal_table.h','delay_candidate.h','gpu_preserving.c','gpu_types.h','Makefile']
try:
 r['sdk_commit']=subprocess.check_output(['git','-C','C:/nxdk','rev-parse','HEAD'],text=True).strip()
 assert r['sdk_commit']=='58427c078b4ccb0121f359b6b6c536b3b2914976'
 for n in names:(P/n).write_bytes((K/n).read_bytes())
 cmd=['powershell','-NoProfile','-File','C:/Homebrew/Invoke-Console.ps1','-Console','xbox','-WorkingDirectory',str(P),'-Command','make -j4'];r['command']=cmd
 with (P/'build.log').open('wb') as f:cp=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 r['exit_code']=cp.returncode;assert cp.returncode==0
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['files']={n:{'sha256':sha(P/n),'bytes':(P/n).stat().st_size} for n in names+['main.obj','layout.obj','combined.obj','main.exe','bin/default.xbe','build.log'] if (P/n).exists()}
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(K/'build002.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS kernel819 build; no hardware access')
