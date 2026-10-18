"""Compile actual application main/engine under ASan/UBSan with modeled SDK APIs."""
import hashlib,json,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('C:/xwn528/ui-host001')
assert not O.exists() and not (K/'ui-host001.json').exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
O.mkdir(parents=True)
names=['main.c','engine.c','engine.h','host-sdk.h','ui-host.c']
for n in names:shutil.copyfile(K/n,O/n)
r=dict(passed=False,actual_main_and_engine=True,SDK_services='MODELED',physical_access=False,
       source_sha256={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in names})
def run(args,log):
 p=subprocess.run(['wsl','-d','Ubuntu','--']+args,capture_output=True,timeout=60)
 (O/log).write_bytes(p.stdout+p.stderr);assert p.returncode==0,(p.stdout+p.stderr).decode(errors='replace')
 return p.stdout.decode()
try:
 flags=['-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
 root='/mnt/c/xwn528/ui-host001/'
 run(['cc']+flags+['-DXWN_HOST_TEST','-Dmain=guest_main','-c',root+'main.c','-o',root+'main.o'],'main-compile.txt')
 run(['cc']+flags+[root+'main.o',root+'engine.c',root+'ui-host.c','-o',root+'ui-host'],'link.txt')
 r['run']=run([root+'ui-host',root+'transcript.txt'],'run.txt');r.update(passed=True,scenarios=30)
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['private_files']={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in O.rglob('*') if p.is_file()}
 (K/'ui-host001.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(r['run'])
