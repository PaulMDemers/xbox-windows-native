"""Bounded read-only framebuffer mapping call/return and alias observation; no timing qualification."""
import datetime,hashlib,json,socket,struct,sys,time,traceback,re
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='trace001'
out=k/case;run=ws/('work/runs/nt5-vcache-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
mapreview=read(k/'map-sites.json')
for name,h in mapreview['dependencies'].items():assert sha(ws/name)==h
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
row_sites={};algorithm_sites={};row_watch=None;page_context=None;inner_sites={};headers={};g=None;stopped=False;armed=set();sites={};loaded=[];active=None;pending=[];registered=False
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
try:
 command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 apis={K+v['rva']:n for n,v in mapreview['modules']['ntoskrnl.exe']['functions'].items()}
 arm(marker)
 for address in apis:arm(address)
 r['mapping_calls']=[];r['mapping_returns']=[];r['mapping_stops']=0
 r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
 deadline=time.monotonic()+600
 g.send('c');stopped=False
 while True:
  g.s.settimeout(2)
  try:reply=g.recv()
  except TimeoutError:
   if time.monotonic()>=deadline:raise TimeoutError('mapping/marker deadline')
   continue
  stopped=True;g.s.settimeout(5)
  regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP','EFLAGS'],struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])))
  if regs['EIP']==marker:break
  r['mapping_stops']+=1
  assert r['mapping_stops']<=2048 and time.monotonic()<deadline,'bounded mapping trace'
  eip=regs['EIP'];esp=regs['ESP']
  if eip in apis:
   ret,lo,hi,length,cache=struct.unpack('<5I',g.read(esp,20))
   if hi==0 and lo in [0x03c00000,0xf3c00000] and length==0x400000:
    owner=who();thread=owner['thread']
    assert len(r['mapping_calls'])<16
    loaded=[dict(base=K,size=(mods['ntoskrnl.exe']['image_size']+4095)&~4095,name='ntoskrnl.exe')]
    entrypin=pin(eip)
    if lo==0x03c00000 and 'early_snapshot' not in r:
     text=command(4594,'info registers');cr={n:int(re.search(n+r'=([0-9a-fA-F]+)',text).group(1),16) for n in ['CR0','CR3','CR4']}
     raw=out/'artifacts/before-bootvid-map.ram';raw.parent.mkdir(exist_ok=True);assert not raw.exists()
     command(4594,'pmemsave 0 67108864 '+json.dumps(raw.resolve().as_posix()));assert raw.stat().st_size==67108864
     r['early_snapshot']=dict(path=str(raw.resolve()),sha256=sha(raw),control_registers=cr,entry=eip,owner=owner,scope='current root immediately before first direct-RAM framebuffer map')
    row=dict(id=len(r['mapping_calls']),api=apis[eip],entry=eip,thread=thread,esp=esp,return_address=ret,physical=lo,length=length,cache_type=cache,owner=owner,entry_pin=entrypin,caller_bytes=g.read(ret,16).hex())
    r['mapping_calls'].append(row);pending.append(row);arm(ret)
  elif eip in armed:
   owner=who();thread=owner['thread']
   matches=[v for v in pending if v['return_address']==eip and v['thread']==thread and v['esp']+20==esp]
   assert len(matches)<=1,'ambiguous frame pairing'
   if matches:
    row=matches[0];pending.remove(row)
    r['mapping_returns'].append(dict(call_id=row['id'],thread=thread,esp=esp,address=eip,value=regs['EAX'],caller_bytes=g.read(eip,16).hex()))
    if not any(v['return_address']==eip for v in pending):remove(eip)
   else:r['ignored_stops']+=1
  else:raise AssertionError(('unexpected stop',hex(eip),reply))
  save();g.send('c');stopped=False
 assert not pending,'mapping calls left unpaired'
 for address in list(armed):
  if address!=marker:remove(address)
 owner=who();assert regs['EIP']==marker and owner['image'].lower()=='probe.exe'
 args=list(struct.unpack('<6I',g.read(regs['ESP']+4,24)));assert args[:3]==[0,0,1]
 loaded=modules(owner['process']);r['module_list']=loaded
 assert next(v['base'] for v in loaded if v['name']=='probe.exe')==mods['probe.exe']['preferred_base']
 assert next(v['base'] for v in loaded if v['name']=='ntoskrnl.exe')==K
 pin(marker);pin(K+mods['ntoskrnl.exe']['exports']['memmove'])
 registers=command(4594,'info registers');control={n:int(re.search(n+r'=([0-9a-fA-F]+)',registers).group(1),16) for n in ['CR0','CR3','CR4']}
 assert control['CR0']&0x80000000 and not control['CR4']&0x20
 recursive=u32(0xc0300c00);assert recursive&0xfffff000==control['CR3']&0xfffff000
 raw=out/'artifacts/desktop.ram';raw.parent.mkdir(exist_ok=True);assert not raw.exists()
 command(4594,'pmemsave 0 67108864 '+json.dumps(raw.resolve().as_posix()))
 assert raw.stat().st_size==67108864
 r.update(status='desktop_snapshot_captured',registers=regs,control_registers=control,register_text=registers,owner=owner,marker_arguments=args,kernel_base=K,recursive_pde=recursive,private_memory=str(raw.resolve()),private_memory_sha256=sha(raw),snapshot_bytes=raw.stat().st_size)
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
 r.update(ended_utc=utc(),armed_breakpoints_remaining=list(armed));save();lock.close()
print(json.dumps({n:r[n] for n in ['status','error','guest_resumed'] if n in r},indent=2))
