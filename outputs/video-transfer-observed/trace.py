"""Bounded read-only GDI route observation; pauses invalidate performance timing."""
import datetime,hashlib,json,socket,struct,sys,time,traceback
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='trace003'
out=k/case;run=ws/('work/runs/nt5-vobs-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
review=read(k/'sites.json');mods=review['modules'];K=review['kernel_base_expected'];L=read(k/'layouts.json')['structures']
for name,h in review['dependencies'].items():assert sha(ws/name)==h
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True
pes={name:pefile.PE(mod['path']) for name,mod in mods.items()}
for name,mod in mods.items():assert sha(Path(mod['path']))==mod['sha256']
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,started_utc=utc(),source_sha256=sha(Path(__file__)),sites_sha256=sha(k/'sites.json'),events=[],runtime_pins=[],calls=[],samples=[],ignored_stops=0)
inner_sites={};headers={};g=None;stopped=False;armed=set();sites={};loaded=[];active=None;pending=[];registered=False
marker=mods['probe.exe']['preferred_base']+mods['probe.exe']['exports']['XwnPhase']
lock=acquire_monitor_lock(4594)
def save():write_json(out/'trace.json',r)
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def field(t,n):return L[t]['fields'][n]['offset']
def uni(a):
 n,maximum,p=struct.unpack('<HHI',g.read(a,8));assert n<=maximum and n<=2048;return g.read(p,n).decode('utf-16le') if n else ''
def who():
 t=u32(0xffdff124);p=u32(t+review['thread_owner_offset']);return dict(thread=t,process=p,pid=u32(p+field('_EPROCESS','UniqueProcessId')),image=g.read(p+field('_EPROCESS','ImageFileName'),16).split(b'\0')[0].decode('ascii',errors='replace'))
def modules(process):
 head=K+review['module_list_rva'];q=u32(head);rows=[];seen=set()
 while q!=head:
  assert q and q not in seen and len(seen)<200;seen.add(q);node=q-field('_LDR_DATA_TABLE_ENTRY','InLoadOrderLinks')
  rows.append(dict(base=u32(node+field('_LDR_DATA_TABLE_ENTRY','DllBase')),size=u32(node+field('_LDR_DATA_TABLE_ENTRY','SizeOfImage')),name=uni(node+field('_LDR_DATA_TABLE_ENTRY','BaseDllName')).lower()));q=u32(q)
 peb=u32(process+field('_EPROCESS','Peb'));ldr=u32(peb+12);head=ldr+12;q=u32(head);seen=set()
 while q!=head:
  assert q and q not in seen and len(seen)<100;seen.add(q)
  rows.append(dict(base=u32(q+24),size=u32(q+32),name=uni(q+44).lower()));q=u32(q)
 return rows
