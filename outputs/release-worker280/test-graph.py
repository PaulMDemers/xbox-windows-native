import argparse,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('attempt');a=p.parse_args();assert a.attempt.isdecimal()
dest=k/('graph-host'+a.attempt+'.json');assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/release280-graph'+a.attempt);out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['test-graph.py','test-graph.c','admission.h','graph.c']:(out/n).write_bytes((k/n).read_bytes())
for n in ['fixture.h','queue.h']:(out/n).write_bytes((Path('E:/Codex-archive/xbox-windows-native/admission277-host002')/n).read_bytes())
(out/'actual-test.c').write_bytes((k/'test-graph.c').read_text().replace('/* ACTUAL_FUNCTIONS */',(k/'graph.c').read_text()).encode())
base='/mnt/e/Codex-archive/xbox-windows-native/release280-graph'+a.attempt
r=dict(passed=False,host_only=True,renderer_built=False,guest_launched=False,actual_function='x280_graph',models=['live QEMU surface/cache objects','GL names'])
try:
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/actual-test.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0;r['passed']=True
except BaseException as e:r['error']=repr(e)
r['files']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='files'},indent=2));assert r['passed']
