"""Fresh diskless705 CPU fixtures; PCI refusal on PC, no Xbox model or Windows."""
import datetime,hashlib,json,os,re,socket,struct,subprocess,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('/mnt/c/xwn761/cpu001');P=Path('/mnt/c/xwn761/host002')
sys.path.insert(0,str(K))
from optical_oracle import paint_report
ROOT=Path('/home/paul/xbox-windows-native/toolchains/qemu-pc/root');Q=ROOT/'usr/bin/qemu-system-i386'
env=dict(os.environ,LD_LIBRARY_PATH=str(ROOT/'usr/lib/x86_64-linux-gnu'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
save=lambda p,r:p.write_text(json.dumps(r,indent=2)+'\n')
sys.path.insert(0,str(W/'tools'));from build_space import require_space
NAMES=['dual','identity','relocated','scatter','bad_magic','bad_base','fb_extent','missing_middle_page','missing_stack_page','physical_payload_corrupt','alias_payload_corrupt','post_pg_ud2']
assert sys.argv[1] in ('build','run')
if sys.argv[1]=='build':
 assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists()
 r={'passed':False,'physical_access':False,'space':require_space(O,20.15),'commands':[],'cases':[]};O.mkdir(parents=True)
 try:
  b=json.loads((K/'host002.json').read_text());assert b['passed']
  for n,h in b['files'].items():assert sha(P/n)==h
  for n,h in b['sources'].items():assert sha(K/n)==h
  pins=[Q,ROOT/'usr/share/seabios/bios.bin',ROOT/'usr/share/qemu/multiboot.bin',Path('/usr/bin/as'),Path('/usr/bin/ld'),K/'fixture.S',K/'link.ld',K/'cpu002.py']
  for tool in [Q,Path('/usr/bin/as'),Path('/usr/bin/ld')]:
   listing=subprocess.check_output(['ldd',str(tool)],env=env,text=True)
   pins.extend(Path(p) for p in re.findall(r'(?:=>\s+|^\s*)(/[^\s]+)',listing,re.M))
  r['inputs']={str(p):sha(p) for p in dict.fromkeys(pins)};r['bridge_symbols']=b['bridge_symbols']
  def run(args,d):
   r['commands'].append([str(a) for a in args])
   with (O/'build.log').open('ab') as f:subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=30,check=True)
  for i,name in enumerate(NAMES):
   d=O/name;d.mkdir();base=0x1ed8000 if i==2 else 0x1ef0000;alias=base if i==1 else 0x2200000
   stride=8192 if i==3 else 4096
   (d/'page.bin').write_bytes((P/(name if i<4 else 'dual')/'page.bin').read_bytes())
   defs=[v for key,val in {'CASE':i,'TARGET':base,'ALIAS':alias,'STRIDE':stride,'POST_OFFSET':b['bridge_symbols']['bridge_post']}.items() for v in ['--defsym',str(key)+'='+str(val)]]
   run(['as','--32',*defs,str(K/'fixture.S'),'-o','fixture.o'],d)
   run(['ld','-m','elf_i386','-T',str(K/'link.ld'),'fixture.o','-o','fixture.elf'],d)
   sy={a[2]:int(a[0],16) for l in subprocess.check_output(['nm','-n',str(d/'fixture.elf')],text=True).splitlines() if len(a:=l.split())==3}
   r['cases'].append({'name':name,'index':i,'base':base,'alias':alias,'stride':stride,'fixture_fault':sy['fixture_fault_loop']})
  r['passed']=True
 except BaseException as e:r['failure']=repr(e);raise
 finally:
  r['files']={str(p):sha(p) for p in O.rglob('*') if p.is_file()};r['ended_utc']=utc();save(K/'cpu-build001.json',r)
 print('PASS fresh705 diskless fixture build')
else:
 assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
 b=json.loads((K/'cpu-build001.json').read_text());assert b['passed']
 assert all(sha(Path(p))==h for p,h in b['inputs'].items())
 assert all(sha(Path(p))==h for p,h in b['files'].items())
 out=K/'cpu-run001.json';assert not out.exists()
 r={'passed':False,'closed':False,'physical_access':False,'scope':__doc__,'cases':[]};save(out,r)
 try:
  for spec in b['cases']:
   d=O/('run-'+spec['name']);d.mkdir();sockpath=Path('/tmp/xwn761-cpu001-'+spec['name']+'.sock');assert not sockpath.exists()
   cmd=[str(Q),'-name','xwn761-'+spec['name'],'-L',str(ROOT/'usr/share/qemu'),'-bios',str(ROOT/'usr/share/seabios/bios.bin'),'-machine','pc,acpi=off,hpet=off','-accel','tcg,thread=single','-cpu','pentium3','-smp','1','-m','64','-vga','none','-display','none','-nic','none','-serial','none','-monitor','none','-qmp','unix:'+str(sockpath)+',server=on,wait=off','-S','-kernel',str(O/spec['name']/'fixture.elf'),'-debugcon','file:'+str(d/'debug.bin'),'-no-reboot','-d','int,cpu_reset','-D',str(d/'cpu.log')]
   c=dict(spec,command=cmd,started=utc(),closed=False,passed=False);r['cases'].append(c);save(out,r)
   with (d/'qemu.log').open('xb') as f:
    p=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT);c['pid']=p.pid;save(out,r)
    sock=None
    try:
     for _ in range(100):
      if sockpath.exists():break
      assert p.poll() is None;time.sleep(.05)
     sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);sock.settimeout(3);sock.connect(str(sockpath));stream=sock.makefile('rb')
     assert 'QMP' in json.loads(stream.readline())
     def qmp(name,args=None):
      data={'execute':name}
      if args is not None:data['arguments']=args
      sock.sendall((json.dumps(data)+'\n').encode())
      while True:
       v=json.loads(stream.readline())
       if 'return' in v:return v['return']
       if 'error' in v:raise RuntimeError(v)
     qmp('qmp_capabilities');qmp('cont')
     terminal=[spec['base']+b['bridge_symbols']['bridge_hold'],spec['base']+b['bridge_symbols']['bridge_fault'],spec['fixture_fault']]
     for _ in range(100):
      time.sleep(.05);regs=qmp('human-monitor-command',{'command-line':'info registers'})
      m=re.search(r'EIP=([0-9a-fA-F]+)',regs)
      if m and any(0<=int(m[1],16)-v<=3 for v in terminal):break
     else:raise RuntimeError('no bounded terminal state')
     qmp('stop');(d/'registers.txt').write_text(regs);c['registers']=regs
     for n,a,size in [('physical',spec['base']-4096,40960),('alias',spec['alias']-4096,73728 if spec['alias']!=spec['base'] else 40960),('fb',0x3000000,3686400)]:
      qmp('pmemsave',{'val':a,'size':size,'filename':str(d/(n+'.bin'))})
     physical=(d/'physical.bin').read_bytes();alias=(d/'alias.bin').read_bytes();fb=(d/'fb.bin').read_bytes()
     assert physical[:4096]==physical[-4096:]==b'\x5a'*4096
     assert alias[:4096]==b'\x5a'*4096
     if spec['stride']==8192:
      for i in range(8):assert alias[4096+i*8192+4096:4096+(i+1)*8192]==b'\x5a'*4096
     else:assert alias[36864:40960]==b'\x5a'*4096
     expected_fb=bytearray(b'\x20'*3686400)
     if spec['index']<4:
      for first,color in [(8,0x00ff00),(48,0xff0000)]:
       for row in range(first,first+32):expected_fb[row*5120+32:row*5120+32+5056]=struct.pack('<I',color)*1264
      # PC bridge refuses GPU id before payload; expected fields are literal, not decoded from its result.
      paint_report(expected_fb,[0x7610000d,0,0,0,0,0,0,0,0,0,0,0,0])
     assert fb==expected_fb,'bounded status bars/report or untouched refusal framebuffer'
     phase=struct.unpack_from('<I',physical,4096+0x880)[0];c['physical_phase']=phase
     c['alias_phase']=struct.unpack_from('<I',alias,4096+0x880)[0]
     if spec['index']<4:
      assert phase==2 and struct.unpack_from('<I',physical,4096+0x8d0)[0]==1
      assert struct.unpack_from('<I',physical,4096+0x8a4)[0]!=0x02a010de
      assert physical[4096+0x1000:4096+0x4800]==(O/spec['name']/'page.bin').read_bytes()[0x1000:0x4800]
      assert re.search('CS =0010',regs) and re.search('DS =0018',regs) and re.search('SS =0018',regs)
      assert int(re.search('CR0=([0-9a-fA-F]+)',regs)[1],16)&0xe0000001==0x40000001
      assert int(re.search('CR3=([0-9a-fA-F]+)',regs)[1],16)==0
      assert int(re.search('ESP=([0-9a-fA-F]+)',regs)[1],16)==spec['base']+32768
      assert not int(re.search('EFL=([0-9a-fA-F]+)',regs)[1],16)&0x200
      c['native_context_and_PC_PCI_refusal']=True
     else:assert phase!=3 and int(m[1],16) not in (terminal[0],terminal[0]+1),'unexpected admission'
     c['neighbor_guards_and_expected_framebuffer']=True;c['passed']=True
     qmp('quit');p.wait(timeout=3)
    finally:
     if sock:sock.close()
     if p.poll() is None:
      p.terminate()
      try:p.wait(timeout=3)
      except subprocess.TimeoutExpired:p.kill();p.wait(timeout=3);c['kill_required']=True
     c['closed']=p.poll() is not None;c['exit_code']=p.returncode;c['ended']=utc()
     if sockpath.exists():sockpath.unlink()
     c['files']={str(q):{'sha256':sha(q),'bytes':q.stat().st_size} for q in d.iterdir() if q.is_file()};save(out,r)
  r['passed']=True
 except BaseException as e:r['failure']=repr(e);raise
 finally:r['closed']=all(c['closed'] for c in r['cases']);r['ended_utc']=utc();save(out,r)
 print('PASS12 fresh CPU contexts/refusals; all VMs closed')
