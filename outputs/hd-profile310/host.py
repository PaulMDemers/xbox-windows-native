import hashlib,json,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;out=Path('D:/xwn310/host001');assert not out.exists() and not (k/'host001.json').exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
assert shutil.disk_usage('D:/').free-64*1024**2>=20*1024**3
out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['profile.c','profile.h','host.c','host.py','Host.ps1','profile-facts.json','DESIGN.md']:shutil.copyfile(k/n,out/n)
r=dict(passed=False,hardware_io=False,source={p.name:sha(p) for p in out.iterdir()})
try:
 compiler=subprocess.check_output(['wsl','-d','Ubuntu','--','gcc','--version'],timeout=20).decode();r['compiler']=compiler
 command=['wsl','-d','Ubuntu','--','gcc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','/mnt/d/xwn310/host001/profile.c','/mnt/d/xwn310/host001/host.c','-o','/mnt/d/xwn310/host001/host']
 x=subprocess.run(command,capture_output=True,timeout=60);r['command']=command;(out/'compile.log').write_bytes(x.stdout+x.stderr);assert x.returncode==0,(x.stdout+x.stderr).decode()
 x=subprocess.run(['wsl','-d','Ubuntu','--','env','ASAN_OPTIONS=detect_leaks=1','/mnt/d/xwn310/host001/host'],capture_output=True,timeout=60);(out/'result.txt').write_bytes(x.stdout);(out/'stderr.txt').write_bytes(x.stderr);assert x.returncode==0 and not x.stderr,x.stderr.decode()
 r.update(passed=True,checks=int(x.stdout.decode().splitlines()[-1].split()[1]),profile_output_sha256=sha(out/'result.txt'),binary_sha256=sha(out/'host'))
except Exception as e:r['failure']=repr(e)
finally:
 r['private_files']={str(p):sha(p) for p in out.iterdir()};(k/'host001.json').write_text(json.dumps(r,indent=2)+'\n')
print({key:r.get(key) for key in ['passed','checks','failure']});assert r['passed']
