"""Read-only bounded tracing of dump-usage IRP dispatch, returns and completion."""
import hashlib,json,socket,struct,sys,time,datetime
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='dispatch001'
out=k/case;run=ws/('work/runs/nt5-dump-usage-trace-'+case);assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
review=read(k/'sites.json');layout=read(k/'layouts.json');L=layout['structures'];mods=read(k/'modules.json')
for n,h in review['dependencies'].items():assert sha(k.parent/n)==h
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
pes={}
for n,m in mods.items():assert sha(Path(m['path']))==m['sha256'];pes[n]=pefile.PE(m['path'])
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
owner=read(k.parent/'shutdown-popup-workload/site-review.json')['thread_owner_offset'];K=review['kernel_base_expected'];utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,started_utc=utc(),source_sha256=sha(Path(__file__)),input_sha256={n:sha(k/n) for n in ['sites.json','layouts.json','modules.json']},events=[],module_list=[],runtime_pins=[],ignored_hits={},tracked_irps=[],calls=[])
g=None;stopped=False;armed=set();sites={s['address']:dict(s) for s in review['sites']};return_owners={};tracked={};active=None;loaded=[];lock=acquire_monitor_lock(4594)
def save():write_json(out/'trace.json',r)
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def field(typ,name):return L[typ]['fields'][name]['offset']
def uni(a):
 n,maxn,p=struct.unpack('<HHI',g.read(a,8));assert n<=maxn and n<=2048;return g.read(p,n).decode('utf-16le') if n else ''
def who():
 t=u32(0xffdff124);p=u32(t+owner);return dict(thread=hex(t),process=hex(p),pid=u32(p+field('_EPROCESS','UniqueProcessId')),image=g.read(p+field('_EPROCESS','ImageFileName'),16).split(b'\0')[0].decode('ascii',errors='replace'))
def registers():return dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
def module_list():
 head=K+review['loaded_module_list_rva'];q=u32(head);seen=set();rows=[]
 while q!=head:
  assert q and q not in seen and len(seen)<200;seen.add(q);node=q-field('_LDR_DATA_TABLE_ENTRY','InLoadOrderLinks')
  rows.append(dict(base=u32(node+field('_LDR_DATA_TABLE_ENTRY','DllBase')),size=u32(node+field('_LDR_DATA_TABLE_ENTRY','SizeOfImage')),name=uni(node+field('_LDR_DATA_TABLE_ENTRY','BaseDllName')),path=uni(node+field('_LDR_DATA_TABLE_ENTRY','FullDllName'))));q=u32(q)
 return rows
