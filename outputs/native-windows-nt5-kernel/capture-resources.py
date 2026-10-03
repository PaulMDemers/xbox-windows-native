"""Read a private xemu's live NT process/device lists without kernel breakpoints."""
import argparse,json,pathlib,re,struct,sys
out=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(out.parent/'native-windows-prebuild'))
from monitor_capture import command, acquire_monitor_lock
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
raw=a.output.with_suffix('.ram');assert not raw.exists()
report={'scope':'Read-only Xbox emulator runtime observation; physical console untested'}
lock=acquire_monitor_lock(a.port)
vm_status = command(a.port,'info status')
was_running = 'VM status: running' in vm_status
report['vm_status_before_capture'] = vm_status.split('VM status:')[-1].splitlines()[0].strip()
command(a.port,'stop')
try:
 regs=command(a.port,'info registers');report['registers']=regs
 command(a.port,'pmemsave 0 67108864 '+json.dumps(raw.resolve().as_posix()))
 data=raw.read_bytes();assert len(data)==64*1024**2
 cr3=int(re.search(r'CR3=([0-9a-fA-F]+)',regs)[1],16)
 def phys32(a):return struct.unpack_from('<I',data,a)[0]
 def pa(va):
  pde=phys32((cr3&0xfffff000)+4*(va>>22));assert pde&1
  if pde&128:return (pde&0xffc00000)+(va&0x3fffff)
  pte=phys32((pde&0xfffff000)+4*((va>>12)&1023));assert pte&1
  return (pte&0xfffff000)+(va&4095)
 def read(va,size):
  result=b''
  while size:
   at=pa(va);n=min(size,4096-(va&4095));assert at+n<=len(data)
   result+=data[at:at+n];va+=n;size-=n
  return result
 def u32(a):return struct.unpack('<I',read(a,4))[0]
 candidates=[]
 for pos in range(0,len(data)-4096,4096):
  if data[pos:pos+2]!=b'MZ':continue
  offset=phys32(pos+60)
  if offset>4096 or data[pos+offset:pos+offset+4]!=b'PE\0\0':continue
  if phys32(pos+offset+8)==0x4b7a1bd5:candidates.append(pos)
 pubs=json.loads((out/'kernel-publics.json').read_text())['symbols'];valid=[]
 for page in range(0x80000,0xc0000):
  va=page*4096
  try:
   if pa(va) not in candidates:continue
   node=u32(va+pubs['_PsLoadedModuleList']['rva'])
   if u32(node+24)==va:valid.append(va)
  except (AssertionError,struct.error):pass
 assert len(valid)==1,('kernel mapping candidates',valid)
 base=valid[0];report['kernel_base']=hex(base)
 modules=[];head=base+pubs['_PsLoadedModuleList']['rva'];link=u32(head);seen=set()
 while link!=head and link not in seen and len(seen)<256:
  seen.add(link);module_base,entry,size=struct.unpack('<III',read(link+24,12))
  length,maximum,buffer=struct.unpack('<HHI',read(link+44,8));assert length<=maximum and length<1024
  modules.append({'name':read(buffer,length).decode('utf-16le') if length else '', 'base':hex(module_base),'entry':hex(entry),'size':size})
  link=u32(link)
 assert link==head;report['modules']=modules
 if '_KiBugCheckData' in pubs:
  report['bugcheck_data']=[hex(v) for v in struct.unpack('<5I',read(base+pubs['_KiBugCheckData']['rva'],20))]
 fields=json.loads((out/'process-layouts.json').read_text())['_EPROCESS']['fields']
 head=base+pubs['_PsActiveProcessHead']['rva'];link=u32(head);seen=set();processes=[]
 while link!=head and link not in seen and len(seen)<128:
  seen.add(link);process=link-fields['ActiveProcessLinks']['offset']
  processes.append({'pid':u32(process+fields['UniqueProcessId']['offset']),'image':read(process+fields['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace')})
  link=u32(link)
 assert link==head;report['processes']=processes
 fields=json.loads((out/'pnp-layouts.json').read_text())['_DEVICE_NODE']['fields']
 def field(n,f):return u32(n+fields[f]['offset'])
 def uni(n,f):
  length,maximum,buffer=struct.unpack('<HHI',read(n+fields[f]['offset'],8));assert length<=maximum and length<=2048
  return read(buffer,length).decode('utf-16le') if length else ''
 pending=[u32(base+pubs['_IopRootDeviceNode']['rva'])];seen=set();nodes=[]
 while pending and len(seen)<256:
  n=pending.pop()
  if not n or n in seen:continue
  seen.add(n);nodes.append({'InstancePath':uni(n,'InstancePath'),'ServiceName':uni(n,'ServiceName'),'Problem':field(n,'Problem'),'FailureStatus':hex(field(n,'FailureStatus'))})
  node=nodes[-1]
  for name in ['ResourceList','ResourceListTranslated','BootResources']:
   ptr=field(n,name)
   if not ptr:continue
   try:
    count=u32(ptr);at=ptr+4;lists=[];assert count<20
    for _ in range(count):
     interface,bus,version,revision,total=struct.unpack('<IIHHI',read(at,16));at+=16;assert total<100
     desc=[]
     for _ in range(total):
      descriptor=read(at,16);kind,share,flags=struct.unpack_from('<BBH',descriptor);desc.append({'type':kind,'share':share,'flags':flags,'data':list(struct.unpack_from('<III',descriptor,4))});at+=16
     lists.append({'interface':interface,'bus':bus,'descriptors':desc})
    node[name]=lists
   except (AssertionError,struct.error) as e:node[name+'_error']=repr(e)
  ptr=field(n,'ResourceRequirements')
  if ptr:
   try:
    length=u32(ptr);assert 32<=length<16384
    node['requirements_raw']=read(ptr,length).hex()
   except (AssertionError,struct.error):pass
  pending.extend([field(n,'Sibling'),field(n,'Child')])
 report['pnp_tree']=nodes
 report['tick_count']=u32(base+pubs['_KeTickCount']['rva'])
 if '_MmNumberOfPhysicalPages' in pubs:report['physical_pages']=u32(base+pubs['_MmNumberOfPhysicalPages']['rva'])
 report['status']='shell_running' if any(p['image'].lower()=='explorer.exe' for p in processes) else 'kernel_running'
 if report.get('bugcheck_data',['0x0'])[0]!='0x0':report['status']='bugcheck_reported'
except Exception as e:
 report['status']='runtime_not_decoded';report['error']=repr(e)
finally:
 raw.unlink(missing_ok=True);report['raw_memory_removed']=not raw.exists()
 a.output.write_text(json.dumps(report,indent=2)+'\n')
 try:
  if was_running:command(a.port,'cont')
 finally:lock.close()
print(json.dumps({k:report[k] for k in ['status','kernel_base','tick_count','error'] if k in report}))
