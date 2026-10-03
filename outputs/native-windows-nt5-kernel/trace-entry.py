"""Release the owned guest's verified gate and trace native entry via xemu GDB."""
import argparse,json,pathlib,re,socket,struct,sys,time,traceback
out=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(out.parents[1]/'work/python-packages'))
sys.path.insert(0,str(out.parent/'native-windows-prebuild'))
import pefile
from monitor_capture import command
class Remote:
 def __init__(self,port):self.s=socket.create_connection(('127.0.0.1',port),timeout=5);self.s.settimeout(5)
 def recv(self):
  while True:
   c=self.s.recv(1)
   if not c:raise EOFError('GDB disconnected')
   if c not in [b'$',b'%']:continue
   b=bytearray()
   while True:
    c=self.s.recv(1)
    if not c:raise EOFError('GDB disconnected in packet')
    if c==b'#':break
    b+=c
   chk=self.s.recv(2)
   assert len(chk)==2 and int(chk,16)==sum(b)%256
   self.s.sendall(b'+')
   if b.startswith(b'O') and len(b)>2 and all(c in b'0123456789abcdefABCDEF' for c in b[1:]):continue
   return b.decode()
 def send(self,text):
  b=text.encode();self.s.sendall(b'$'+b+b'#'+f'{sum(b)%256:02x}'.encode())
 def ask(self,text):self.send(text);return self.recv()
 def interrupt(self):self.s.sendall(b'\x03');return self.recv()
 def read(self,addr,size):
  result=self.ask(f'm{addr:x},{size:x}');assert not result.startswith('E'),result
  data=bytes.fromhex(result);assert len(data)==size;return data
 def write(self,addr,data):assert self.ask(f'M{addr:x},{len(data):x}:'+data.hex())=='OK'
 def bp(self,addr,add=True):assert self.ask(f'{"Z" if add else "z"}0,{addr:x},1')=='OK'
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--monitor',type=int,required=True);p.add_argument('--state',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--trace-registry',action='store_true');p.add_argument('--trace-network',action='store_true');a=p.parse_args()
state=json.loads(a.state.read_text());assert state['status']=='pre_entry_halt_verified'
report={'scope':'Actual Windows kernel execution on xemu, isolated snapshot disk. Breakpoint observations do not prove a boot.','events':[],'pre_entry_state':str(a.state),'kernel_entered':False}
g=None
returns={}
def save():a.output.write_text(json.dumps(report,indent=2)+'\n')
def regs():
 text=command(a.monitor,'info registers')
 return {n:int(v,16) for n,v in re.findall(r'\b(EAX|EBX|ECX|EDX|ESI|EDI|EBP|ESP|EIP|EFL|CR0|CR2|CR3|CR4)=([0-9a-fA-F]+)',text)},text
