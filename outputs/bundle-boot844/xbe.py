import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent; P=Path('D:/xwn-bundle844/xbe001'); H=Path('D:/xwn-bundle844/host001'); C=Path('D:/xwn-bundle844/chain001')
sys.path.insert(0,str(K.parents[1]/'tools')); from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists()
r={'passed':False,'space':require_space(P,20.2),'physical_access':False}; P.mkdir(parents=True)
try:
 m=json.loads((K/'host001.json').read_text()); assert m['passed']; assert sha(H/'embed.h')==m['files']['embed.h']
 r['sdk_commit']=subprocess.check_output(['git','-C','C:/nxdk','rev-parse','HEAD'],text=True).strip(); assert r['sdk_commit']=='58427c078b4ccb0121f359b6b6c536b3b2914976'
 names=['main.c','Makefile','layout.c','layout.h','plan.c','plan.h','page.c','page.h']
 for n in names: assert sha(K/n)==m['sources'][n]; (P/n).write_bytes((K/n).read_bytes())
 (P/'embed.h').write_bytes((H/'embed.h').read_bytes())
 cmd=['powershell','-NoProfile','-File','C:/Homebrew/Invoke-Console.ps1','-Console','xbox','-WorkingDirectory',str(P),'-Command','make -j4']; r['command']=cmd
 with (P/'build.log').open('wb') as f: cp=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 r['exit_code']=cp.returncode; assert cp.returncode==0
 assert (P/'main.exe').read_bytes().count((H/'bridge.bin').read_bytes())==1
 assert (P/'main.exe').read_bytes().count((C/'image-crom.bin').read_bytes())==1
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['files']={str(p.relative_to(P)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in P.rglob('*') if p.is_file()}; r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat(); (K/'xbe001.json').write_text(json.dumps(r,indent=2)+'\n')
