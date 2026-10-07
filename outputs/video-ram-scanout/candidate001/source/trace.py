"""Bounded physical-framebuffer oracle at twelve pinned probe boundaries."""
import datetime,hashlib,json,re,socket,struct,sys,time,traceback
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';run=ws/'work/runs/nt5-vrscan-candidate001'
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
old=k.parent/'video-shared-trace2';sites=read(old/'sites.json');L=read(old/'layouts.json')['structures'];K=sites['kernel_base_expected']
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
review=read(k/'pe-review.json');paths={'probe.exe':k/'artifacts/probe.exe','xwnram.dll':out/'artifacts/xwnram.dll','ntoskrnl.exe':Path(sites['modules']['ntoskrnl.exe']['path'])}
assert sha(paths['probe.exe'])==review['probe_sha256'] and sha(paths['xwnram.dll'])==review['display_sha256']
assert sha(paths['ntoskrnl.exe'])==sites['modules']['ntoskrnl.exe']['sha256']
pes={n:pefile.PE(str(p)) for n,p in paths.items()};probe=pes['probe.exe']
entry=next(e.address for e in probe.DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'XwnScanout');marker=probe.OPTIONAL_HEADER.ImageBase+entry
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),events=[],pins=[],
 dependencies={str(p.relative_to(ws)) if p.is_relative_to(ws) else str(p):sha(p) for p in [Path(__file__),old/'sites.json',old/'layouts.json',k.parent/'native-windows-nt5-kernel/trace-entry.py',*paths.values()]})
g=None;stopped=False;armed=set();loaded=[];lock=acquire_monitor_lock(4594)
def save():write_json(out/'trace.json',r)
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def field(t,n):return L[t]['fields'][n]['offset']
def uni(a):
 n,m,p=struct.unpack('<HHI',g.read(a,8));assert n<=m and n<=2048;return g.read(p,n).decode('utf-16le') if n else ''
def who():
 t=u32(0xffdff124);p=u32(t+sites['thread_owner_offset']);return dict(thread=t,process=p,image=g.read(p+field('_EPROCESS','ImageFileName'),16).split(b'\0')[0].decode('ascii',errors='replace'))
def modules(process):
 head=K+sites['module_list_rva'];q=u32(head);rows=[];seen=set()
 while q!=head:
  assert q and q not in seen and len(seen)<200;seen.add(q);n=q-field('_LDR_DATA_TABLE_ENTRY','InLoadOrderLinks')
  rows.append(dict(base=u32(n+field('_LDR_DATA_TABLE_ENTRY','DllBase')),size=u32(n+field('_LDR_DATA_TABLE_ENTRY','SizeOfImage')),name=uni(n+field('_LDR_DATA_TABLE_ENTRY','BaseDllName')).lower()));q=u32(q)
 peb=u32(process+field('_EPROCESS','Peb'));ldr=u32(peb+12);head=ldr+12;q=u32(head);seen=set()
 while q!=head:
  assert q and q not in seen and len(seen)<100;seen.add(q)
  rows.append(dict(base=u32(q+24),size=u32(q+32),name=uni(q+44).lower()));q=u32(q)
 return rows
def pin(name,rva,n=32):
 m=next(v for v in loaded if v['name']==name);p=pes[name];base=m['base'];assert m['size']==((p.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
 assert g.read(base,2)==b'MZ';nt=u32(base+60);assert nt<4096 and u32(base+nt+8)==p.FILE_HEADER.TimeDateStamp
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
 data=paths['xwnram.dll'].read_bytes();offset=p.FILE_HEADER.PointerToSymbolTable;count=p.FILE_HEADER.NumberOfSymbols;strings=offset+count*18;size=struct.unpack_from('<I',data,strings)[0];assert strings+size<=len(data)
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
expected_order=[(phase,size,kind) for size in [0,2] for kind in [1,3] for phase in [0,1,2]]
try:
 command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 g.bp(marker);armed.add(marker);r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
 deadline=time.monotonic()+600;g.send('c');stopped=False
 while len(r['events'])<12:
  g.s.settimeout(2)
  try:reply=g.recv()
  except TimeoutError:
   if time.monotonic()>=deadline:raise TimeoutError('600-second capture bound')
   continue
  stopped=True;g.s.settimeout(5)
  regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP','EFLAGS'],struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])))
  assert regs['EIP']==marker and time.monotonic()<deadline
  owner=who();assert owner['image'].lower()=='probe.exe'
  args=list(struct.unpack('<5I',g.read(regs['ESP']+4,20)));phase,size,kind,x,y=args
  assert tuple(args[:3])==expected_order[len(r['events'])]
  if not loaded:
   loaded=modules(owner['process']);r['loaded_modules']=loaded
   assert next(v for v in loaded if v['name']=='probe.exe')['base']==probe.OPTIONAL_HEADER.ImageBase
   symbols=coff_symbols(pes['xwnram.dll'])
   for label in ['XwnBitBlt','XwnCopyBits','XwnUpload','XwnDirectEscape','DrvMovePointer']:pin('xwnram.dll',symbols[label])
   pin('ntoskrnl.exe',sites['modules']['ntoskrnl.exe']['exports']['KeBugCheckEx'])
  pin('probe.exe',entry)
  w,h=[(64,64),(768,384)][size//2];delta=16 if kind==3 and phase else 0;x+=delta;y+=delta
  assert 0<=x<x+w<=1024 and 0<=y<y+h<=576 and not(x<=1000<x+w and y<=550<y+h)
  raw=out/'artifacts'/('frame-%02d.raw'%len(r['events']));assert not raw.exists()
  command(4594,'pmemsave 0x03c00000 2359296 '+json.dumps(raw.resolve().as_posix()));data=raw.read_bytes();assert len(data)==2359296
  bad=[];bad_count=0
  for yy in range(h):
   for xx in range(w):
    want=(((xx*13+yy*7)&255)<<16)|(((yy*11+xx*3)&255)<<8)|((xx*17+yy*19)&255)
    got=struct.unpack_from('<I',data,(y+yy)*4096+(x+xx)*4)[0]&0xffffff
    if got!=want:
     bad_count+=1
     if len(bad)<16:bad.append([xx,yy,want,got])
  r['events'].append(dict(args=args,owner=owner,rectangle=[x,y,w,h],physical_address=0x03c00000,pitch=4096,pixels=w*h,mismatches=bad_count,examples=bad,raw=raw.name,sha256=sha(raw)))
  save();assert not bad_count,'Independent physical framebuffer mismatch'
  g.bp(marker,False);armed.remove(marker)
  if len(r['events'])==12:break
  assert g.ask('s').startswith(('T','S'));g.bp(marker);armed.add(marker);g.send('c');stopped=False
 r['status']='twelve_physical_snapshots_match'
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
