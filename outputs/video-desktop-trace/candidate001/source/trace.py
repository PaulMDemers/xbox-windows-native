"""Bounded raw framebuffer oracle for color cursor, hidden, replacement and restoration."""
import datetime,hashlib,json,re,socket,struct,sys,time,traceback
from pathlib import Path
from atomic_json import write_json
from discover_kernel import discover
from protocol import fnv
from desktop_observer import DesktopObserver
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';run=ws/'work/runs/nt5-vdesktrace-candidate001'
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
old=k.parent/'video-shared-trace2';sites=read(old/'sites.json');L=read(old/'layouts.json')['structures'];K=sites['kernel_base_expected']
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
review=read(k/'pe-review.json');paths={'kernel32.dll':Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/kernel32.dll'),'probe.exe':k/'artifacts/probe.exe','xwnown.dll':k.parent/'video-mode-reset/candidate001/artifacts/xwnown.dll','ntoskrnl.exe':Path(sites['modules']['ntoskrnl.exe']['path'])}
assert sha(paths['probe.exe'])==review['probe_sha256'] and sha(paths['xwnown.dll'])==review['display_sha256']
assert sha(paths['kernel32.dll'])==next(v for v in review['files'] if v['name']=='probe.exe')['targets']['kernel32.dll']
assert sha(paths['ntoskrnl.exe'])==sites['modules']['ntoskrnl.exe']['sha256']
paths['win32k.sys']=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/win32k.sys')
assert sha(paths['win32k.sys'])=='414cc2568ba7f11fa58490060c947477f44d6218e6c52e01deea1bbe8a364a92'
pes={n:pefile.PE(str(p)) for n,p in paths.items()};probe=pes['probe.exe']
startup=probe.OPTIONAL_HEADER.ImageBase+probe.OPTIONAL_HEADER.AddressOfEntryPoint
entry=next(e.address for e in probe.DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'XwnDesktopStage');marker=probe.OPTIONAL_HEADER.ImageBase+entry
r=dict(scope='Bounded supported desktop interval; real driver callbacks and ownership identity',physical_access=False,ordinary_qualified=False,events=[],pins=[],stop_sequence=[],dependencies={str(p):sha(p) for p in [Path(__file__),k/'desktop_observer.py',k/'discover_kernel.py',old/'sites.json',old/'layouts.json',*paths.values()]})
g=None;stopped=False;armed=set();loaded=[];headers={};lock=acquire_monitor_lock(4594)
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
observer=DesktopObserver(globals(),marker,entry)
try:
 command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 for address in [startup,marker]:g.bp(address);armed.add(address)
 r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
 deadline=time.monotonic()+600;g.send('c');stopped=False
 while len(r.get('desktop_stages',[]))<15:
  g.s.settimeout(2)
  try:reply=g.recv()
  except TimeoutError:
   if time.monotonic()>=deadline:raise TimeoutError('600-second bounded desktop capture')
   continue
  stopped=True;g.s.settimeout(5);regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP','EFLAGS'],struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])))
  assert time.monotonic()<deadline;owner=who();assert len(r['stop_sequence'])<384
  r['stop_sequence'].append(dict(owner=owner,registers=regs,armed=sorted(armed)));save();a=regs['EIP'];assert a in armed
  try:g.read(a,32)
  except AssertionError as exc:
   if str(exc)!='E14':raise
   rows=r.setdefault('entry_unreadable',[]);rows.append(dict(owner=owner,registers=regs));save();assert sum(v['registers']['EIP']==a for v in rows)<=3
   g.bp(a,False);armed.remove(a);assert step_observed().startswith(('T','S'));g.bp(a);armed.add(a);g.send('c');stopped=False;continue
  if loaded and (a!=marker or owner==r['probe_entry']['owner']) and observer.handle(regs,owner):stopped=False;continue
  if owner['image'].lower()!='probe.exe' or ('probe_entry' in r and owner['process']!=r['probe_entry']['owner']['process']):
   rows=r.setdefault('foreign_hits',[]);rows.append(dict(owner=owner,registers=regs));save();assert len(rows)<=64
   g.bp(a,False);armed.remove(a);assert step_observed().startswith(('T','S'));g.bp(a);armed.add(a);g.send('c');stopped=False;continue
  assert a==startup and not loaded
  K,discovery=discover(g.read,command(4594,'info registers'),pes['ntoskrnl.exe'],read(k.parent/'native-windows-nt5-kernel/kernel-publics.json')['symbols']);r['kernel_discovery']=discovery
  loaded=modules(owner['process']);r['loaded_modules']=loaded;assert next(v for v in loaded if v['name']=='probe.exe')['base']==probe.OPTIONAL_HEADER.ImageBase
  pin('probe.exe',probe.OPTIONAL_HEADER.AddressOfEntryPoint);r['probe_entry']=dict(owner=owner,registers=regs)
  g.bp(a,False);armed.remove(a);save();assert step_observed().startswith(('T','S'));g.send('c');stopped=False
 assert len(observer.stages)==15 and not observer.pending and not observer.active
 r['status']='desktop_intervals_complete';r['intervals_complete']=True
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