def pnp_tree(kernel_base,pubs):
 layouts=json.loads((out/'pnp-layouts.json').read_text())
 fields=layouts['_DEVICE_NODE']['fields'];get=lambda n,f:struct.unpack('<I',g.read(n+fields[f]['offset'],4))[0]
 def ranges(head,seen=None):
  seen=set() if seen is None else seen;result=[];q=struct.unpack('<I',g.read(head,4))[0]
  while q!=head and len(result)<100 and q not in seen:
   seen.add(q);b=g.read(q-28,36);low,high=struct.unpack_from('<QQ',b);item={'start':hex(low),'end':hex(high),'owner':hex(struct.unpack_from('<I',b,20)[0]),'attributes':b[24],'flags':b[25],'internal_flags':b[26]};result.append(item)
   if b[26]&1:item['merged']=ranges(q-12,seen)
   q=struct.unpack_from('<I',b,28)[0]
  return result
 def uni(n,f):
  length,maximum,buffer=struct.unpack('<HHI',g.read(n+fields[f]['offset'],8))
  assert length<=2048 and length<=maximum
  return g.read(buffer,length).decode('utf-16le') if length else ''
 root=struct.unpack('<I',g.read(kernel_base+pubs['_IopRootDeviceNode']['rva'],4))[0]
 pending=[root];seen=set();result=[]
 while pending and len(seen)<128:
  n=pending.pop()
  if not n or n in seen:continue
  seen.add(n);item={'address':hex(n)};result.append(item)
  try:
   for field in ['Sibling','Child','Parent','Flags','Problem','PhysicalDeviceObject','FailureStatus','InterfaceType','BusNumber','ResourceRequirements','ResourceList','ResourceListTranslated','BootResources']:
    item[field]=hex(get(n,field))
   item['InstancePath']=uni(n,'InstancePath');item['ServiceName']=uni(n,'ServiceName')
   for field in ['ResourceList','ResourceListTranslated','BootResources']:
    addr=get(n,field)
    if addr:item[field+'_bytes']=g.read(addr,128).hex()
   addr=get(n,'ResourceRequirements')
   if addr:
    size=struct.unpack('<I',g.read(addr,4))[0]
    if 0<size<=8192:item['ResourceRequirements_bytes']=g.read(addr,size).hex()
   head=n+fields['DeviceArbiterList']['offset'];arb=struct.unpack('<I',g.read(head,4))[0];item['arbiters']=[]
   while arb!=head and len(item['arbiters'])<8:
    entry=g.read(arb,52);interface=struct.unpack_from('<I',entry,12)[0];record={'resource_type':struct.unpack_from('<I',entry,8)[0],'entry':entry.hex()}
    item['arbiters'].append(record)
    if interface:
     raw=g.read(interface,24);record['interface']=raw.hex();context=struct.unpack_from('<I',raw,4)[0];record['context_address']=hex(context)
     if context:
      data=g.read(context,156);record['context']=data.hex()
      # Common arbiter state has signature 'Arbs' at offset zero.
      if data[:4]==b'Arbs':
       for label,off in [('allocation',16),('possible',20)]:
        ptr=struct.unpack_from('<I',data,off)[0];record[label+'_list_address']=hex(ptr)
        if ptr:
         record[label+'_header']=g.read(ptr,20).hex();record[label+'_ranges']=ranges(ptr)
    arb=struct.unpack_from('<I',entry)[0]
   pending.extend([get(n,'Sibling'),get(n,'Child')])
  except Exception as e:item['read_error']=str(e)
 return result
