"""Build normalized720p Xromwell836 handoff with diagnostic firmware836. Does not stage or launch hardware."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn837/build001')
sys.path.insert(0,str(K.parents[1]/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists()
r={'passed':False,'physical_access':False,'space':require_space(P,20.15)};P.mkdir(parents=True)
names=['main.c','Makefile','layout.c','layout.h','plan.c','plan.h','page.c','page.h']
try:
 h=Path('C:/xwn837/host006');meta=json.loads((K/'host006.json').read_text());assert meta['passed']
 for n,v in meta['files'].items():assert sha(h/n)==v
 for n,v in meta['sources'].items():assert sha(K/n)==v
 assert json.loads((K/'cpu-run010.json').read_text())['passed']
 (P/'embed.h').write_bytes((h/'embed.h').read_bytes())
 r['sdk_commit']=subprocess.check_output(['git','-C','C:/nxdk','rev-parse','HEAD'],text=True).strip()
 assert r['sdk_commit']=='58427c078b4ccb0121f359b6b6c536b3b2914976'
 for n in names:(P/n).write_bytes((K/n).read_bytes())
 cmd=['powershell','-NoProfile','-File','C:/Homebrew/Invoke-Console.ps1','-Console','xbox','-WorkingDirectory',str(P),'-Command','make -j4'];r['command']=cmd
 with (P/'build.log').open('wb') as f:cp=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 r['exit_code']=cp.returncode;assert cp.returncode==0
 assert (P/'main.exe').read_bytes().count((h/'bridge.bin').read_bytes())==1
 assert (P/'main.exe').read_bytes().count(Path('C:/xwn837/chain002/image-crom.bin').read_bytes())==1
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['files']={n:{'sha256':sha(P/n),'bytes':(P/n).stat().st_size} for n in names+['embed.h','page.obj','plan.obj','layout.obj','main.obj','main.exe','bin/default.xbe','build.log'] if (P/n).exists()}
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS kernel836 build; no hardware access')
