"""Build unique no-CRT NT5 probes with the reviewed 403 compiler; no SDK mutation."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent
P=Path('/mnt/e/xwn423/build001')
sys.path.insert(0,str(K.parents[1]/'tools'))
from build_space import require_space
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not P.exists() and not (K/'build001.json').exists()
space=require_space(P,20+8/1024)
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
P.mkdir(parents=True)
(P/'probe.c').write_bytes((K/'probe.c').read_bytes())
record={'space':space,'compiler':str(cc),'compiler_sha256':sha(cc),'source_sha256':sha(P/'probe.c'),'rows':[],'guest_launched':False}
for name,phase in [('create.exe',1),('reopen.exe',0)]:
 cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0',f'-DCREATE_PHASE={phase}','-o',str(P/name),str(P/'probe.c'),'-lkernel32','-luser32','-ladvapi32','-lcrypt32']
 with (P/(name+'.log')).open('xb') as f:ret=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT).returncode
 row={'name':name,'command':cmd,'exit_code':ret,'log_sha256':sha(P/(name+'.log'))};record['rows'].append(row)
 if not ret:row.update(path=str(P/name),sha256=sha(P/name),bytes=(P/name).stat().st_size)
 (K/'build001.json').write_text(json.dumps(record,indent=2)+'\n')
 assert not ret,(P/(name+'.log')).read_text()
print('Two bounded-state NT5 probe binaries built; runtime still untested.')
