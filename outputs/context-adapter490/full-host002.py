"""Actual assembled full wrapper with explicit modeled CPU/kernel/IO hooks."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn490/full002');B=Path('/mnt/c/xwn490/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not (K/'full-host002.json').exists()
assert shutil.disk_usage('/mnt/c').free-64*1024**2>=20*1024**3
b=json.loads((K/'build001.json').read_text());assert sha(B/'default.xbe')==b['sha256']
assert json.loads((K/'validation001.json').read_text())['passed']
O.mkdir();s=b['wrapper_symbols']
(O/'symbols.h').write_text(''.join('#define '+n+' '+str(s[v])+'u\n' for n,v in [('MARKER_ADDRESS','before_marker_record'),('CAPTURE_ADDRESS','capture490_begin'),('FIRST_ADDRESS','context490_first'),('SECOND_ADDRESS','context490_second'),('CLAIM_ADDRESS','context490_claim')]))
shutil.copyfile(K/'full-wrapper002.c',O/'test-wrapper.c')
r=dict(status='running',physical_access=False,cpu_kernel_IO_SMBus_TSC='MODELED',capture_entry='explicit debugger breakpoint substitution; original XBE file unchanged',privileged_capture_actual='separate host-run001.json',inputs={str(p):sha(p) for p in [K/'full-host002.py',K/'full-wrapper002.c',K/'full-source002.json',K/'validation001.json',B/'default.xbe',Path('/usr/bin/x86_64-linux-gnu-gcc-12')]})
def save():(K/'full-host002.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 cmds=[['/usr/bin/x86_64-linux-gnu-gcc-12','-m32','-O0','-Wall','-Wextra','-Werror','-fno-pie','-no-pie','test-wrapper.c','-o','test-wrapper'],['./test-wrapper',str(B/'default.xbe')]]
 with (O/'host.log').open('w') as f:
  for cmd in cmds:subprocess.run(cmd,cwd=O,stdout=f,stderr=f,check=True,timeout=60)
 assert 'PASS 154 actual-wrapper cases' in (O/'host.log').read_text()
 assert sha(B/'default.xbe')==b['sha256']
 r.update(status='passed',cases=154,commands=cmds)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