def pin(a,n=16):
 m=next((v for v in loaded if v['base']<=a<v['base']+v['size']),None);assert m is not None,('No loaded module',hex(a))
 name=m['name'].lower();assert name in mods,('Unpinned module',name,hex(a));p=pes[name];base=m['base'];rva=a-base
 assert g.read(base,2)==b'MZ' and u32(base+u32(base+60)+8)==mods[name]['timestamp']
 # Include any HIGHLOW relocation straddling the requested window end.
 while True:
  rel=[e.rva-rva for block in p.DIRECTORY_ENTRY_BASERELOC for e in block.entries if e.type==3 and rva<=e.rva<rva+n]
  end=max([n]+[o+4 for o in rel]);assert end<=64
  if end==n:break
  n=end
 raw=p.get_data(rva,n);assert len(raw)==n;data=bytearray(raw)
 for off in rel:struct.pack_into('<I',data,off,(struct.unpack_from('<I',data,off)[0]+base-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 actual=g.read(a,n);assert actual==data,('Resident mismatch',name,hex(rva),actual.hex(),data.hex())
 row=dict(address=hex(a),module=name,base=hex(base),rva=hex(rva),source_sha256=mods[name]['sha256'],raw=raw.hex(),resident=actual.hex(),relocations=rel)
 r['runtime_pins'].append(row);return len(r['runtime_pins'])-1

def device(a,major):
 d=u32(a+field('_DEVICE_OBJECT','DriverObject'));base=u32(d+field('_DRIVER_OBJECT','DriverStart'));target=u32(d+field('_DRIVER_OBJECT','MajorFunction')+major*4)
 return dict(device=hex(a),driver=hex(d),name=uni(d+field('_DRIVER_OBJECT','DriverName')),base=hex(base),size=u32(d+field('_DRIVER_OBJECT','DriverSize')),dispatch_address=hex(target),dispatch_pin=pin(target))
def snapshot(irp):
 return dict(irp=hex(irp),io_status=hex(u32(irp+field('_IRP','IoStatus'))),information=hex(u32(irp+field('_IRP','IoStatus')+4)),current_location=g.read(irp+field('_IRP','CurrentLocation'),1)[0],stack_count=g.read(irp+field('_IRP','StackCount'),1)[0],current_stack=hex(u32(irp+layout['irp_current_stack_location_offset'])))
def arm(a):
 if a not in armed:g.bp(a);armed.add(a)
def remove(a):
 if a in armed:g.bp(a,False);armed.remove(a)
def emit(row):r['events'].append(row);save()
try:
 command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 for a,s in sites.items():
  if s['initial']:arm(a)
 r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
 deadline=time.monotonic()+600;window=None
 for hit in range(2000):
  g.send('c');stopped=False
  while True:
   g.s.settimeout(2)
   try:reply=g.recv();break
   except TimeoutError:
    launch=out/'launch.json';returned=launch.exists() and any(v.get('dashboard_return') for v in read(launch).get('cycles',[]))
    if returned or time.monotonic()>=deadline or (window and time.monotonic()>=window):
     g.s.settimeout(5);reply=g.interrupt();r['status']='dashboard_without_complete_trace' if returned else 'capture_deadline';break
  stopped=True;g.s.settimeout(5)
  if r['status'] in ['dashboard_without_complete_trace','capture_deadline']:break
  regs=registers();a=regs['EIP'];assert a in sites,(hex(a),reply);s=sites[a];name=s['name'];assert g.read(a,len(bytes.fromhex(s['relocated']))).hex()==s['relocated']
  row=dict(index=len(r['events']),kind=name,utc=utc(),registers={n:hex(v) for n,v in regs.items()},**who());thread=int(row['thread'],16);r['last_stop']=row
  if name=='usage_call':
   assert active is None;args=struct.unpack('<3I',g.read(regs['ESP'],12));sl=g.read(args[1],36);assert sl[:2]==bytes([27,22]) and sl[4]==1 and u32(args[1]+8)==3
   loaded=module_list();r['module_list']=loaded;active=dict(thread=thread,frame=regs['EBP'],parameters=sl[4:20],file_object=sl[24:28]);window=time.monotonic()+120
   row.update(arguments=[hex(v) for v in args],stack_location=sl.hex(),device=device(args[0],27),call_pin=pin(a))
   for key,kind in [('dispatch_pointer_rva','dispatch'),('completion_pointer_rva','complete'),('free_pointer_rva','free')]:
    expected=next(v['address'] for v in review['sites'] if v['name']==kind);assert u32(K+review[key])==expected,(key,hex(u32(K+review[key])));arm(expected);pin(expected)
   emit(row)
  elif name=='dispatch':
   assert active;irp=regs['EDX'];slp=u32(irp+layout['irp_current_stack_location_offset'])-L['_IO_STACK_LOCATION']['size'];sl=g.read(slp,36)
   matching=sl[:2]==bytes([27,22]) and sl[4:20]==active['parameters']
   if irp in tracked or matching:
    if irp not in tracked:
     relation='original_file_object_match' if sl[24:28]==active['file_object'] else 'same_usage_parameters_only'
     tracked[irp]=dict(irp=hex(irp),relation=relation,freed=False);r['tracked_irps'].append(tracked[irp])
    assert not tracked[irp]['freed'],'Reused freed IRP pointer'
    ret=u32(regs['ESP']);pid=pin(ret);raw=r['runtime_pins'][pid]['resident']
    if ret in sites:assert sites[ret]['name']=='dispatch_return'
    else:sites[ret]=dict(name='dispatch_return',relocated=raw,pin=pid)
    call=dict(index=len(r['calls']),irp=hex(irp),thread=hex(thread),entry_stack=hex(regs['ESP']),return_address=hex(ret),return_pin=pid,returned=False)
    r['calls'].append(call);return_owners.setdefault(ret,[]).append(call);arm(ret)
    row.update(call_index=call['index'],request=snapshot(irp),stack_location=sl.hex(),device=device(regs['ECX'],sl[0]),relation=tracked[irp]['relation']);emit(row)
   else:r['ignored_hits'][name]=r['ignored_hits'].get(name,0)+1
  elif name=='dispatch_return':
   owners=return_owners[a];match=[v for v in owners if int(v['thread'],16)==thread and int(v['entry_stack'],16)+4==regs['ESP']];assert len(match)==1,'Unpaired dispatch return'
   call=match[0];owners.remove(call);call.update(returned=True,status=hex(regs['EAX']));row.update(call_index=call['index'],irp=call['irp'],status=hex(regs['EAX']),return_pin=call['return_pin']);emit(row)
  elif name in ['complete','free']:
   irp=regs['ECX'] if name=='complete' else u32(regs['ESP']+4)
   if irp in tracked:
    assert not tracked[irp]['freed'];row.update(request=snapshot(irp),caller=hex(u32(regs['ESP'])),caller_pin=pin(u32(regs['ESP'])),stack_words=[hex(v) for v in struct.unpack('<16I',g.read(regs['ESP'],64))]);emit(row)
    if name=='free':tracked[irp]['freed']=True
   else:r['ignored_hits'][name]=r['ignored_hits'].get(name,0)+1
  elif name=='usage_return':
   assert active and thread==active['thread'] and regs['EBP']==active['frame'];row.update(status=hex(regs['EAX']),return_pin=pin(a));emit(row);r['status']='usage_return_captured';break
  else:raise AssertionError(name)
  remove(a);assert g.ask('s').startswith(('T','S'))
  if name!='dispatch_return' or return_owners[a]:arm(a)
  if time.monotonic()>=deadline or (window and time.monotonic()>=window):r['status']='capture_deadline';break
 else:r['status']='hit_limit'
except Exception as exc:r.update(status='capture_incomplete',error=repr(exc))
finally:
 if g:
  try:
   if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
   for a in list(armed):remove(a)
   g.send('c');r['guest_resumed']=True
  except Exception as exc:r['resume_error']=repr(exc)
  g.s.close()
 elif stopped:command(4594,'cont')
 r.update(ended_utc=utc(),armed_breakpoints_remaining=[hex(a) for a in armed],unreturned_dispatches=sum(not v['returned'] for v in r['calls']));save();lock.close()
print(json.dumps({n:r[n] for n in ['status','error','guest_resumed','unreturned_dispatches','tracked_irps','ignored_hits'] if n in r},indent=2))
