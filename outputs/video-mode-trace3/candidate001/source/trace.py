"""Bounded raw framebuffer oracle for color cursor, hidden, replacement and restoration."""
import datetime,hashlib,json,re,socket,struct,sys,time,traceback
from pathlib import Path
from atomic_json import write_json
from discover_kernel import discover
from protocol import fnv
from mode_observer import ModeObserver
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';run=ws/'work/runs/nt5-vmodetrace3-candidate001'
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
old=k.parent/'video-shared-trace2';sites=read(old/'sites.json');L=read(old/'layouts.json')['structures'];K=sites['kernel_base_expected']
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
review=read(k/'pe-review.json');paths={'kernel32.dll':Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/kernel32.dll'),'probe.exe':k/'artifacts/probe.exe','xwnown.dll':out/'artifacts/xwnown.dll','ntoskrnl.exe':Path(sites['modules']['ntoskrnl.exe']['path'])}
assert sha(paths['probe.exe'])==review['probe_sha256'] and sha(paths['xwnown.dll'])==review['display_sha256']
assert sha(paths['kernel32.dll'])==next(v for v in review['files'] if v['name']=='probe.exe')['targets']['kernel32.dll']
assert sha(paths['ntoskrnl.exe'])==sites['modules']['ntoskrnl.exe']['sha256']
paths['win32k.sys']=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/win32k.sys')
assert sha(paths['win32k.sys'])=='414cc2568ba7f11fa58490060c947477f44d6218e6c52e01deea1bbe8a364a92'
pes={n:pefile.PE(str(p)) for n,p in paths.items()};probe=pes['probe.exe']
startup=probe.OPTIONAL_HEADER.ImageBase+probe.OPTIONAL_HEADER.AddressOfEntryPoint
entry=next(e.address for e in probe.DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'XwnGdiShot');marker=probe.OPTIONAL_HEADER.ImageBase+entry
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),events=[],pins=[],
 dependencies={str(p.relative_to(ws)) if p.is_relative_to(ws) else str(p):sha(p) for p in [Path(__file__),k/'discover_kernel.py',k/'mode_observer.py',k.parent/'native-windows-nt5-kernel/kernel-publics.json',old/'sites.json',old/'layouts.json',k.parent/'native-windows-nt5-kernel/trace-entry.py',*paths.values()]})
cursor_entry=next(e.address for e in probe.DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'XwnCursorShot');cursor_marker=probe.OPTIONAL_HEADER.ImageBase+cursor_entry;r['cursor_events']=[]
mode_rva=next(e.address for e in probe.DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'XwnModeStage');mode_marker=probe.OPTIONAL_HEADER.ImageBase+mode_rva
g=None;stopped=False;armed=set();loaded=[];headers={};create_address=None;exit_address=None;create_return=None;lock=acquire_monitor_lock(4594)
def save():write_json(out/'trace.json',r)
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def field(t,n):return L[t]['fields'][n]['offset']
def uni(a):
 n,m,p=struct.unpack('<HHI',g.read(a,8));assert n<=m and n<=2048;return g.read(p,n).decode('utf-16le') if n else ''
def who():
 t=u32(0xffdff124);p=u32(t+sites['thread_owner_offset']);return dict(thread=t,process=p,image=g.read(p+field('_EPROCESS','ImageFileName'),16).split(b'\0')[0].decode('ascii',errors='replace'))
def step_observed():
 # A stop reply does not prove retirement. Keep removed entry breakpoint absent
 # and issue at most four real steps if the complete observed CPU/owner state
 # remains unchanged. Never skip, deduplicate a marker, or mutate guest registers.
 for attempt in range(4):
  before_regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP','EFLAGS'],struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])))
  before_owner=who();assert before_regs['EIP'] not in armed
  reply=g.ask('s')
  after_regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP','EFLAGS'],struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])))
  after_owner=who();unchanged=before_regs==after_regs and before_owner==after_owner
  rows=r.setdefault('single_steps',[]);assert len(rows)<512
  rows.append(dict(before=before_regs,before_owner=before_owner,reply=reply,after=after_regs,after_owner=after_owner,armed=sorted(armed),attempt=attempt,unchanged=unchanged))
  save();assert reply.startswith(('T','S'))
  if not unchanged:return reply
 raise RuntimeError('Four single-step replies without observed CPU/owner progress')

