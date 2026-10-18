"""Unique diskless adapter fixture; build and run under separate owned leases."""
import datetime,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn490/host001');P=Path('/mnt/c/xwn487/build001')
R=Path('/home/paul/xbox-windows-native/toolchains/qemu-pc/root');Q=R/'usr/bin/qemu-system-i386'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(name,r):(K/name).write_text(json.dumps(r,indent=2)+'\n')
assert sys.argv[1] in ('build','run')
if sys.argv[1]=='build':
 assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not (K/'host-build001.json').exists()
 assert shutil.disk_usage('/mnt/c').free-64*1024**2>=20*1024**3
 parent=json.loads((K.parent/'cpu-context489/build001.json').read_text())
 inputs={p:h for p,h in parent['inputs'].items() if not p.startswith('/mnt/c/')}
 for p in [Path('/usr/bin/x86_64-linux-gnu-gcc-12'),P/'xbeboot.S',P/'witness.S',P/'default.xbe',K.parent/'cpu-context489/capture.S',K.parent/'cpu-context489/decode.py',K/'host001.py',K/'fixture.S',K/'fixture.c',K/'context.S',K/'decode.py',K/'review001.py',K.parent/'paging-handoff488/link.ld']:inputs[str(p)]=sha(p)
 assert sha(P/'default.xbe')=='851a916de6454a8e100b98657d2f52625fedb1d12eb3e91d8dad932a3eab74ec'
 assert sha(P/'xbeboot.S')=='bf1737899cc4ff783b26c0bef3c5b6aa622f5160697bf8f27f27adf4030a7e70'
 assert all(sha(Path(p))==h for p,h in inputs.items())
 O.mkdir(parents=True);r=dict(passed=False,physical_access=False,inputs=inputs,started=utc(),commands=[],kernel_IO='MODELED',privileged_capture='actual instructions in synthetic CPU context',refusal_cleanup='modeled endpoint, not original cleanup')
 try:
  for n in ['fixture.S','fixture.c','context.S','host001.py','decode.py','review001.py']:shutil.copyfile(K/n,O/n)
  shutil.copyfile(K.parent/'cpu-context489/capture.S',O/'capture.S');shutil.copyfile(K.parent/'cpu-context489/decode.py',O/'capture_decode.py')
  shutil.copyfile(K.parent/'paging-handoff488/link.ld',O/'link.ld')
  w=(P/'witness.S').read_text().replace('487','490')
  a='witness_entry:\n';b='witness_entry:\n    call context490_pre\n'
  c='    // No kernel or SMBus calls after these final comparisons.'
  d='    call context490_post\n'+c
  assert w.count(a)==w.count(c)==1
  w=w.replace(a,b).replace(c,d)
  assert w.replace(b,a).replace(d,c).replace('490','487')==(P/'witness.S').read_text()
  (O/'witness.S').write_text(w)
  s=(P/'xbeboot.S').read_text()
  helpers=s[s.index('diag_compare_loader:'):s.index('// SPDX-License-Identifier: GPL-2.0-or-later\n// All file calls')]+s[s.index('diag_reset_iosb:'):s.index('diag_close_refuse:')]
  (O/'helpers.S').write_text(helpers)
  sym=json.loads((K.parent/'blend-precision487/build001.json').read_text())['wrapper_symbols'];old=(P/'default.xbe').read_bytes();off=sym['blentry']-0x10000
  loader=old[off:off+1024];assert hashlib.sha256(loader).hexdigest()=='c039a983e17220bd6150e888e7a8c791134c03dbaca555d236158b41694ace2e';(O/'loader.bin').write_bytes(loader)
  cmds=[['as','--32','fixture.S','-o','fixture.o'],['/usr/bin/x86_64-linux-gnu-gcc-12','-m32','-O1','-Wall','-Wextra','-Werror','-ffreestanding','-fno-pie','-fno-stack-protector','-fno-asynchronous-unwind-tables','-c','fixture.c','-o','fixture-c.o'],['ld','-m','elf_i386','-T','link.ld','fixture.o','fixture-c.o','-o','fixture.elf']]
  for cmd in cmds:
   r['commands'].append(cmd)
   with (O/'build.log').open('ab') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
  nm=subprocess.check_output(['nm','-n',str(O/'fixture.elf')],text=True);(O/'symbols.txt').write_text(nm)
  r['symbols']={v[2]:int(v[0],16) for l in nm.splitlines() if len(v:=l.split())==3}
  (O/'disassembly.txt').write_bytes(subprocess.check_output(['objdump','-d','-Mintel',str(O/'fixture.elf')]))
  subprocess.run(['objcopy','-O','binary','fixture.elf','fixture.bin'],cwd=O,check=True,timeout=30)
  raw=(O/'fixture.bin').read_bytes();lo=r['symbols']['capture_begin']-0x100000;hi=r['symbols']['capture_end']-0x100000
  assert hi-lo==313 and hashlib.sha256(raw[lo:hi]).hexdigest()=='d5bed1052a1eeab8810e15f05734b2c9795d56641bf1ddb50e1a2618a808b196'
  r.update(passed=True,capture_bytes=313,capture_byte_identical489=True,original_witness_reconstructed=True,original_compare_reset_flush_helpers=True)
 except BaseException as e:r['error']=repr(e);raise
 finally:r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};r['finished']=utc();save('host-build001.json',r)
