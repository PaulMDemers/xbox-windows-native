import json,subprocess,sys
from pathlib import Path
W=Path(__file__).resolve().parents[2];K=W/'outputs/release-readiness403';base=Path('/home/paul/xbox-windows-native');deps=base/'release-readiness403-dependencies001';boot=base/'release-readiness403-bootstrap001'
results=[]
for name in ['hal','network','fatx','framebuffer','loader','display','audio','launcher']:
 out=base/('release-readiness403-'+name+'001')
 command=['python3','-B',str(W/'tools/xwn.py'),'build','--profile',name,'--output',str(out)]
 if name=='launcher':command+=['--cache',str(deps/'cromwell'),'--gcc12','/usr/bin/gcc-12']
 else:command+=['--cache',str(deps/'reactos'),'--rosbe',str(boot/'RosBE-2.2.1'),'--toolchain-receipt',str(boot/'toolchain.json')]
 print('START',name,flush=True)
 with (K/('build-'+name+'001-console.txt')).open('x') as log:
  p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1600)
 results.append({'profile':name,'exit_code':p.returncode,'output':str(out)})
 (K/'build-batch001.json').write_text(json.dumps(results,indent=2)+'\n')
 print('FINISH',name,p.returncode,flush=True)
 if p.returncode:break
assert all(r['exit_code']==0 for r in results) and len(results)==8
