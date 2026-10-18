"""Run actual x86 wrapper with modeled kernel calls; trap CLI before execution."""
import datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn471/stub-host001');B=Path('/mnt/c/xwn471/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not O.exists() and not (K/'stub-host001.json').exists()
assert shutil.disk_usage('/mnt/c').free-8*1024**2>=20*1024**3
build=json.loads((K/'build001.json').read_text());assert sha(B/'stub.bin')==build['files'][str(B/'stub.bin')]['sha256']
O.mkdir();shutil.copyfile(K/'test-stub.c',O/'test-stub.c');shutil.copyfile(K/'enter-stub.S',O/'enter-stub.S')
r=dict(status='running',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_assembled_wrapper=True,kernel_file_effects='MODELED',physical_access=False,privileged_loader_executed=False,SMBus_TSC_CLI='MODELED',inputs={str(p):sha(p) for p in [K/'stub-host001.py',O/'test-stub.c',O/'enter-stub.S',B/'stub.bin',Path('/usr/bin/x86_64-linux-gnu-gcc-12')]})
def save():(K/'stub-host001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 cmds=[['/usr/bin/x86_64-linux-gnu-gcc-12','-m32','-O0','-Wall','-Wextra','-Werror','-fno-pie','-no-pie','test-stub.c','enter-stub.S','-o','test-stub'],['./test-stub',str(B/'stub.bin')]]
 with (O/'host.log').open('w') as log:
  for cmd in cmds:subprocess.run(cmd,cwd=O,stdout=log,stderr=log,check=True,timeout=45)
 assert 'PASS 45 actual post-stack stub cases' in (O/'host.log').read_text()
 r.update(status='passed',cases=45,commands=cmds)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
 r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
