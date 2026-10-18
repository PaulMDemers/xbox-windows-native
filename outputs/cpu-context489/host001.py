"""Build or run one unique diskless privileged capture test; no Xbox IO."""
import datetime,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn489/host001')
R=Path('/home/paul/xbox-windows-native/toolchains/qemu-pc/root');Q=R/'usr/bin/qemu-system-i386'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(R/'usr/lib/x86_64-linux-gnu')
def save(name,r):(K/name).write_text(json.dumps(r,indent=2)+'\n')
assert sys.argv[1] in ('build','run')
if sys.argv[1]=='build':
 assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not (K/'build001.json').exists()
 assert shutil.disk_usage('/mnt/c').free-64*1024**2>=20*1024**3
 parent=json.loads((K.parent/'paging-handoff488/build003.json').read_text())
 inputs={p:h for p,h in parent['inputs'].items() if not p.startswith('/mnt/c/')}
 assert all(sha(Path(p))==h for p,h in inputs.items())
 for p in [K/'capture.S',K/'test.S',K/'decode.py',K/'host001.py',K/'review001.py',K.parent/'paging-handoff488/link.ld']:inputs[str(p)]=sha(p)
 O.mkdir(parents=True);r=dict(passed=False,physical_access=False,inputs=inputs,started=utc(),commands=[])
 try:
  for n in ['capture.S','test.S','decode.py','host001.py','review001.py']:shutil.copyfile(K/n,O/n)
  shutil.copyfile(K.parent/'paging-handoff488/link.ld',O/'link.ld')
  for cmd in [['as','--32','test.S','-o','test.o'],['ld','-m','elf_i386','-T','link.ld','test.o','-o','test.elf']]:
   r['commands'].append(cmd)
   with (O/'build.log').open('ab') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
  (O/'disassembly.txt').write_bytes(subprocess.check_output(['objdump','-d','-Mintel',str(O/'test.elf')]))
  nm=subprocess.check_output(['nm','-n',str(O/'test.elf')],text=True);(O/'symbols.txt').write_text(nm)
  r['symbols']={v[2]:int(v[0],16) for l in nm.splitlines() if len(v:=l.split())==3}
  r['passed']=True
 except BaseException as e:r['error']=repr(e);raise
 finally:
  r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};r['finished']=utc();save('build001.json',r)
else:
 assert os.environ.get('XBOX_XEMU_MODE')=='exclusive' and not (K/'run001.json').exists()
 b=json.loads((K/'build001.json').read_text());assert b['passed']
 for p,h in b['inputs'].items():assert sha(Path(p))==h,p
 for p,h in b['files'].items():assert sha(Path(p))==h['sha256'],p
 assert shutil.disk_usage('/mnt/c').free-128*1024**2>=20*1024**3
 f=O/'run001';assert not f.exists();f.mkdir()
 cmd=[str(Q),'-name','xwn-cpu-context489-host001','-L',str(R/'usr/share/qemu'),'-bios',str(R/'usr/share/seabios/bios.bin'),'-machine','pc,acpi=off,hpet=off','-accel','tcg,thread=single','-cpu','pentium3','-smp','1','-m','64','-vga','none','-display','none','-nic','none','-serial','none','-monitor','none','-kernel',str(O/'test.elf'),'-debugcon','file:'+str(f/'capture.bin'),'-device','isa-debug-exit,iobase=0xf4,iosize=0x04','-no-reboot','-d','int,cpu_reset','-D',str(f/'cpu.log')]
 r=dict(started=utc(),closed=False,passed=False,physical_access=False,command=cmd,build_sha256=sha(K/'build001.json'));save('run001.json',r)
 with (f/'qemu.log').open('xb') as log:
  proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT);r['pid']=proc.pid;save('run001.json',r)
  try:r['exit_code']=proc.wait(timeout=15);r['deadline']=False
  except subprocess.TimeoutExpired:
   r['deadline']=True;proc.terminate()
   try:r['exit_code']=proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill();r['exit_code']=proc.wait(timeout=3);r['fallback_kill']=True
  finally:r['closed']=proc.poll() is not None
 try:
  from review001 import review
  r['review']=review((f/'capture.bin').read_bytes(),b['symbols'])
  cpu=(f/'cpu.log').read_text();assert 'Triple fault' not in cpu and 'check_exception' not in cpu
  assert r['exit_code']==33 and r['closed'] and not r['deadline']
  for p,h in b['inputs'].items():assert sha(Path(p))==h
  for p,h in b['files'].items():assert sha(Path(p))==h['sha256']
  r['passed']=True
 except BaseException as e:r['error']=repr(e);raise
 finally:r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in f.iterdir() if p.is_file()};r['finished']=utc();save('run001.json',r)
