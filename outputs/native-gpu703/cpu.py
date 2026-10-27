"""Fresh diskless QEMU CPU fixtures executing the exact linked nxdk page.
No Xbox kernel, DMA, NV2A, physical cache behavior or Windows is modeled.
"""
import datetime,hashlib,json,os,re,socket,struct,subprocess,sys,time
from oracle import expected_framebuffer
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('/mnt/c/xwn703/cpu001')
R=Path('/home/paul/xbox-windows-native/toolchains/qemu-pc/root');Q=R/'usr/bin/qemu-system-i386'
env=dict(os.environ,LD_LIBRARY_PATH=str(R/'usr/lib/x86_64-linux-gnu'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
save=lambda p,r:p.write_text(json.dumps(r,indent=2)+'\n')
names=['dual','identity','relocated','bad_magic','bad_base','fb_overlap','fb_extent','missing_pte','post_pg_ud2','bad_gdt']
assert sys.argv[1] in ('build','run')
sys.path.insert(0,str(W/'tools'));from build_space import require_space
if sys.argv[1]=='build':
 assert os.environ.get('XWN_BUILD_LEASE')=='held'
 assert not O.exists() and not (K/'cpu-build001.json').exists()
 space=require_space(O,20.15);O.mkdir(parents=True)
 r={'passed':False,'space':space,'scope':__doc__,'commands':[],'cases':[]}
 try:
  x=json.loads((K/'extract001.json').read_text());assert x['passed'];r['extract']=x
  blob=Path('/mnt/c/xwn703/build001/stub.bin');assert sha(blob)==x['template_sha256']
  cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
  pins=[cc,Path('/usr/bin/as'),Path('/usr/bin/ld'),Path('/usr/bin/nm'),Q,R/'usr/share/seabios/bios.bin',R/'usr/share/qemu/multiboot.bin',blob,*[K/n for n in ['page.c','page.h','page_tool.c','fixture002.S','link.ld','cpu.py','oracle.py']]]
  for tool in [Q,cc,Path('/usr/bin/as'),Path('/usr/bin/ld')]:
   listing=subprocess.check_output(['ldd',str(tool)],env=env,text=True)
   pins.extend(Path(p) for p in re.findall(r'(?:=>\s+|^\s*)(/[^\s]+)',listing,re.M))
  r['inputs']={str(p):sha(p) for p in dict.fromkeys(pins)}
  def run(args,cwd=O):
   r['commands'].append([str(a) for a in args]);save(K/'cpu-build001.json',r)
   with (O/'build.log').open('ab') as log:subprocess.run(args,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,timeout=60,check=True)
  run([str(cc),'-std=c11','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(K/'page.c'),str(K/'page_tool.c'),'-o',str(O/'page-tool')])
  for i,n in enumerate(names):
   d=O/n;d.mkdir();base=0x1edc000 if i==2 else 0x1eff000;alias=base if i==1 else 0x2200000
   offsets=x['offsets'];run([str(O/'page-tool'),str(blob),str(d/'page.bin'),str(offsets['code_end']),str(offsets['flat']),str(offsets['fault']),str(base),str(0x3000000),n])
   defs=[v for key,val in {'CASE':i,'TARGET':base,'ALIAS':alias,'POST_OFFSET':offsets['post']}.items() for v in ['--defsym',str(key)+'='+str(val)]]
   run(['as','--32',*defs,str(K/'fixture002.S'),'-o','fixture.o'],d)
   run(['ld','-m','elf_i386','-T',str(K/'link.ld'),'fixture.o','-o','fixture.elf'],d)
   nm=subprocess.check_output(['nm','-n',str(d/'fixture.elf')],text=True)
   sy={v[2]:int(v[0],16) for line in nm.splitlines() if len(v:=line.split())==3}
   r['cases'].append({'name':n,'index':i,'target':base,'alias':alias,'fixture_fault_loop':sy['fixture_fault_loop']})
  r['passed']=True
 except BaseException as e:r['failure']=repr(e);raise
 finally:
  r['files']={str(p):sha(p) for p in O.rglob('*') if p.is_file()};r['ended_utc']=utc();save(K/'cpu-build001.json',r)
 print('CPU fixture build passed')
else:
 assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
 b=json.loads((K/'cpu-build001.json').read_text());assert b['passed']
 assert all(sha(Path(p))==v for p,v in b['inputs'].items())
 assert all(sha(Path(p))==v for p,v in b['files'].items())
 out=K/'cpu-run001.json';assert not out.exists()
 r={'passed':False,'closed':False,'space':require_space(O,20.15),'scope':__doc__,'cases':[]};save(out,r)
 try:
  for spec in b['cases']:
   d=O/('run-'+spec['name']);d.mkdir();sockpath=Path('/tmp/xwn703-cpu001-'+spec['name']+'.sock');assert not sockpath.exists()
   cmd=[str(Q),'-name','xwn703-'+spec['name'],'-L',str(R/'usr/share/qemu'),'-bios',str(R/'usr/share/seabios/bios.bin'),'-machine','pc,acpi=off,hpet=off','-accel','tcg,thread=single','-cpu','pentium3','-smp','1','-m','64','-vga','none','-display','none','-nic','none','-serial','none','-monitor','none','-qmp','unix:'+str(sockpath)+',server=on,wait=off','-S','-kernel',str(O/spec['name']/'fixture.elf'),'-debugcon','file:'+str(d/'debug.bin'),'-no-reboot','-d','int,cpu_reset','-D',str(d/'cpu.log')]
   c=dict(spec,command=cmd,started=utc(),closed=False,passed=False);r['cases'].append(c);save(out,r)
   with (d/'qemu.log').open('xb') as log:
    proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT);c['pid']=proc.pid;save(out,r)
    sock=None
    try:
     for _ in range(100):
      if sockpath.exists():break
      assert proc.poll() is None,'QEMU exited before QMP';time.sleep(.05)
     sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);sock.settimeout(3);sock.connect(str(sockpath));stream=sock.makefile('rb')
     assert 'QMP' in json.loads(stream.readline())
     def qmp(name,args=None):
      data={'execute':name}
      if args is not None:data['arguments']=args
      sock.sendall((json.dumps(data)+'\n').encode())
      while True:
       line=stream.readline();assert line,'QMP disconnected';v=json.loads(line)
       if 'return' in v:return v['return']
       if 'error' in v:raise RuntimeError(v)
     qmp('qmp_capabilities');qmp('cont')
     offset=b['extract']['offsets'];terminal=[spec['target']+offset['hold'],spec['target']+offset['fault'],spec['fixture_fault_loop']]
     regs=''
     for _ in range(60):
      time.sleep(.05);regs=qmp('human-monitor-command',{'command-line':'info registers'})
      match=re.search(r'EIP=([0-9a-fA-F]+)',regs)
      if match and any(0<=int(match[1],16)-v<=3 for v in terminal):break
     else:raise RuntimeError('did not reach a bounded expected hold')
     qmp('stop');(d/'registers.txt').write_text(regs);c['registers']=regs
     for n,addr,size in [('target',spec['target']-4096,12288),('alias',spec['alias']-4096,12288),('fb',0x3000000,1228800)]:
      qmp('pmemsave',{'val':addr,'size':size,'filename':str(d/(n+'.bin'))})
     target=(d/'target.bin').read_bytes();alias=(d/'alias.bin').read_bytes();fb=(d/'fb.bin').read_bytes()
     assert len(target)==len(alias)==12288 and len(fb)==1228800
     assert target[:4096]==target[8192:]==alias[:4096]==alias[8192:]==b'\x5a'*4096
     c['phase_physical']=struct.unpack_from('<L',target,4096+0x540)[0];c['phase_alias']=struct.unpack_from('<L',alias,4096+0x540)[0]
     c['neighbor_guards_intact']=True
     if spec['index']<3:
      assert c['phase_physical']==4
      raw=struct.unpack_from('<12L',target,4096+0x5a0)
      assert raw[1]!=0x02a010de and raw[4:11]==(0xffffffff,)*7 and raw[11]==2
      c['native_read_result']=list(raw)
      expected=expected_framebuffer(raw[1:11],2)
      assert fb==expected,'framebuffer differs outside or inside intended green header'
      assert re.search(r'CS =0010',regs) and re.search(r'DS =0018',regs) and re.search(r'SS =0018',regs)
      cr0=int(re.search(r'CR0=([0-9a-fA-F]+)',regs)[1],16);assert cr0&0xe0000001==0x40000001
      assert int(re.search(r'CR3=([0-9a-fA-F]+)',regs)[1],16)==0
      assert not int(re.search(r'EFL=([0-9a-fA-F]+)',regs)[1],16)&0x200
      c['green_header_and_red_refusal_and_raw_panels_exact']=True
     else:
      assert fb==b'\x20'*1228800 and c['phase_physical'] not in (3,4)
      c['no_green_and_framebuffer_unchanged']=True
     c['passed']=True;qmp('quit');proc.wait(timeout=3)
    finally:
     if sock:sock.close()
     if proc.poll() is None:
      proc.terminate()
      try:proc.wait(timeout=3)
      except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=3);c['kill_required']=True
     c['closed']=proc.poll() is not None;c['exit_code']=proc.returncode;c['ended']=utc()
     if sockpath.exists():sockpath.unlink()
     c['files']={str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in d.iterdir() if p.is_file()};save(out,r)
  r['passed']=True
 except BaseException as e:r['failure']=repr(e);raise
 finally:r['closed']=all(c['closed'] for c in r['cases']);r['ended_utc']=utc();save(out,r)
 print('CPU fixtures passed; all owned VMs closed')
