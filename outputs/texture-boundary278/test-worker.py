"""Extract actual adapter functions. No guest/runtime claims from models."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'worker-host001.json';assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/boundary278-worker001');out.mkdir(exist_ok=False)
source=(k/'adapter.c').read_text()
def function(name):
 p=source.index(name+'(');a=source.rfind('static ',0,p);b=source.index('{',p)+1;n=1
 while n:n+=(source[b]=='{')-(source[b]=='}');b+=1
 return source[a:b]
names=['x278_cpu_copy','x278_quiescent','x278_validate','x278_publish','x278_worker']
body='\n'.join(function(n) for n in names)
# Test-only wrapper counts entry; actual validation body is otherwise exact.
body=body.replace('static bool x278_validate(NV2AState *d,X265State *s)\n{','static bool x278_validate(NV2AState *d,X265State *s)\n{\n    validate_calls++;')
for n in ['test-worker.py','test-worker.c','admission.h','adapter.c','clock.c','patch-renderer.py']:(out/n).write_bytes((k/n).read_bytes())
(out/'fixture.h').write_bytes(Path('E:/Codex-archive/xbox-windows-native/admission277-host002/fixture.h').read_bytes())
(out/'actual-test.c').write_text((k/'test-worker.c').read_text().replace('/* ACTUAL_FUNCTIONS */',body))
base='/mnt/e/Codex-archive/xbox-windows-native/boundary278-worker001'
r=dict(passed=False,guest_launched=False,actual_functions=names,models=['CPU job scheduling','GL fences/context calls','live graph collection'],actual_admission_core=True)
try:
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/actual-test.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test',base+'/rows.bin'],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0;r['passed']=True
except BaseException as e:r['error']=repr(e)
r['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='files'},indent=2));assert r['passed']