try:
 g=Remote(a.port);report['gdb_features']=g.ask('qSupported');report['initial_stop']=g.ask('?')
 before,_=regs();report['gate_registers']={k:hex(v) for k,v in before.items()}
 symbols={int(state['kernel_entry'],16):'KernelEntry',0:'NullInstructionPointer'}
 files={'hal.dll':out/'artifacts/halxboxnt5.dll','ntoskrnl.exe':out.parent/'native-windows-nt5/installed-files/WINNT/system32/ntoskrnl.exe'}
 for m in state['modules']:
  if m['name'].lower() not in files:continue
  pe=pefile.PE(str(files[m['name'].lower()]));base=int(m['base'],16)
  for e in pe.DIRECTORY_ENTRY_EXPORT.symbols:
   if e.name and e.name.decode() in ['HalInitSystem','HalInitializeProcessor','KeBugCheckEx','KeBugCheck']:
    symbols[base+e.address]=e.name.decode()
 # Private HAL callbacks are COFF symbols in the reproducible diagnostic DLL.
 pe=pefile.PE(str(files['hal.dll']));base=int(next(m['base'] for m in state['modules'] if m['name'].lower()=='hal.dll'),16)
 data=pe.__data__;pos=pe.FILE_HEADER.PointerToSymbolTable;n=pe.FILE_HEADER.NumberOfSymbols;strings=pos+18*n;i=0
 while i<n:
  raw,value,section,typ,cls,aux=struct.unpack_from('<8sIhHBB',data,pos+18*i)
  if raw[:4]==b'\0'*4:
   off=struct.unpack_from('<I',raw,4)[0];start=strings+off;name=data[start:data.find(b'\0',start)].decode('ascii')
  else:name=raw.rstrip(b'\0').decode('ascii')
  if name in ['_HalpNt5GetInterruptTranslator@28','_HalpNt5TranslateResource@28','_HalpNt5TranslateRequirements@20','_HalpNt5QueryRootResources@4','_HalpNt5QueryRootRequirements@4','_HaliQuerySystemInformation@16','_HalpQueryInterface@28','_HaliFindBusAddressTranslation@24']:
   symbols[base+pe.sections[section-1].VirtualAddress+value]=name
  i+=1+aux
 kernel_base=int(next(m['base'] for m in state['modules'] if m['name'].lower()=='ntoskrnl.exe'),16)
 pubs=json.loads((out/'kernel-publics.json').read_text())['symbols']
 symbols[kernel_base+pubs['_IopInitializeBuiltinDriver@20']['rva']]='IopInitializeBuiltinDriver'
 symbols[kernel_base+pubs['_MmLoadSystemImage@24']['rva']]='_MmLoadSystemImage@24'
 for symbol in (['_CmpInitializeSystemHive@4','_CmpInitializeHive@40','_CmpLinkHiveToMaster@20','_HvInitializeHive@52','_CmCheckRegistry@8'] if a.trace_registry else []):
  if symbol in pubs:symbols[kernel_base+pubs[symbol]['rva']]=symbol
 symbols[kernel_base+0x122035]='HiveKeyCountMismatch'
 for addr in symbols:g.bp(addr)
 report['breakpoints']={hex(k):v for k,v in symbols.items()}
 record=state['record_candidates'][0];gate=int(record['physical_address'],16)+64
 assert g.read(gate,4)==b'\0'*4
 g.write(gate,struct.pack('<I',0x574e454e));report['gate_released']=True;save()
 started=time.monotonic()
 for event_index in range(500):
  g.send('c')
  timed_out=False
  try:stop=g.recv()
  except socket.timeout:stop=g.interrupt();timed_out=True
  r,text=regs();ip=r['EIP'];name=symbols.get(ip,'Timeout' if timed_out else 'OtherStop')
  event={'name':name,'stop':stop,'registers':{k:hex(v) for k,v in r.items()},'monitor_registers':text}
  try:event['stack_words']=[hex(v) for v in struct.unpack('<16I',g.read(r['ESP'],64))]
  except Exception as e:event['stack_read_error']=str(e)
  report['events'].append(event)
  if name=='NullInstructionPointer' or name.startswith('KeBugCheck') or (timed_out and not a.trace_network):
   caller=struct.unpack('<I',g.read(r['ESP'],4))[0]
   event['caller_address']=hex(caller);event['caller_window_start']=hex(caller-48)
   try:event['caller_window_hex']=g.read(caller-48,80).hex()
   except Exception as e:event['caller_window_read_error']=str(e)
   kernel_base=int(next(m['base'] for m in state['modules'] if m['name'].lower()=='ntoskrnl.exe'),16)
   pubs=json.loads((out/'kernel-publics.json').read_text())['symbols']
   module_head=kernel_base+pubs['_PsLoadedModuleList']['rva']
   event['live_modules']=[];node=struct.unpack('<I',g.read(module_head,4))[0]
   for _ in range(128):
    if node==module_head:break
    data=g.read(node,64);base,entry,size=struct.unpack_from('<III',data,24);length,maximum,buffer=struct.unpack_from('<HHI',data,44)
    name_=g.read(buffer,length).decode('utf-16le') if length else ''
    event['live_modules'].append({'base':hex(base),'entry':hex(entry),'size':size,'name':name_})
    node=struct.unpack_from('<I',data)[0]
   haldispatch=kernel_base+pubs['_HalDispatchTable']['rva']
   event['hal_dispatch_words']=[hex(v) for v in struct.unpack('<32I',g.read(haldispatch,128))]
   event['pnp_tree']=pnp_tree(kernel_base,pubs)
   try:
    layout=json.loads((out/'process-layouts.json').read_text())['_EPROCESS']['fields']
    head=kernel_base+pubs['_PsActiveProcessHead']['rva'];link=struct.unpack('<I',g.read(head,4))[0]
    event['processes']=[];seen_processes=set()
    while link!=head and link not in seen_processes and len(seen_processes)<128:
     seen_processes.add(link);process=link-layout['ActiveProcessLinks']['offset']
     pid=struct.unpack('<I',g.read(process+layout['UniqueProcessId']['offset'],4))[0]
     image=g.read(process+layout['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace')
     event['processes'].append({'pid':pid,'image':image,'eprocess':hex(process)})
     link=struct.unpack('<I',g.read(link,4))[0]
   except Exception as e:event['process_read_error']=str(e)
   event['frames']=[];frame=r['EBP'];seen=set()
   for _ in range(20):
    if frame in seen or not frame:break
    seen.add(frame)
    try:
     data=struct.unpack('<6I',g.read(frame,24));event['frames'].append({'ebp':hex(frame),'words':[hex(v) for v in data]});frame=data[0]
    except Exception:break
   if name=='NullInstructionPointer':report['outcome']='null_instruction_pointer';save();break
  if name=='KernelEntry':
   report['kernel_entered']=True;g.bp(ip,False);del symbols[ip]
  elif name=='HiveKeyCountMismatch':
   event['key_node_hex']=g.read(r['EDI'],160).hex()
   event['key_index_hex']=g.read(r['ESI'],160).hex()
   event['check_debug_hex']=g.read(kernel_base+pubs['_CmpCheckKeyDebug']['rva'],64).hex()
   g.bp(ip,False);del symbols[ip]
  elif name in ['HalInitSystem','HalInitializeProcessor','IopInitializeBuiltinDriver'] or name.startswith(('_HalpNt5','_Hali','_HalpQueryInterface','_MmLoadSystemImage','DriverEntry_','_Nt5Video','_Cm','_Hv','_NvNet','_MiniportInitialize','_Allocate','_NdisM')):
   count=(int(name.rsplit('@',1)[1])//4+1) if name.startswith('_') and '@' in name else (6 if name=='IopInitializeBuiltinDriver' else 3)
   words=struct.unpack('<'+'I'*count,g.read(r['ESP'],count*4));ret=words[0]
   event['arguments']=[hex(v) for v in words[1:]]
   if name=='_MmLoadSystemImage@24':
    try:
     length,maximum,buffer=struct.unpack('<HHI',g.read(words[1],8));event['image_name']=g.read(buffer,length).decode('utf-16le')
    except Exception as e:event['image_name_error']=str(e)
   if name=='IopInitializeBuiltinDriver':
    try:
     length,maximum,buffer=struct.unpack('<HHI',g.read(words[1],8));driver_name=g.read(buffer,length).decode('utf-16le')
    except Exception:driver_name=hex(words[3])
    event['driver_name']=driver_name
    if words[3] not in symbols:symbols[words[3]]='DriverEntry_'+driver_name;g.bp(words[3])
   if name=='_NdisMInitializeScatterGatherDma@12':
    event['miniport_block_prefix']=g.read(words[1],0x420).hex()
   if name=='_HalpQueryInterface@28':event['interface_guid_hex']=g.read(words[2],16).hex()
   returns[ret]={'name':name,'args':words[1:],'image_name':event.get('image_name','')}
   if ret not in symbols:symbols[ret]='Return_'+name;g.bp(ret)
   # QEMU remote breakpoints remain at the current PC until stepped past.
   g.bp(ip,False);event['step_over_breakpoint']=g.ask('s');g.bp(ip)
  elif name.startswith('Return_'):
   entry=returns.pop(ip,None)
   if entry:
    event['entry_arguments']=[hex(v) for v in entry['args']]
    if entry['name']=='_MmLoadSystemImage@24' and r['EAX']==0 and entry['image_name'].lower().endswith(('xboxvnt5.sys','nvnetnt5.sys')):
     video_base=struct.unpack('<I',g.read(entry['args'][5],4))[0];event['video_base']=hex(video_base)
     image_file='nvnetnt5.sys' if entry['image_name'].lower().endswith('nvnetnt5.sys') else 'xboxvnt5.sys'
     video=pefile.PE(str(out/'artifacts'/image_file));symbols[video_base+video.OPTIONAL_HEADER.AddressOfEntryPoint]='DriverEntry_'+image_file;g.bp(video_base+video.OPTIONAL_HEADER.AddressOfEntryPoint)
     if a.trace_network and image_file=='nvnetnt5.sys':
      calls={'NdisMSetAttributesEx':20,'NdisMAllocateMapRegisters':20,'NdisMFreeMapRegisters':4,'NdisMQueryAdapterResources':16,'NdisMMapIoSpace':20,'NdisMInitializeScatterGatherDma':12,'NdisMAllocateSharedMemory':24,'NdisMRegisterInterrupt':28}
      for imports in video.DIRECTORY_ENTRY_IMPORT:
       for symbol in imports.imports:
        name_=symbol.name.decode() if symbol.name else ''
        if name_ in calls:
         addr_=struct.unpack('<I',g.read(video_base+symbol.address-video.OPTIONAL_HEADER.ImageBase,4))[0]
         symbols[addr_]='_'+name_+'@'+str(calls[name_]);g.bp(addr_)
     data_=video.__data__;pos_=video.FILE_HEADER.PointerToSymbolTable;n_=video.FILE_HEADER.NumberOfSymbols;strings_=pos_+18*n_;i_=0
     while i_<n_:
      raw_,value_,section_,typ_,cls_,aux_=struct.unpack_from('<8sIhHBB',data_,pos_+18*i_)
      if raw_[:4]==b'\0'*4:
       off_=struct.unpack_from('<I',raw_,4)[0];start_=strings_+off_;name_=data_[start_:data_.find(b'\0',start_)].decode('ascii')
      else:name_=raw_.rstrip(b'\0').decode('ascii')
      if section_>0 and (name_.startswith('_Nt5Video') or (a.trace_network and name_.split('@')[0] in ['_MiniportInitialize','_NvNetReadConfiguration','_NvNetRecognizeHardware','_NvNetInitializeAdapterResources','_AllocateAdapterMemory','_NvNetGetPermanentMacAddress','_NvNetInitNIC','_NvNetFreeAdapter','_AllocateTransmitBuffers','_AllocateTransmitBlocks','_AllocateTransmitDescriptors','_AllocateReceiveDescriptors','_AllocateReceiveBuffers'])):
       address_=video_base+video.sections[section_-1].VirtualAddress+value_;symbols[address_]=name_;g.bp(address_)
      i_+=1+aux_
    if entry['name']=='_NdisMQueryAdapterResources@16':
     event['ndis_status']=g.read(entry['args'][0],4).hex();event['resources_size']=g.read(entry['args'][3],4).hex()
    if entry['name']=='_HaliQuerySystemInformation@16' and r['EAX']==0:
     event['output_hex']=g.read(entry['args'][2],min(entry['args'][1],256)).hex()
    if entry['name']=='_HaliFindBusAddressTranslation@24':
     event['address_space']=g.read(entry['args'][2],4).hex();event['translated']=g.read(entry['args'][3],8).hex();event['context']=g.read(entry['args'][4],4).hex()
   g.bp(ip,False);del symbols[ip]
  elif name.startswith('KeBugCheck'):
   if event.get('stack_words',[None,None])[1]=='0x7b':
    pointer=int(event['stack_words'][2],16)
    try:
     length,maximum,buffer=struct.unpack('<HHI',g.read(pointer,8));event['boot_device_name']=g.read(buffer,length).decode('utf-16le')
    except Exception as e:event['boot_device_read_error']=str(e)
   report['outcome']='bugcheck_breakpoint';save();break
  elif timed_out and a.trace_network:
   pass
  elif timed_out:
   report['outcome']='no_breakpoint_within_5_seconds';save();break
  else:
   report['outcome']='unexpected_debug_stop';save();break
  save()
  if time.monotonic()-started>(150 if a.trace_network else 75):report['outcome']='trace_time_limit';break
 else:report['outcome']='trace_event_limit'
 report.setdefault('outcome','trace_complete')
except Exception as exc:
 report['outcome']='trace_exception';report['error']=repr(exc);report['traceback']=traceback.format_exc()
finally:
 if g:
  removed=[];errors=[]
  for address in list(locals().get('symbols',{})):
   try:g.bp(address,False);removed.append(hex(address))
   except Exception as e:errors.append({'address':hex(address),'error':str(e)})
  report['breakpoint_cleanup']={'removed':removed,'errors':errors}
 save()
 if g:g.s.close()
print(json.dumps({'kernel_entered':report['kernel_entered'],'events':[e['name'] for e in report['events']],'outcome':report['outcome'],'error':report.get('error')},indent=2))

