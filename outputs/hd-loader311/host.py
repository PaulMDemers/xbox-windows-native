import hashlib,json,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;out=Path('D:/xwn311/host002')
assert not out.exists() and not (k/'host002.json').exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
out.mkdir(parents=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['adapter.c','adapter.h','host.c','host.py','native.c']:shutil.copyfile(k/n,out/n)
for n in ['profile.c','profile.h']:shutil.copyfile(k.parent/'hd-profile310'/n,out/n)
r=dict(passed=False,hardware_io='modeled',source={p.name:sha(p) for p in out.iterdir()})
try:
 r['compiler']=subprocess.check_output(['wsl','-d','Ubuntu','--','gcc','--version'],timeout=20).decode()
 cmd=['wsl','-d','Ubuntu','--','gcc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer']+['/mnt/d/xwn311/host002/'+n for n in ['profile.c','adapter.c','host.c']]+['-o','/mnt/d/xwn311/host002/host']
 x=subprocess.run(cmd,capture_output=True,timeout=60);r['command']=cmd;(out/'compile.log').write_bytes(x.stdout+x.stderr);assert x.returncode==0,(x.stdout+x.stderr).decode()
 x=subprocess.run(['wsl','-d','Ubuntu','--','env','ASAN_OPTIONS=detect_leaks=1','/mnt/d/xwn311/host002/host'],capture_output=True,timeout=60)
 (out/'result.txt').write_bytes(x.stdout);(out/'stderr.txt').write_bytes(x.stderr)
 assert x.returncode==0 and not x.stderr,x.stderr.decode()
 r.update(passed=True,checks=int(x.stdout.decode().splitlines()[-1].split()[1]),binary_sha256=sha(out/'host'))
except Exception as e:r['failure']=repr(e)
finally:
 r['private_files']={str(p):sha(p) for p in out.iterdir()};(k/'host002.json').write_text(json.dumps(r,indent=2)+'\n')
print({a:r.get(a) for a in ['passed','checks','failure']});assert r['passed']
