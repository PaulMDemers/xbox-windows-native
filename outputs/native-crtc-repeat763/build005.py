"""Fresh nxdk763 with exact host-tested bridge and horizontal timing763 payload embedded."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn763/build002');H=Path('C:/xwn763/host002')
sys.path.insert(0,str(K.parents[1]/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists()
r={'passed':False,'physical_access':False,'space':require_space(P,20.15)};P.mkdir(parents=True)
names=['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','Makefile']
try:
 b=json.loads((K/'host002.json').read_text());assert b['passed']
 assert json.loads((K/'cpu-run001.json').read_text())['passed'] and json.loads((K/'integration003.json').read_text())['passed']
 for n,v in b['files'].items():assert sha(H/n)==v
 for n,v in b['sources'].items():assert sha(K/n)==v
 r['sdk_commit']=subprocess.check_output(['git','-C','C:/nxdk','rev-parse','HEAD'],text=True).strip()
 assert r['sdk_commit']=='58427c078b4ccb0121f359b6b6c536b3b2914976'
 for n in names:(P/n).write_bytes((K/n).read_bytes())
 header=(H/'payload_meta.h').read_text()
 for symbol,file in [('bridge_image','bridge.bin'),('payload_image','payload.bin')]:
  data=(H/file).read_bytes();header+='\nstatic const uint8_t '+symbol+'['+str(len(data))+']={'+','.join(hex(v) for v in data)+'};\n'
 (P/'embed.h').write_text(header)
 cmd=['powershell','-NoProfile','-File','C:/Homebrew/Invoke-Console.ps1','-Console','xbox','-WorkingDirectory',str(P),'-Command','make -j4'];r['command']=cmd
 with (P/'build.log').open('wb') as f:cp=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 r['exit_code']=cp.returncode;assert cp.returncode==0
 pe=(P/'main.exe').read_bytes()
 for n in ['bridge.bin','payload.bin']:assert pe.count((H/n).read_bytes())==1,'embedded bytes not unique/exact'
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['files']={n:{'sha256':sha(P/n),'bytes':(P/n).stat().st_size} for n in names+['embed.h','main.obj','layout.obj','plan.obj','page002.obj','main.exe','bin/default.xbe','build.log'] if (P/n).exists()}
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(K/'build002.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS nxdk763 build; exact bridge/payload embedded')
