import os,subprocess,shutil,json,hashlib,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn840/build001')
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not P.exists() and not (K/'build001.json').exists()
free=shutil.disk_usage('C:/').free;assert free-64*1024**2>=20*1024**3
r={'passed':False,'physical_access':False,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'space':{'C_free':free,'projected_allocation':64*1024**2,'reserve':20*1024**3}}
P.mkdir(parents=True)
try:
 r['sdk_commit']=subprocess.check_output(['git','-C','C:/nxdk','rev-parse','HEAD'],text=True).strip()
 assert r['sdk_commit']=='58427c078b4ccb0121f359b6b6c536b3b2914976'
 for n in ['main.c','report-path.h','Makefile']:shutil.copyfile(K/n,P/n)
 cmd=['powershell','-NoProfile','-File','C:/Homebrew/Invoke-Console.ps1','-Console','xbox','-WorkingDirectory',str(P),'-Command','make -j4'];r['command']=cmd
 with (P/'build.log').open('wb') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
 r['files']={n:{'bytes':len(b:=(P/n).read_bytes()),'sha256':hashlib.sha256(b).hexdigest()} for n in ['main.c','report-path.h','Makefile','main.exe','bin/default.xbe','build.log']}
 r['passed']=True
finally:(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
