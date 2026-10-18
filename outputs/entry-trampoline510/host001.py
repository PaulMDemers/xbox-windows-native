"""Build and execute exact-address i386 trampoline checks, not an Xbox runtime."""
import datetime,hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn510/host001');out=K/'host001.json'
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not out.exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
O.mkdir(parents=True);names=['trampoline.S','host.S','host.c','host001.py']
tools=[Path('/usr/bin')/n for n in ['x86_64-linux-gnu-gcc-12','as','ld','objcopy','objdump']]
r=dict(started_utc=utc(),passed=False,closed=False,source_pins={n:sha(K/n) for n in names},tool_pins={str(p):sha(p) for p in tools},commands=[],physical_access=False,new_XBE=False)
def save():out.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def run(cmd):
 r['commands'].append(cmd);save()
 with (O/'build.log').open('ab') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
try:
 for n in names:shutil.copyfile(K/n,O/n)
 run(['as','--32','trampoline.S','-o','trampoline.o'])
 run(['ld','-m','elf_i386','-Ttext','0x11100','-e','entry510_trampoline','trampoline.o','-o','trampoline.elf'])
 run(['objcopy','-O','binary','trampoline.elf','trampoline.bin'])
 b=(O/'trampoline.bin').read_bytes();assert b==b'\xe9'+struct.pack('<i',0x94aff-0x11105)
 (O/'trampoline-disassembly.txt').write_bytes(subprocess.check_output(['objdump','-d','-Mintel','trampoline.elf'],cwd=O))
 run(['x86_64-linux-gnu-gcc-12','-m32','-O2','-g','-fno-pie','-no-pie','-fno-stack-protector','-Wall','-Wextra','-Werror','host.c','host.S','-o','host'])
 p=subprocess.run([str(O/'host'),str(O/'trampoline.bin')],cwd=O,capture_output=True,timeout=10)
 (O/'stdout.txt').write_bytes(p.stdout);(O/'stderr.txt').write_bytes(p.stderr);r['exit_code']=p.returncode
 assert p.returncode==0;presult=json.loads(p.stdout);assert presult['passed'] and presult['actual_jump_cases']==4096 and presult['executed_negative_controls']==2
 r.update(passed=True,result=presult,stub_hex=b.hex(),rel32=struct.unpack_from('<i',b,1)[0],scope='actual Linux i386 five-byte jump at11100 to94aff; captures GPR/EFLAGS/ESP; not Xbox kernel/privileged state/boot proof')
 assert all(sha(K/n)==h for n,h in r['source_pins'].items())
except BaseException as e:r['error']=repr(e);raise
finally:
 r.update(closed=True,finished_utc=utc(),files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()});save()
 print(json.dumps({k:r[k] for k in ['passed','closed']}))
