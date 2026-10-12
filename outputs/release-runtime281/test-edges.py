import argparse,hashlib,json,struct,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('attempt');a=p.parse_args();assert a.attempt.isdecimal()
dest=k/('edges-host'+a.attempt+'.json');assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/runtime281-edges'+a.attempt);out.mkdir(exist_ok=False)
old=k.parent/'texture-boundary278';sys.path.insert(0,str(old));import proof
src=old/'emu001';t=json.loads((src/'trace.json').read_text());assert json.loads((src/'host-closure.json').read_text())['closed']
g=proof.load_pages(src,t,'initial',1,180000);u=proof.load_pages(src,t,'ui',1,8192)
proof.validate_graph(g,1,t['checkpoints'][0]['state_header'][10:14])
names=[r[3] for r in sorted((r for r in g if r[0]==67),key=lambda r:r[1])]
data=struct.pack('<6Q',len(g),len(u),*names)+b''.join(struct.pack('<8Q',*r) for r in g+u)
(out/'graphs.bin').write_bytes(data)
for n in ['test-edges.py','test-edges.c','edges.h','ui-provider.c','unbound.c']:(out/n).write_bytes((k/n).read_bytes())
for n in ['admission.h','release.h']:(out/n).write_bytes((k.parent/'release-worker280'/n).read_bytes())
(out/'fixture.h').write_bytes(Path('E:/Codex-archive/xbox-windows-native/admission277-host002/fixture.h').read_bytes())
base='/mnt/e/Codex-archive/xbox-windows-native/runtime281-edges'+a.attempt
r=dict(passed=False,host_only=True,guest_launched=False,old_278_modified=False,models=['UI acquire/state globals','current live texture/worker/lock-path state over captured278 context rows; old guest not requalified'])
try:
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/test-edges.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test',base+'/graphs.bin'],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0;r['passed']=True
except BaseException as e:r['error']=repr(e)
r['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='files'},indent=2));assert r['passed']
