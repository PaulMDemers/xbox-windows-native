"""Compile shared admission and retained original pure controls before NT5."""
import hashlib,json,os,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn610/host001')
out=K/'host-tests001.json';assert not out.exists() and not O.exists()
assert os.environ.get('XWN_BUILD_LEASE')=='held'
O.mkdir(parents=True);r=dict(passed=False,physical_access=False,rows=[])
try:
 for name in ['calls','dib','phase','lifetime']:
  p=K/('host_'+name+'.c');exe=O/name
  cmd=['gcc','-std=c99','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-g',str(p),'-o',str(exe)]
  build=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
  r['rows'].append(dict(command=cmd,build_exit=build.returncode,build_stdout=build.stdout,build_stderr=build.stderr))
  assert build.returncode==0,build.stderr
  run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
  r['rows'][-1].update(exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr)
  assert run.returncode==0,run.stderr
 r['passed']=True
finally:
 r['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in list(K.glob('host_*.c'))+[K/'lifetime.h',K/'calls.h',K/'phase.h',K/'dib_header.h']}
 out.write_text(json.dumps(r,indent=2)+'\n')
print('610 shared-policy and retained host controls passed')
