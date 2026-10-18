"""One-shot diskless privileged CPU fixture. Never accesses the physical Xbox."""
import datetime,hashlib,json,os,re,shutil,subprocess,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent
O=Path('/mnt/c/xwn488/lab002')
R=Path('/home/paul/xbox-windows-native/toolchains/qemu-pc/root')
Q=R/'usr/bin/qemu-system-i386'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(R/'usr/lib/x86_64-linux-gnu')
names=['dual_copy','identity_copy','missing_pte','post_pg_ud2','low_entry_ud2','bad_far_target','bad_payload','df_set','wrong_source','short_copy']
def save(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
def cmd(argv,cwd=O):
 with (O/'build.log').open('ab') as f:subprocess.run(argv,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
assert sys.argv[1] in ('build','run')
if sys.argv[1]=='build':
 assert os.environ.get('XWN_BUILD_LEASE')=='held'
 assert not O.exists() and not (K/'build002.json').exists()
 assert shutil.disk_usage('/mnt/c').free-64*1024**2>=20*1024**3
 b=Path('/mnt/c/xwn487/build001/default.xbe');a=Path('/mnt/c/xwn483/build001/default.xbe')
 assert sha(b)=='851a916de6454a8e100b98657d2f52625fedb1d12eb3e91d8dad932a3eab74ec'
 assert sha(a)=='763b9516be6ea3c5c17aaf356a9743ea94385c77b2a1d32598359a009f65438e'
 review=K.parent/'blend-precision487/build001.json'
 sy=json.loads(review.read_text())['wrapper_symbols'];entry=sy['blentry'];off=entry-0x10000
 loader=b.read_bytes()[off:off+1024]
 assert len(loader)==1024 and loader==a.read_bytes()[off:off+1024]
 assert loader[:12]==bytes.fromhex('fa0f20c025ffffff7f0f22c0')
 assert loader[sy['newloc']-entry:sy['newloc']-entry+10]==bytes.fromhex('bf00006002b900001000')
 O.mkdir(parents=True)
 r=dict(started=utc(),completed=False,passed=False,physical_access=False,scope='synthetic diskless QEMU CPU fixture; no Xbox kernel, devices or Windows',files={},cases=names)
 try:
  pins=[b,a,review,*[K/n for n in ['boot002.S','payload.S','link.ld','lab002.py']],Path('/usr/bin/as'),Path('/usr/bin/ld'),Path('/usr/bin/objcopy'),Path('/usr/bin/objdump'),Q,R/'usr/share/seabios/bios.bin',R/'usr/share/qemu/multiboot.bin']
  # Resolve and pin actual dynamic dependencies of the executable on this host.
  for tool in [Q,Path('/usr/bin/as'),Path('/usr/bin/ld'),Path('/usr/bin/objcopy')]:
   listing=subprocess.check_output(['ldd',str(tool)],env=env,text=True)
   pins.extend(Path(x) for x in re.findall(r'(?:=>\s+|^\s*)(/[^\s]+)',listing,re.M))
  pins=list(dict.fromkeys(pins))
  r['inputs']={str(p):sha(p) for p in pins}
  for n in ['boot002.S','payload.S','link.ld','lab002.py']:shutil.copyfile(K/n,O/('boot.S' if n=='boot002.S' else n))
  (O/'loader.bin').write_bytes(loader)
  r['loader']=dict(sha256=sha(O/'loader.bin'),bytes=1024,entry=entry,source_offset=off,both_actual_wrappers_identical=True)
  r['symbols']={n:sy[n] for n in ['blentry','newloc','ptr_newloc','bootloader_gdt','gdt_48','idt_48']}
  defs=['--defsym',f'GDT_OFFSET={sy["bootloader_gdt"]-entry}']
  cmd(['as','--32',*defs,'payload.S','-o','payload.o'])
  cmd(['ld','-m','elf_i386','-Ttext','0x2600000','-e','_start','payload.o','-o','payload.elf'])
  cmd(['objcopy','-O','binary','payload.elf','payload.bin'])
  values=dict(ORIGINAL_ENTRY=entry,FAR_OFFSET=sy['ptr_newloc']-entry,NEW_OFFSET=sy['newloc']-entry,POST_PG_OFFSET=12)
  for i,n in enumerate(names):
   d=[v for k,vv in dict(values,CASE=i).items() for v in ['--defsym',f'{k}={vv}']]
   cmd(['as','--32',*d,'boot.S','-o',n+'.o'])
   cmd(['ld','-m','elf_i386','-T','link.ld',n+'.o','-o',n+'.elf'])
   (O/(n+'-disassembly.txt')).write_bytes(subprocess.check_output(['objdump','-d','-Mintel',n+'.elf'],cwd=O))
  assert all(sha(Path(p))==h for p,h in r['inputs'].items())
  r.update(completed=True,passed=True)
 except BaseException as e:r['error']=repr(e);raise
 finally:
  r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};r['finished']=utc();save(K/'build002.json',r)
else:
 assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
 out=K/'run002.json';assert not out.exists()
 b=json.loads((K/'build002.json').read_text());assert b['passed']
 assert all(sha(Path(p))==h for p,h in b['inputs'].items())
 assert all(sha(Path(p))==h['sha256'] for p,h in b['files'].items())
 assert shutil.disk_usage('/mnt/c').free-128*1024**2>=20*1024**3
 r=dict(started=utc(),closed=False,passed=False,physical_access=False,cases=[],build_sha256=sha(K/'build002.json'))
 save(out,r)
 try:
  for i,n in enumerate(names):
   f=O/('run-'+n);assert not f.exists();f.mkdir()
   argv=[str(Q),'-name','xwn488-'+n,'-L',str(R/'usr/share/qemu'),'-bios',str(R/'usr/share/seabios/bios.bin'),'-machine','pc,acpi=off,hpet=off','-accel','tcg,thread=single','-cpu','pentium3','-smp','1','-m','64','-vga','none','-display','none','-nic','none','-serial','none','-monitor','none','-kernel',str(O/(n+'.elf')),'-debugcon','file:'+str(f/'debug.bin'),'-device','isa-debug-exit,iobase=0xf4,iosize=0x04','-no-reboot','-d','int,cpu_reset','-D',str(f/'cpu.log')]
   case=dict(name=n,command=argv,started=utc(),closed=False,expected='BEP/exit33' if i<2 else 'BEF/exit35' if i==9 else 'B/architectural fault')
   r['cases'].append(case);save(out,r)
   with (f/'qemu.log').open('xb') as log:
    proc=subprocess.Popen(argv,env=env,stdout=log,stderr=subprocess.STDOUT);case['pid']=proc.pid;save(out,r)
    try:code=proc.wait(timeout=12);case['deadline']=False
    except subprocess.TimeoutExpired:
     case['deadline']=True;proc.terminate()
     try:code=proc.wait(timeout=3)
     except subprocess.TimeoutExpired:proc.kill();code=proc.wait(timeout=3);case['fallback_kill']=True
    finally:case['closed']=proc.poll() is not None
   data=(f/'debug.bin').read_bytes();cpu=(f/'cpu.log').read_text()
   case.update(exit_code=code,debug_hex=data.hex(),triple_fault='Triple fault' in cpu,finished=utc())
   case['passed']=(not case['deadline'] and ((data==b'BEP' and code==33) if i<2 else (data==b'BEF' and code==35) if i==9 else (data==b'B' and code==0 and case['triple_fault'])))
   case['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in f.iterdir() if p.is_file()};save(out,r)
   assert case['passed'],n
  assert all(sha(Path(p))==h for p,h in b['inputs'].items())
  assert all(sha(Path(p))==h['sha256'] for p,h in b['files'].items())
  r['passed']=True
 except BaseException as e:r['error']=repr(e);raise
 finally:r['closed']=all(c['closed'] for c in r['cases']);r['finished']=utc();save(out,r)
