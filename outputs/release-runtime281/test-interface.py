import argparse,hashlib,json,struct,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('attempt');a=p.parse_args();assert a.attempt.isdecimal()
dest=k/('interface-host'+a.attempt+'.json');assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/runtime281-interface'+a.attempt);out.mkdir(exist_ok=False)
old=k.parent/'texture-boundary278'
source=Path('E:/Codex-archive/xbox-windows-native/boundary278-build002/source/hw/xbox/nv2a/pgraph/gl/renderer.c').read_text()
def function(name):
 p=source.index(name+'(');start=source.rfind('static ',0,p);end=source.index('{',p)+1;depth=1
 while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[start:end]
for n in ['test-interface.py','test-interface.c','interface.c','transaction.h']:(out/n).write_bytes((k/n).read_bytes())
for n in ['release.h','admission.h']:(out/n).write_bytes((k.parent/'release-worker280'/n).read_bytes())
body=function('x278_parse')+'\n'+function('x265_rows_page')+'\n'+(k/'interface.c').read_text()
(out/'actual-test.c').write_bytes((k/'test-interface.c').read_text().replace('/* ACTUAL_FUNCTIONS */',body).encode())
base='/mnt/e/Codex-archive/xbox-windows-native/runtime281-interface'+a.attempt
r=dict(passed=False,host_only=True,guest_launched=False,old_278_modified=False,models=['allocator/GLib formatting','FIFO lock/guest/frontend state','completed worker metadata; no runtime request'])
try:
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/actual-test.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0;r['passed']=True
except BaseException as e:r['error']=repr(e)
r['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='files'},indent=2));assert r['passed']
