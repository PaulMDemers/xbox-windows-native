"""Compile actual header/layout assertions without executing any executable."""
import hashlib,json,os,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/home/paul/xbox-windows-native/discovery455-layout001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists() and not (K/'layout001.json').exists();P.mkdir()
b=json.loads((K/'sample-build001.json').read_text());cc=Path(b['compiler']);assert sha(cc)==b['compiler_sha256']
(P/'layout001.c').write_bytes((K/'layout001.c').read_bytes())
cmd=[str(cc),'-Wall','-Wextra','-Werror','-c','-MD','-MF',str(P/'headers.d'),str(P/'layout001.c'),'-o',str(P/'layout001.o')]
with (P/'compile.log').open('xb') as f:code=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=60).returncode
r=dict(command=cmd,exit_code=code,source_sha256=sha(P/'layout001.c'),compiler_sha256=sha(cc),log_sha256=sha(P/'compile.log'),host_executed=False,assertions=12)
if code==0:
 deps=(P/'headers.d').read_text().replace('\\\n','').split(': ',1)[1].split();r['headers']={n:sha(Path(n)) for n in sorted(set(deps)) if Path(n)!=P/'layout001.c'}
 for p,h in r['headers'].items():assert b['headers'][p]==h,p
(K/'layout001.json').write_text(json.dumps(r,indent=2)+'\n');assert code==0
print('12 actual compiled layout/capability assertions passed.')
