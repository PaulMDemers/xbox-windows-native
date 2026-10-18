"""Compile and run the actual assembly with modeled privileged I/O and TSC."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent
O=Path('/mnt/c/xwn470/host001')
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not O.exists() and not (K/'host001.json').exists()
assert shutil.disk_usage('/mnt/c').free-16*1024**2 >=20*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cc=Path('/usr/bin/x86_64-linux-gnu-gcc-12')
assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
O.mkdir(parents=True)
for n in ['marker.S','invoke.S','test.c']:shutil.copyfile(K/n,O/n)
r=dict(status='running',physical_access=False,actual_assembled_code=True,port_IO_CLI_TSC='MODELED by SIGSEGV emulation',compiler_sha256=sha(cc),source={str(K/n):sha(K/n) for n in ['marker.S','invoke.S','test.c','host001.py']})
def save():(K/'host001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    cmds=[[str(cc),'-m32','-g','-O0','-Wall','-Wextra','-Werror','-fno-pie','-no-pie','test.c','marker.S','invoke.S','-o','test'],['./test']]
    with (O/'host.log').open('w') as log:
        for cmd in cmds:subprocess.run(cmd,cwd=O,stdout=log,stderr=log,check=True,timeout=45)
    assert 'PASS 51 actual x86 marker cases' in (O/'host.log').read_text()
    (O/'disassembly.txt').write_bytes(subprocess.check_output(['objdump','-d','-Mintel',str(O/'test')]))
    r.update(status='passed',actual_cases=51,immutable_repeat_cases=51,commands=cmds)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
    r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
