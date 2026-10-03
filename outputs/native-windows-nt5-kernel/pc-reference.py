"""Read native HAL root bus resources from an isolated PC snapshot, under WSL."""
import pathlib,sys,os,subprocess,socket,json,time,re,struct
root=pathlib.Path('/home/paul/xbox-windows-native')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
out=ws/'outputs/native-windows-nt5-kernel/pc-reference';out.mkdir(exist_ok=True)
vm=root/'fixtures/pc-reference';vm.mkdir(exist_ok=True);sock=vm/'qmp.sock';raw=vm/'memory.raw'
assert not sock.exists() and not raw.exists()
runtime=root/'toolchains/qemu-pc/root';env=dict(os.environ,LD_LIBRARY_PATH=str(runtime/'usr/lib/x86_64-linux-gnu'))
args=[str(runtime/'usr/bin/qemu-system-i386'),'-name','xwn-pc-reference','-L',str(runtime/'usr/share/qemu'),'-bios',str(runtime/'usr/share/seabios/bios.bin'),'-machine','pc,acpi=off,hpet=off','-accel','tcg,thread=single','-cpu','pentium3','-smp','1','-m','64','-vga','cirrus','-display','none','-nic','none','-drive',f'file={ws}/outputs/native-windows-nt5/artifacts/windows2000-pc-base.qcow2,format=qcow2,if=ide,index=0','-snapshot','-boot','order=c','-qmp',f'unix:{sock},server=on,wait=off','-no-reboot']
log=(out/'launch.log').open('wb');proc=subprocess.Popen(args,env=env,stdout=log,stderr=subprocess.STDOUT)
(out/'instance.json').write_text(json.dumps({'pid':proc.pid,'command':args},indent=2)+'\n')
try:
 for _ in range(120):
  if proc.poll() is not None:raise RuntimeError('QEMU exited')
  if sock.exists():break
  time.sleep(.25)
 s=socket.socket(socket.AF_UNIX);s.settimeout(20);s.connect(str(sock));f=s.makefile('rwb',buffering=0);json.loads(f.readline())
 def command(name,arguments=None):
  f.write((json.dumps({'execute':name,'arguments':arguments or {}})+'\n').encode())
  while True:
   result=json.loads(f.readline())
   if 'error' in result:raise RuntimeError(result)
   if 'return' in result:return result['return']
 command('qmp_capabilities');time.sleep(40)
 command('stop');regs=command('human-monitor-command',{'command-line':'info registers'})
 command('screendump',{'filename':str(out/'desktop.png'),'format':'png'})
 command('pmemsave',{'val':0,'size':64*1024*1024,'filename':str(raw)})
 data=raw.read_bytes();cr3=int(re.search(r'CR3=([0-9a-fA-F]+)',regs)[1],16)
 def phys32(a):return struct.unpack_from('<I',data,a)[0]
 def read(va,size):
  result=b''
  while size:
   pde=phys32((cr3&0xfffff000)+4*(va>>22));assert pde&1
   if pde&128:pa=(pde&0xffc00000)+(va&0x3fffff)
   else:
    pte=phys32((pde&0xfffff000)+4*((va>>12)&1023));assert pte&1
    pa=(pte&0xfffff000)+(va&4095)
   n=min(size,4096-(va&4095));result+=data[pa:pa+n];va+=n;size-=n
  return result
 def u32(a):return struct.unpack('<I',read(a,4))[0]
 candidates=[]
 for pos in range(0,len(data)-4096,4096):
  if data[pos:pos+2]!=b'MZ':continue
  offset=phys32(pos+60)
  if offset>4096 or data[pos+offset:pos+offset+4]!=b'PE\0\0':continue
  if phys32(pos+offset+8)==0x4b7a1bd5:candidates.append(pos)
 assert candidates,candidates
 # Find the mapped virtual base using the current page tables, not an assumed PC base.
 bases=[]
 for page in range(0x80000,0xc0000):
  va=page*4096
  pde=phys32((cr3&0xfffff000)+4*(va>>22))
  if not pde&1:continue
  if pde&128:mapped=(pde&0xffc00000)+(va&0x3fffff)
  else:
   pte=phys32((pde&0xfffff000)+4*((va>>12)&1023))
   if not pte&1:continue
   mapped=pte&0xfffff000
  if mapped in candidates:bases.append(va)
 pubs=json.loads((out.parent/'kernel-publics.json').read_text())['symbols']
 valid=[]
 for b in bases:
  try:
   node=u32(b+pubs['_PsLoadedModuleList']['rva'])
   if u32(node+24)==b:valid.append(b)
  except (AssertionError,struct.error):pass
 assert len(valid)==1,(candidates,bases,valid)
 base=valid[0]
 layouts=json.loads((out.parent/'pnp-layouts.json').read_text());fields=layouts['_DEVICE_NODE']['fields']
 def get(n,name):return u32(n+fields[name]['offset'])
 def uni(n,name):
  length,maximum,buffer=struct.unpack('<HHI',read(n+fields[name]['offset'],8));return read(buffer,length).decode('utf-16le') if length else ''
 pending=[u32(base+pubs['_IopRootDeviceNode']['rva'])];seen=set();nodes=[]
 while pending and len(seen)<200:
  n=pending.pop()
  if not n or n in seen:continue
  seen.add(n);item={'InstancePath':uni(n,'InstancePath'),'ServiceName':uni(n,'ServiceName'),'Problem':get(n,'Problem')};nodes.append(item)
  for field in ['ResourceList','ResourceListTranslated','BootResources','ResourceRequirements']:
   addr=get(n,field);item[field]=hex(addr)
   if addr:item[field+'_bytes']=read(addr,256).hex()
  pending.extend([get(n,'Sibling'),get(n,'Child')])
 (out/'pnp-tree.json').write_text(json.dumps({'kernel_base':hex(base),'registers':regs,'pnp_tree':nodes},indent=2)+'\n')
 command('quit');proc.wait(timeout=15);f.close();s.close()
 print(json.dumps({'kernel_base':hex(base),'nodes':len(nodes),'root_pci_nodes':[n for n in nodes if 'PNP0A03' in n['InstancePath']]},indent=2))
finally:
 if proc.poll() is None:proc.terminate();proc.wait(timeout=15)
 log.close();raw.unlink(missing_ok=True);sock.unlink(missing_ok=True)
 (out/'cleanup.json').write_text(json.dumps({'pid':proc.pid,'exit_code':proc.returncode,'raw_memory_removed':not raw.exists(),'snapshot_discarded':True})+'\n')