def pin(a,n=16):
 m=next(v for v in loaded if v['base']<=a<v['base']+v['size']);name=m['name'];p=pes[name];base=m['base'];rva=a-base
 assert m['size']==((mods[name]['image_size']+4095)&~4095)
 if base not in headers:
  mz=g.read(base,2);nt=u32(base+60);stamp=u32(base+nt+8);assert mz==b'MZ' and stamp==mods[name]['timestamp']
  headers[base]=dict(base=base,module=name,mz=mz.hex(),nt_offset=nt,timestamp=stamp);r['module_header_identities']=list(headers.values())
 while True:
  rel=[e.rva-rva for b in getattr(p,'DIRECTORY_ENTRY_BASERELOC',[]) for e in b.entries if e.type==3 and rva<=e.rva<rva+n]
  end=max([n]+[o+4 for o in rel]);assert end<=64
  if n==end:break
  n=end
 raw=p.get_data(rva,n);assert len(raw)==n;data=bytearray(raw)
 for off in rel:struct.pack_into('<I',data,off,(struct.unpack_from('<I',data,off)[0]+base-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 actual=g.read(a,n);assert actual==data,(name,hex(rva),'resident mismatch')
 r['runtime_pins'].append(dict(address=a,base=base,rva=rva,module=name,source_sha256=mods[name]['sha256'],header_identity_base=base,raw=raw.hex(),resident=actual.hex(),relocations=rel));return len(r['runtime_pins'])-1
def arm(a):
 if a not in armed:g.bp(a);armed.add(a)
def remove(a):
 if a in armed:g.bp(a,False);armed.remove(a)
def add(a,name,args):
 assert a not in sites;sites[a]=dict(name=name,args=args,pin=pin(a));arm(a)
def surface(a):
 assert a;raw=g.read(a,52);v=struct.unpack('<12I2H',raw)
 result=dict(address=a,raw=raw.hex(),dhsurf=v[0],hsurf=v[1],dhpdev=v[2],hdev=v[3],width=v[4],height=v[5],cjBits=v[6],pvBits=v[7],pvScan0=v[8],stride=struct.unpack_from('<i',raw,36)[0],uniq=v[10],format=v[11],type=v[12],flags=v[13])
 assert result['format']==6 and result['type']==0 and 0<result['width']<=1024 and 0<result['height']<=576
 assert abs(result['stride'])>=result['width']*4 and abs(result['stride'])<=4096
 return result
def setup(owner):
 global loaded,registered
 loaded=modules(owner['process']);r['module_list']=loaded
 assert next(v for v in loaded if v['name']=='probe.exe')['base']==mods['probe.exe']['preferred_base']
 for name,args in [('BitBlt',9),('GdiFlush',0)]:
  base=next(v['base'] for v in loaded if v['name']=='gdi32.dll');add(base+mods['gdi32.dll']['exports'][name],name,args)
 wb=next(v['base'] for v in loaded if v['name']=='win32k.sys')
 for name,args in [('EngBitBlt',11),('EngCopyBits',6),('EngStretchBlt',11)]:add(wb+mods['win32k.sys']['exports'][name],name,args)
 desc=K+review['service_shadow_rva']+16;raw=g.read(desc,16);table,counts,limit,argument_table=struct.unpack('<4I',raw)
 r['service_descriptor']=dict(address=desc,raw=raw.hex(),table=table,limit=limit,argument_table=argument_table)
 for name,stub in review['stubs'].items():
  index=stub['service_number']&0xfff;assert index<limit
  address=u32(table+index*4);assert wb<=address<wb+mods['win32k.sys']['image_size']
  assert g.read(argument_table+index,1)[0]==stub['argument_count']*4
  add(address,name,stub['argument_count'])
 for rva in [0x26b09,0x26b80,0x26bfd,0x26c9a,0x26d47,0x26e60]:
  addr=wb+rva;ins=next(md.disasm(pes['win32k.sys'].get_data(rva,15),addr));assert ins.mnemonic=='call'
  inner_sites[addr]=dict(rva=rva,size=ins.size,raw=bytes(ins.bytes).hex(),operand=ins.op_str);pin(addr)
 registered=True
try:
 command(4594,'stop');stopped=True;g=Remote(4595)
 original_read=g.read
 def observed_read(address,length):
  try:return original_read(address,length)
  except Exception:
   r['failed_read']=dict(address=address,length=length,stack=traceback.format_stack(limit=8));raise
 g.read=observed_read
 r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 arm(marker);r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
 deadline=time.monotonic()+600
 for hit in range(512):
  g.send('c');stopped=False
  while True:
   g.s.settimeout(2)
   try:reply=g.recv();break
   except TimeoutError:
    launch=out/'launch.json';returned=launch.exists() and any(v.get('dashboard_return') for v in read(launch).get('cycles',[]))
    if returned or time.monotonic()>=deadline:
     g.s.settimeout(5);reply=g.interrupt();r['status']='dashboard_before_capture_complete' if returned else 'capture_deadline';break
  stopped=True;g.s.settimeout(5)
  if r['status'] in ['dashboard_before_capture_complete','capture_deadline']:break
  regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
  r['last_registers']=regs;save()
  a=regs['EIP'];assert a in armed,(hex(a),reply);owner=who();row=None
  if a==marker and owner['image'].lower()=='probe.exe':
   if not registered:setup(owner)
   marker_pin=pin(a);args=list(struct.unpack('<6I',g.read(regs['ESP']+4,24)));phase,size,kind,screen,memory,window=args
   assert size in [0,2] and kind in [1,3] and phase in [0,1,2]
   if phase==0:
    assert active is None and not pending
    active=dict(index=len(r['samples']),size=size,kind=kind,thread=owner['thread'],process=owner['process'],screen=screen,memory=memory,window=window,phase=0);r['samples'].append(active)
    for addr in list(sites)+list(inner_sites):arm(addr)
   else:
    assert active and active['size']==size and active['kind']==kind and active['thread']==owner['thread'] and active['phase']==phase-1 and not pending
    active['phase']=phase
   row=dict(kind='marker',arguments=args,pin=marker_pin,sample=active['index'])
   if phase==2:
    active['complete']=True;active=None
    for addr in list(armed):
     if addr!=marker:remove(addr)
    if len(r['samples'])==4:r['status']='four_routes_captured'
  elif active and owner['thread']==active['thread']:
   matches=[v for v in pending if v['return_address']==a and (v.get('expected_return_sp')==regs['ESP'] or (v.get('caller_ebp')==regs['EBP'] and 0<=regs['ESP']-v['stack']<=64))]
   if matches:
    assert len(matches)==1 and pending[-1] is matches[0];call=pending.pop();call.update(returned=True,result=regs['EAX']);row=dict(kind='return',call_index=call['index'],name=call['name'],sample=active['index'],phase=active['phase'],pin=pin(a))
    if a not in sites and a not in inner_sites and not any(v['return_address']==a for v in pending):remove(a)
   elif a in inner_sites:
    spec=inner_sites[a];ins=next(md.disasm(g.read(a,spec['size']),a));assert bytes(ins.bytes).hex()==spec['raw'] and pending and pending[-1]['name']=='EngCopyBits'
    op=ins.operands[0];mem_address=None
    if op.type==capstone.x86.X86_OP_IMM:target=op.imm
    elif op.type==capstone.x86.X86_OP_REG:target=regs[ins.reg_name(op.reg).upper()]
    else:
     assert op.type==capstone.x86.X86_OP_MEM and not op.mem.segment
     mem_address=(op.mem.disp+(regs[ins.reg_name(op.mem.base).upper()] if op.mem.base else 0)+(regs[ins.reg_name(op.mem.index).upper()]*op.mem.scale if op.mem.index else 0))&0xffffffff;target=u32(mem_address)
    ret=a+spec['size'];call=dict(index=len(r['calls']),name='copy_inner_'+hex(spec['rva']),sample=active['index'],phase=active['phase'],thread=owner['thread'],stack=regs['ESP'],caller_ebp=regs['EBP'],return_address=ret,returned=False,entry_pin=pin(a),return_pin=pin(ret),target=target,target_pin=pin(target,32),indirect_pointer_address=mem_address,stack_before=g.read(regs['ESP'],64).hex(),registers_before=regs)
    pending.append(call);r['calls'].append(call);arm(ret);row=dict(kind='entry',call_index=call['index'],name=call['name'],sample=active['index'],phase=active['phase'])
   elif a in sites:
    site=sites[a];args=list(struct.unpack('<'+'I'*site['args'],g.read(regs['ESP']+4,site['args']*4))) if site['args'] else []
    ret=u32(regs['ESP']);call=dict(index=len(r['calls']),name=site['name'],sample=active['index'],phase=active['phase'],thread=owner['thread'],stack=regs['ESP'],return_address=ret,expected_return_sp=regs['ESP']+4+site['args']*4,arguments=args,returned=False,entry_pin=pin(a),return_pin=pin(ret))
    if site['name'].startswith('Eng'):
     call['destination']=surface(args[0]);call['source']=surface(args[1]);rect_index=5 if site['name']=='EngBitBlt' else 4 if site['name']=='EngCopyBits' else 7
     call['rect_bytes']=g.read(args[rect_index],16).hex() if args[rect_index] else None
    pending.append(call);r['calls'].append(call);arm(ret);row=dict(kind='entry',call_index=call['index'],name=site['name'],sample=active['index'],phase=active['phase'])
   else:r['ignored_stops']+=1
  else:r['ignored_stops']+=1
  if row:row.update(utc=utc(),registers=regs,**owner);r['events'].append(row);save()
  if r['status']=='four_routes_captured':break
  still=a in armed
  if still:remove(a)
  assert g.ask('s').startswith(('T','S'))
  if still:arm(a)
  if time.monotonic()>=deadline:r['status']='capture_deadline';break
 else:r['status']='hit_limit'
except Exception as exc:r.update(status='capture_incomplete',error=repr(exc),exception_traceback=traceback.format_exc())
finally:
 if g:
  try:
   if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
   for a in list(armed):remove(a)
   g.send('c');r['guest_resumed']=True
  except Exception as exc:r['resume_error']=repr(exc)
  g.s.close()
 elif stopped:command(4594,'cont')
 r.update(ended_utc=utc(),pending_calls=len(pending),armed_breakpoints_remaining=list(armed));save();lock.close()
print(json.dumps({n:r[n] for n in ['status','error','pending_calls','guest_resumed'] if n in r},indent=2))
