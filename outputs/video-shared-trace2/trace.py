"""Bounded read-only framebuffer mapping call/return and alias observation; no timing qualification."""
import datetime,hashlib,json,socket,struct,sys,time,traceback,re
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='trace002'
out=k/case;run=ws/('work/runs/nt5-vsharetrace2-'+case)
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
def boot_module(ret):
 for base in range(ret&~4095,(ret&~4095)-0x20000,-4096):
  try:
   if g.read(base,2)!=b'MZ':continue
   nt=u32(base+60)
   if nt>4096 or u32(base+nt+8)!=mods['bootvid.dll']['timestamp']:continue
   size=u32(base+nt+80)
   assert size==mods['bootvid.dll']['image_size'] and base<=ret<base+size
   return dict(base=base,size=size,name='bootvid.dll')
  except (AssertionError,ValueError):continue
 raise AssertionError('Actual bootvid caller image not identified')

def view(a):return list(struct.unpack('<11I',g.read(a,44)))

try:
 command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 loaded=[dict(base=K,size=mods['ntoskrnl.exe']['image_size'],name='ntoskrnl.exe')]
 apis={}
 def register(a,name,argc):
  assert a not in apis;apis[a]=(name,argc);arm(a)
 for name in ['MmMapIoSpace','MmMapVideoDisplay']:register(K+mods['ntoskrnl.exe']['exports'][name],name,4)
 for name,n in [('InbvNotifyDisplayOwnershipLost',1),('InbvAcquireDisplayOwnership',0)]:register(K+mods['ntoskrnl.exe']['exports'][name],name,n)
 arm(marker);r.update(status='armed_before_launch',calls=[],returns=[],stops=0);save();(out/'trace-armed.signal').touch(exist_ok=False)
 deadline=time.monotonic()+600;g.send('c');stopped=False;boot=None
 while True:
  g.s.settimeout(2)
  try:reply=g.recv()
  except TimeoutError:
   if time.monotonic()>=deadline:raise TimeoutError('bounded shared-pointer trace deadline')
   continue
  stopped=True;g.s.settimeout(5)
  regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP','EFLAGS'],struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])))
  eip=regs['EIP'];esp=regs['ESP']
  r['events'].append(dict(eip=eip,esp=esp,eax=regs['EAX'],thread=who()['thread'],pending_ids=[c['id'] for c in pending]))
  if eip==marker:break
  r['stops']+=1;assert r['stops']<=2048 and time.monotonic()<deadline
  if eip in apis:
   name,argc=apis[eip];ret=u32(esp);args=list(struct.unpack('<'+'I'*argc,g.read(esp+4,argc*4))) if argc else []
   interested=True
   if name in ['MmMapIoSpace','MmMapVideoDisplay']:
    interested=args[1]==0 and args[0] in [0x03c00000,0xf3c00000] and args[2]==0x400000
    if interested and args[0]==0x03c00000 and boot is None:
     boot=boot_module(ret);loaded.append(boot);r['early_bootvid_module']=boot
     for label,n in [('XwnFbPublish',1),('XwnFbAcquire',2),('XwnFbRelease',2),('XwnFbReleaseOwner',1)]:
      rva=mods['bootvid.dll']['symbols']['_'+label+'@'+str(n*4)];register(boot['base']+rva,label,n)

   if name=='XwnFbAcquire' and K+mods['ntoskrnl.exe']['exports']['InbvCheckDisplayOwnership'] not in apis:
    register(K+mods['ntoskrnl.exe']['exports']['InbvCheckDisplayOwnership'],'InbvCheckDisplayOwnership',0)
   if interested:
    owner=who();assert len(r['calls'])<256
    row=dict(id=len(r['calls']),name=name,eip=eip,esp=esp,thread=owner['thread'],owner=owner,return_address=ret,argc=argc,args=args,entry_pin=pin(eip),caller=g.read(ret,16).hex())
    if name=='XwnFbPublish':row['view']=view(args[0])
    if name=='XwnFbAcquire':row['view']=view(args[1])
    r['calls'].append(row);pending.append(row);arm(ret)
  elif eip in armed:
   thread=who()['thread'];matches=[v for v in pending if v['return_address']==eip and v['thread']==thread and esp==v['esp']+4+4*v['argc']]
   assert len(matches)<=1
   if matches:
    call=matches[0];pending.remove(call)
    row=dict(call_id=call['id'],thread=thread,esp=esp,eip=eip,value=regs['EAX'],caller=g.read(eip,16).hex())
    if call['name']=='XwnFbAcquire':
     row['view']=view(call['args'][1]);remove(K+mods['ntoskrnl.exe']['exports']['InbvCheckDisplayOwnership'])
    r['returns'].append(row)
    if not any(v['return_address']==eip for v in pending):remove(eip)
   else:r['ignored_stops']+=1
  else:raise AssertionError(('unexpected stop',hex(eip),reply))
  save();rearm=eip in armed
  if rearm:remove(eip)
  assert g.ask('s').startswith(('T','S'))
  if rearm:arm(eip)
  g.send('c');stopped=False
 assert not pending,'unpaired call at drawing marker'
 for a in list(armed):
  if a!=marker:remove(a)
 owner=who();assert owner['image'].lower()=='probe.exe';args=list(struct.unpack('<6I',g.read(esp+4,24)));assert args[:3]==[0,0,1]
 loaded=modules(owner['process']);r['module_list']=loaded
 assert next(v for v in loaded if v['name']=='bootvid.dll')['base']==boot['base']
 pin(marker)
 for name in ['bootvid.dll','xboxvnt5.sys']:
  m=next(v for v in loaded if v['name']==name);sec=next(v for v in pes[name].sections if v.Name.rstrip(b'\0')==b'.text')
  # Pin complete resident text in relocation-safe windows, not only entry bytes.
  pos=0
  while pos<sec.Misc_VirtualSize:
   n=min(48,sec.Misc_VirtualSize-pos);idx=pin(m['base']+sec.VirtualAddress+pos,n);pos+=len(bytes.fromhex(r['runtime_pins'][idx]['raw']))
 symbols=mods['bootvid.dll']['symbols'];base=boot['base']
 r['provider_globals']={n:u32(base+symbols[n]) for n in ['_FrameBufferStart','_BackBuffer','_Owner','_References','_Ready']}
 r['published_view']=view(base+symbols['_Published'])
 registers=command(4594,'info registers');cr={n:int(re.search(n+r'=([0-9a-fA-F]+)',registers).group(1),16) for n in ['CR0','CR3','CR4']}
 assert cr['CR0']&0x80000000 and not cr['CR4']&0x20
 recursive=u32(0xc0300c00);assert recursive&0xfffff000==cr['CR3']&0xfffff000
 raw=out/'artifacts/desktop.ram';assert not raw.exists();command(4594,'pmemsave 0 67108864 '+json.dumps(raw.resolve().as_posix()));assert raw.stat().st_size==67108864
 r.update(status='desktop_snapshot_captured',registers=regs,control_registers=cr,owner=owner,marker_arguments=args,kernel_base=K,recursive_pde=recursive,private_memory=str(raw.resolve()),private_memory_sha256=sha(raw),snapshot_bytes=raw.stat().st_size)
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
print(json.dumps({n:r[n] for n in ['status','error','guest_resumed','stops'] if n in r},indent=2))