else:
 assert os.environ.get('XBOX_XEMU_MODE')=='exclusive' and not (K/'host-run001.json').exists()
 b=json.loads((K/'host-build001.json').read_text());assert b['passed']
 for p,h in b['inputs'].items():assert sha(Path(p))==h,p
 for p,h in b['files'].items():assert sha(Path(p))==h['sha256'],p
 assert shutil.disk_usage('/mnt/c').free-128*1024**2>=20*1024**3
 f=O/'run001';assert not f.exists();f.mkdir()
 cmd=[str(Q),'-name','xwn-context-adapter490-host001','-L',str(R/'usr/share/qemu'),'-bios',str(R/'usr/share/seabios/bios.bin'),'-machine','pc,acpi=off,hpet=off','-accel','tcg,thread=single','-cpu','pentium3','-smp','1','-m','64','-vga','none','-display','none','-nic','none','-serial','none','-monitor','none','-kernel',str(O/'fixture.elf'),'-debugcon','file:'+str(f/'capture.bin'),'-device','isa-debug-exit,iobase=0xf4,iosize=0x04','-no-reboot','-d','int,cpu_reset','-D',str(f/'cpu.log')]
 r=dict(started=utc(),closed=False,passed=False,physical_access=False,command=cmd,build_sha256=sha(K/'host-build001.json'));save('host-run001.json',r)
 env=os.environ.copy();env['LD_LIBRARY_PATH']=str(R/'usr/lib/x86_64-linux-gnu')
 with (f/'qemu.log').open('xb') as log:
  p=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT);r['pid']=p.pid;save('host-run001.json',r)
  try:r['exit_code']=p.wait(timeout=15);r['deadline']=False
  except subprocess.TimeoutExpired:
   r['deadline']=True;p.terminate()
   try:r['exit_code']=p.wait(timeout=3)
   except subprocess.TimeoutExpired:p.kill();r['exit_code']=p.wait(timeout=3);r['fallback_kill']=True
  finally:r['closed']=p.poll() is not None
 try:
  from review001 import review
  r['review']=review((f/'capture.bin').read_bytes(),b['symbols'])
  cpu=(f/'cpu.log').read_text();assert 'Triple fault' not in cpu and 'check_exception' not in cpu
  assert r['exit_code']==33 and r['closed'] and not r['deadline']
  for p,h in b['inputs'].items():assert sha(Path(p))==h
  for p,h in b['files'].items():assert sha(Path(p))==h['sha256']
  r['passed']=True
 except BaseException as e:r['error']=repr(e);raise
 finally:r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in f.iterdir() if p.is_file()};r['finished']=utc();save('host-run001.json',r)
