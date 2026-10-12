"""Unique frozen ASan/UBSan test of proposed actual three-boundary worker code."""
import argparse,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('attempt');a=p.parse_args();assert a.attempt.isdecimal()
dest=k/('worker-host'+a.attempt+'.json');assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/release280-worker'+a.attempt);out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=k.parent/'texture-boundary278/adapter.c';source=old.read_text()
def function(name):
 p=source.index(name+'(');start=source.rfind('static ',0,p);end=source.index('{',p)+1;depth=1
 while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[start:end]
legacy=['x278_cpu_copy','x278_quiescent','x278_publish']
body='\n'.join(function(n) for n in legacy)+'\n'
for n in ['validate.c','retained.c','publish.c','scalar-publish.c','capture.c','worker.c']:
 s=(k/n).read_text()
 if n=='capture.c':s=s.replace('{\n    X265State *initial','{\n    active_stage=stage; /* test-only fault scope */\n    X265State *initial')
 body+=s+'\n'
inputs=['test-worker.py','test-worker.c','admission.h','release.h','boundary.h','link.h','resume.h','transaction.h','graph.c','validate.c','retained.c','publish.c','scalar-publish.c','capture.c','worker.c','proposed-release.c']
for n in inputs:(out/n).write_bytes((k/n).read_bytes())
(out/'legacy-adapter.c').write_bytes(old.read_bytes())
(out/'fixture.h').write_bytes(Path('E:/Codex-archive/xbox-windows-native/admission277-host002/fixture.h').read_bytes())
(out/'actual-test.c').write_bytes((k/'test-worker.c').read_text().replace('/* ACTUAL_FUNCTIONS */',body).encode())
base='/mnt/e/Codex-archive/xbox-windows-native/release280-worker'+a.attempt
r=dict(passed=False,host_only=True,guest_launched=False,renderer_built=False,release_installed=False,
       actual_worker_sources=['capture.c','worker.c','validate.c','retained.c','publish.c'],legacy_functions=legacy,
       models=['CPU jobs','GL fences and contexts','complete live graph collection','unbound graph authorization','counted release call and partial mask','snapshot file and GL operations'],
       test_instrumentation='Set fault-scope stage at capture entry only; no production branch removed or rewritten')
try:
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/actual-test.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test',base],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0;r['passed']=True
except BaseException as e:r['error']=repr(e)
r['files']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='files'},indent=2));assert r['passed']