def modules(process):
 head=K+sites['module_list_rva'];q=u32(head);rows=[];seen=set()
 while q!=head:
  assert q and q not in seen and len(seen)<200;seen.add(q);n=q-field('_LDR_DATA_TABLE_ENTRY','InLoadOrderLinks')
  rows.append(dict(base=u32(n+field('_LDR_DATA_TABLE_ENTRY','DllBase')),size=u32(n+field('_LDR_DATA_TABLE_ENTRY','SizeOfImage')),name=uni(n+field('_LDR_DATA_TABLE_ENTRY','BaseDllName')).lower()));q=u32(q)
 if process is None:return rows
 peb=u32(process+field('_EPROCESS','Peb'));ldr=u32(peb+12);head=ldr+12;q=u32(head);seen=set()
 while q!=head:
  assert q and q not in seen and len(seen)<100;seen.add(q)
  rows.append(dict(base=u32(q+24),size=u32(q+32),name=uni(q+44).lower()));q=u32(q)
 return rows
def pin(name,rva,n=32):
 m=next(v for v in loaded if v['name']==name);p=pes[name];base=m['base'];assert m['size']==((p.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
 if name not in headers:
  try:
   assert g.read(base,2)==b'MZ';nt=u32(base+60);assert nt<4096 and u32(base+nt+8)==p.FILE_HEADER.TimeDateStamp
   headers[name]=dict(readable=True,base=base,timestamp=p.FILE_HEADER.TimeDateStamp)
  except AssertionError as exc:
   if name!='xwnown.dll' or str(exc)!='E14':raise
   headers[name]=dict(readable=False,base=base,reason='GDB E14 on header; identity instead requires loader base/size/name and exact relocated resident code. Cold PE hash retained.')
  r['module_header_observations']=headers

 while True:
  rel=[e.rva-rva for b in getattr(p,'DIRECTORY_ENTRY_BASERELOC',[]) for e in b.entries if e.type==3 and rva<=e.rva<rva+n]
  size=max([n]+[o+4 for o in rel]);assert size<=64
  if size==n:break
  n=size
 raw=p.get_data(rva,n);assert len(raw)==n;expected=bytearray(raw)
 for off in rel:struct.pack_into('<I',expected,off,(struct.unpack_from('<I',expected,off)[0]+base-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 actual=g.read(base+rva,n);assert actual==expected,(name,hex(rva),'resident mismatch')
 r['pins'].append(dict(module=name,base=base,rva=rva,raw=raw.hex(),resident=actual.hex(),relocations=rel,sha256=sha(paths[name])))
def coff_symbols(p):
 data=paths['xwnown.dll'].read_bytes();offset=p.FILE_HEADER.PointerToSymbolTable;count=p.FILE_HEADER.NumberOfSymbols;strings=offset+count*18;size=struct.unpack_from('<I',data,strings)[0];assert strings+size<=len(data)
 result={};i=0
 while i<count:
  at=offset+i*18;name=data[at:at+8];value,sec,typ,storage,aux=struct.unpack_from('<IhHBB',data,at+8);i+=1+aux
  if name[:4]==bytes(4):
   pos=struct.unpack('<I',name[4:])[0];assert 4<=pos<size;name=data[strings+pos:strings+size].split(b'\0')[0]
  else:name=name.split(b'\0')[0]
  if sec>0:result[name.decode().lstrip('_').split('@')[0]]=p.sections[sec-1].VirtualAddress+value
 return result
def remove():
 for a in list(armed):g.bp(a,False);armed.remove(a)
expected_order=list(range(26))
mode_observer=ModeObserver(globals(),mode_marker,mode_rva)
try:
 command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 g.bp(mode_marker);armed.add(mode_marker);g.bp(cursor_marker);armed.add(cursor_marker);g.bp(marker);armed.add(marker);g.bp(startup);armed.add(startup);r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
 deadline=time.monotonic()+600;g.send('c');stopped=False
 while len(r['events'])<26:
  g.s.settimeout(2)
  try:reply=g.recv()
  except TimeoutError:
   if time.monotonic()>=deadline:raise TimeoutError('600-second capture bound')
   continue
  stopped=True;g.s.settimeout(5)
  regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP','EFLAGS'],struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])))
  assert time.monotonic()<deadline
  owner=who()
  stops=r.setdefault('stop_sequence',[]);assert len(stops)<640
  stops.append(dict(owner=owner,registers=regs,armed=sorted(armed),cursor_count=len(r['cursor_events']),restored_count=len(r['events'])));save()
  if loaded and mode_observer.handle(regs,owner):
   stopped=False;continue
  if owner['image'].lower()!='probe.exe' or ('probe_entry' in r and owner['process']!=r['probe_entry']['owner']['process']):
   other=r.setdefault('other_process_hits',[]);other.append(dict(owner=owner,registers=regs));save();assert len(other)<=128
   address=regs['EIP'];assert address in armed
   g.bp(address,False);armed.remove(address);assert step_observed().startswith(('T','S'))
   g.bp(address);armed.add(address);g.send('c');stopped=False;continue
  if regs['EIP'] in [startup,create_address,exit_address,cursor_marker,marker]:
   current=regs['EIP']
   try:g.read(current,32)
   except AssertionError as exc:
    if str(exc)!='E14':raise
    retries=r.setdefault('entry_unreadable_observations',[])
    retries.append(dict(owner=owner,registers=regs,error='E14'));save();assert sum(e['registers']['EIP']==current for e in retries)<=3
    # Let the CPU take its real fault/step; do not skip code or force memory resident.
    g.bp(current,False);armed.remove(current);r['entry_step_reply']=step_observed()
    assert r['entry_step_reply'].startswith(('T','S'));g.bp(current);armed.add(current);save();g.send('c');stopped=False;continue

  if not loaded:
   K,discovery=discover(g.read,command(4594,'info registers'),pes['ntoskrnl.exe'],read(k.parent/'native-windows-nt5-kernel/kernel-publics.json')['symbols'])
   r['kernel_discovery']=discovery
   loaded=modules(owner['process']);r['loaded_modules']=loaded
   assert next(v for v in loaded if v['name']=='probe.exe')['base']==probe.OPTIONAL_HEADER.ImageBase
   symbols=coff_symbols(pes['xwnown.dll'])
   for label in ['XwnBitBlt','XwnCopyBits','XwnUpload','XwnDirectEscape','DrvMovePointer']:pin('xwnown.dll',symbols[label])
   sec=next(s for s in pes['xwnown.dll'].sections if s.Name.rstrip(b'\0')==b'.text')
   offset=0
   while offset<sec.Misc_VirtualSize:
    pin('xwnown.dll',sec.VirtualAddress+offset,min(48,sec.Misc_VirtualSize-offset));offset+=len(bytes.fromhex(r['pins'][-1]['raw']))
   r['display_text_identity']=dict(rva=sec.VirtualAddress,bytes=sec.Misc_VirtualSize,matched=True)
   pin('ntoskrnl.exe',sites['modules']['ntoskrnl.exe']['exports']['KeBugCheckEx'])
  address=regs['EIP']
  if address==startup:
   pin('probe.exe',probe.OPTIONAL_HEADER.AddressOfEntryPoint)
   r['probe_entry']=dict(owner=owner,registers=regs)
   base=next(v for v in loaded if v['name']=='kernel32.dll')['base']
   exports={e.name.decode():e.address for e in pes['kernel32.dll'].DIRECTORY_ENTRY_EXPORT.symbols if e.name}
   create_address=base+exports['CreateFileA'];exit_address=base+exports['ExitProcess']
   for address_to_arm in [create_address,exit_address]:g.bp(address_to_arm);armed.add(address_to_arm)
   g.bp(startup,False);armed.remove(startup);save();assert step_observed().startswith(('T','S'));g.send('c');stopped=False;continue
  if address==create_address:
   pin('kernel32.dll',exports['CreateFileA'])
   callargs=list(struct.unpack('<8I',g.read(regs['ESP'],32)))
   r['first_create']=dict(args=callargs,owner=owner,entry_esp=regs['ESP'])
   create_return=callargs[0];g.bp(create_return);armed.add(create_return)
   g.bp(create_address,False);armed.remove(create_address);save();assert step_observed().startswith(('T','S'));g.send('c');stopped=False;continue
  if address==create_return:
   assert owner['thread']==r['first_create']['owner']['thread'] and regs['ESP']==r['first_create']['entry_esp']+32
   name=bytearray()
   for offset in range(256):
    byte=g.read(r['first_create']['args'][1]+offset,1)
    if byte==b'\0':break
    name+=byte
   else:raise AssertionError('Unterminated CreateFileA path')
   r['first_create']['filename']=name.decode('ascii')
   segment_text=command(4594,'info registers');r['first_create']['segment_registers']=segment_text
   fs=re.search(r'FS\s*=([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',segment_text)
   if fs:
    teb=int(fs[2],16);assert 0x10000<=teb<0x80000000
    r['first_create']['teb']=teb;r['first_create']['teb_first256']=g.read(teb,256).hex()
   r['first_create']['return']=regs['EAX'];g.bp(create_return,False);armed.remove(create_return);save();assert step_observed().startswith(('T','S'));g.send('c');stopped=False;continue
  if address==exit_address:
   pin('kernel32.dll',exports['ExitProcess'])
   r['probe_exit']=dict(owner=owner,status=u32(regs['ESP']+4),registers=regs)
   raise RuntimeError('Probe exited before all26 markers')
  if address==cursor_marker:
   args=list(struct.unpack('<8I',g.read(regs['ESP']+4,32)));index,phase,reference,cx,cy,shape,digest,shown=args
   r['last_cursor_hit']=dict(args=args,owner=owner,registers=regs,expected_cursor=divmod(len(r['cursor_events']),3),expected_restored=len(r['events']));save()
   assert index==len(r['events']) and (index,phase)==divmod(len(r['cursor_events']),3) and index<26
   assert (cx,cy)==([80,0,380,170][index%4],[70,0,250,140][index%4])
   assert shape==(1-index%2 if phase==2 else index%2) and shown==int(phase!=1)
   assert 0x10000<=reference<reference+393216<0x80000000
   pin('probe.exe',cursor_entry)
   raw=out/'artifacts'/('cursor-frame-%02d-%d.raw'%(index,phase));assert not raw.exists()
   reply=command(4594,'pmemsave 0x03c00000 2359296 '+json.dumps(raw.resolve().as_posix()));r.setdefault('physical_capture_replies',[]).append(dict(path=raw.name,reply=reply));save();data=raw.read_bytes();assert len(data)==2359296
   hx,hy=([7,11] if shape==0 else [15,3])
   r['cursor_events'].append(dict(args=args,owner=owner,position=[cx,cy],hotspot=[hx,hy],pixels=98304,raw=raw.name,sha256=sha(raw),oracle='Pending exact cold ref%02d.rgb and runtime FNV digest'%index))
   save();g.bp(cursor_marker,False);armed.remove(cursor_marker);assert step_observed().startswith(('T','S'));g.bp(cursor_marker);armed.add(cursor_marker);g.send('c');stopped=False;continue
  r['last_restored_hit']=dict(address=address,registers=regs,owner=owner,expected_cursor_count=3*(len(r['events'])+1),cursor_count=len(r['cursor_events']));save()
  assert address==marker
  assert len(r['cursor_events'])==3*(len(r['events'])+1)
  args=list(struct.unpack('<8I',g.read(regs['ESP']+4,32)));index,reference,x,y,w,h,stride,digest=args
  assert index==expected_order[len(r['events'])] and (w,h,stride)==(384,256,1536)
  assert 0x10000<=reference<reference+h*stride<0x80000000
  pin('probe.exe',entry)
  assert 0<=x<x+w<=1024 and 0<=y<y+h<=576 and not(x<=1000<x+w and y<=550<y+h)
  raw=out/'artifacts'/('frame-%02d.raw'%len(r['events']));assert not raw.exists()
  reply=command(4594,'pmemsave 0x03c00000 2359296 '+json.dumps(raw.resolve().as_posix()));r.setdefault('physical_capture_replies',[]).append(dict(path=raw.name,reply=reply));save();data=raw.read_bytes();assert len(data)==2359296
  r['events'].append(dict(args=args,owner=owner,rectangle=[x,y,w,h],physical_address=0x03c00000,pitch=4096,pixels=w*h,raw=raw.name,sha256=sha(raw),oracle='Pending exact cold ref%02d.rgb and runtime FNV digest'%index))
  save() # Preserve all 26 outcomes, including mismatches; never waive them.
  g.bp(marker,False);armed.remove(marker)
  if len(r['events'])==26:break
  assert step_observed().startswith(('T','S'));g.bp(marker);armed.add(marker);g.send('c');stopped=False
 assert len(r['cursor_events'])==78 and len(r['mode_stages'])==3 and not mode_observer.pending
 r['mode_interval_complete']=True
 r['status']='104_snapshots_pending_cold_oracle'
except Exception as exc:r.update(status='capture_incomplete',error=repr(exc),exception_traceback=traceback.format_exc())
finally:
 if g:
  try:
   if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
   remove();g.send('c');r['guest_resumed']=True
  except Exception as exc:r['resume_error']=repr(exc)
  g.s.close()
 elif stopped:command(4594,'cont')
 r.update(ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),armed_breakpoints_remaining=list(armed));save();lock.close()
print(json.dumps({n:r[n] for n in ['status','error','guest_resumed'] if n in r},indent=2))
