"""Run actual x86 wrapper with modeled kernel calls; trap CLI before execution."""
import datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn475/host002');B=Path('/mnt/c/xwn475/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not O.exists() and not (K/'host002.json').exists()
assert shutil.disk_usage('/mnt/c').free-8*1024**2>=20*1024**3
build=json.loads((K/'build001.json').read_text());assert sha(B/'default.xbe')==build['sha256']
O.mkdir();shutil.copyfile(K/'test-wrapper002.c',O/'test-wrapper.c')
r=dict(status='running',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_assembled_wrapper=True,kernel_file_effects='MODELED',physical_access=False,privileged_loader_executed=False,SMBus_TSC_CLI='MODELED',inputs={str(p):sha(p) for p in [K/'host002.py',O/'test-wrapper.c',B/'default.xbe',Path('/usr/bin/x86_64-linux-gnu-gcc-12')]})
def save():(K/'host002.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 cmds=[['/usr/bin/x86_64-linux-gnu-gcc-12','-m32','-O0','-Wall','-Wextra','-Werror','-fno-pie','-no-pie','test-wrapper.c','-o','test-wrapper'],['./test-wrapper',str(B/'default.xbe')]]
 with (O/'host.log').open('w') as log:
  for cmd in cmds:subprocess.run(cmd,cwd=O,stdout=log,stderr=log,check=True,timeout=45)
 assert 'PASS 104 actual-wrapper cases' in (O/'host.log').read_text()
 r.update(status='passed',cases=104,commands=cmds)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
 r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
