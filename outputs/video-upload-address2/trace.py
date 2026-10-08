"""Bounded actual upload operands/pages/copy branch; no timing qualification."""
import datetime,hashlib,json,re,socket,struct,sys,time,traceback
from pathlib import Path
from atomic_json import write_json
from discover_kernel import discover
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';run=ws/'work/runs/nt5-vaddress2-candidate001'
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
old=k.parent/'video-shared-trace2';sites=read(old/'sites.json');L=read(old/'layouts.json')['structures'];K=sites['kernel_base_expected']
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
review=read(k/'pe-review.json');static=read(k/'sites.json')
paths={'probe.exe':k/'artifacts/probe.exe','xwnown.dll':Path(static['driver_path']),'ntoskrnl.exe':Path(sites['modules']['ntoskrnl.exe']['path'])}
assert sha(paths['probe.exe'])==review['probe_sha256'] and sha(paths['xwnown.dll'])==review['display_sha256']==static['driver_sha256']
assert sha(paths['ntoskrnl.exe'])==sites['modules']['ntoskrnl.exe']['sha256']
pes={n:pefile.PE(str(p)) for n,p in paths.items()};probe=pes['probe.exe']
entry=next(e.address for e in probe.DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'XwnAddressStage@8');marker=probe.OPTIONAL_HEADER.ImageBase+entry
r=dict(scope=__doc__,ordinary_qualified=False,physical_access=False,events=[],pins=[],samples=[],stop_sequence=[],dependencies={str(p):sha(p) for p in [Path(__file__),k/'discover_kernel.py',k/'sites.json',old/'sites.json',old/'layouts.json',k.parent/'native-windows-nt5-kernel/kernel-publics.json',k.parent/'native-windows-nt5-kernel/trace-entry.py',*paths.values()]})
g=None;stopped=False;armed=set();loaded=[];headers={};lock=acquire_monitor_lock(4594);active=None;bp={};pending=None

def save():write_json(out/'trace.json',r)
def arm(a):
 if a not in armed:g.bp(a);armed.add(a)
def remove(a):
 if a in armed:g.bp(a,False);armed.remove(a)

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
 # User loader list was unreadable in the preserved first attempt. Identify the
 # executing probe directly from its actual marker/header and relocated code.
 base=marker-entry;assert g.read(base,2)==b'MZ';nt=u32(base+60);assert nt<4096
 assert g.read(base+nt,4)==b'PE\0\0' and u32(base+nt+8)==probe.FILE_HEADER.TimeDateStamp
 assert u32(base+nt+80)==probe.OPTIONAL_HEADER.SizeOfImage
 rows.append(dict(base=base,size=probe.OPTIONAL_HEADER.SizeOfImage,name='probe.exe',identity='live marker/header/code; no user loader-list assumption'))

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

def context():
 text=command(4594,'info registers');cr={n:int(re.search(n+r'=([0-9a-fA-F]+)',text).group(1),16) for n in ['CR0','CR3','CR4']}
 assert cr['CR0']&0x80000000 and not cr['CR4']&0x20
 recursive=u32(0xc0300c00);assert recursive&1 and (recursive&0xfffff000)==(cr['CR3']&0xfffff000)
 return dict(registers=cr,raw=text,recursive_pde=recursive,limits='Raw paging bits only; effective memory type/PAT/MTRR not established')

def row_pages(base,rect,pitch):
 # Cache raw PDE/PTE pages at this stop: bounded full 96-row translation coverage.
 l,t,right,bottom=rect;pd={};pt={};rows=[]
 for y in range(t,bottom):
  points=[]
  for va in [base+y*pitch+l*4,base+y*pitch+right*4-1]:
   index=va>>22
   if index not in pd:pd[index]=u32(0xc0300000+index*4)
   pde=pd[index];assert pde&1
   item=dict(virtual=va,pde=pde,pde_address=0xc0300000+index*4)
   if pde&128:item.update(large=True,physical=(pde&0xffc00000)+(va&0x3fffff),pwt=bool(pde&8),pcd=bool(pde&16),pat=bool(pde&4096))
   else:
    page=0xc0000000+index*4096
    if page not in pt:pt[page]=g.read(page,4096)
    offset=((va>>12)&1023)*4;pte=struct.unpack_from('<I',pt[page],offset)[0];assert pte&1
    item.update(large=False,pte=pte,pte_address=page+offset,physical=(pte&0xfffff000)+(va&4095),pwt=bool(pte&8),pcd=bool(pte&16),pat=bool(pte&128))
   points.append(item)
  assert points[0]['virtual']//4096==points[1]['virtual']//4096
  rows.append(dict(y=y,points=points))
 return dict(base=base,rows=rows,tables=[dict(address=a,raw=data.hex()) for a,data in pt.items()])

def pdev(address):
 raw=g.read(address,136);o=static['pdev_offsets'];values={n:struct.unpack_from('<Q' if n=='ShadowBytes' else '<I',raw,off)[0] for n,off in o.items()}
 assert values['ScreenDelta']==4096
 return dict(address=address,raw=raw.hex(),**values)

try:
 command(4594,'stop');stopped=True;g=Remote(4595)
 original_read=g.read
 def read_observed(address,size):
  try:return original_read(address,size)
  except Exception:
   r['failed_read']=dict(address=address,size=size);raise
 g.read=read_observed;r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 arm(marker);r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
 deadline=time.monotonic()+600;g.send('c');stopped=False
 while True:
  g.s.settimeout(2)
  try:reply=g.recv()
  except TimeoutError:
   if time.monotonic()>=deadline:raise TimeoutError('600-second diagnostic bound')
   continue
  stopped=True;g.s.settimeout(5);regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP','EFLAGS'],struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])))
  assert time.monotonic()<deadline and len(r['stop_sequence'])<64
  owner=who();a=regs['EIP'];assert a in armed
  r['stop_sequence'].append(dict(registers=regs,owner=owner,armed=sorted(armed)))
  event=dict(address=a,registers=regs,owner=owner)
  if a==marker:
   sample,phase=struct.unpack('<2I',g.read(regs['ESP']+4,8));assert sample in [0,1,2] and phase in [0,1] and owner['image'].lower()=='probe.exe'
   if not loaded:
    K,discovery=discover(g.read,command(4594,'info registers'),pes['ntoskrnl.exe'],read(k.parent/'native-windows-nt5-kernel/kernel-publics.json')['symbols']);r['kernel_discovery']=discovery
    loaded=modules(owner['process']);r['loaded_modules']=loaded
    assert next(m for m in loaded if m['name']=='probe.exe')['base']==probe.OPTIONAL_HEADER.ImageBase
    base=next(m for m in loaded if m['name']=='xwnown.dll')['base'];bp={n:base+rv for n,rv in static['sites'].items()}
    symbols=coff_symbols(pes['xwnown.dll']);assert symbols['XwnUploadBox']==static['sites']['upload_entry'] and symbols['memmove']==static['sites']['memmove']
    for n,rv in static['sites'].items():pin('xwnown.dll',rv)
   pin('probe.exe',entry);event.update(kind='marker',sample=sample,phase=phase)
   if phase==0:
    assert active is None and sample==len(r['samples'])
    active=dict(sample=sample,thread=owner['thread'],process=owner['process'],context=context());r['samples'].append(active);arm(bp['upload_entry'])
   else:
    assert active and active['sample']==sample and active['thread']==owner['thread'] and active.get('returned') and pending is None
    active['complete']=True;active=None
    if sample==2:r['status']='three_uploads_captured'
  else:
   assert active and owner['thread']==active['thread'] and owner['process']==active['process']
   event['sample']=active['sample'];remove(a)
   if a==bp['upload_entry']:
    assert 'pdev' not in active;d=pdev(regs['EAX']);rect=list(struct.unpack('<4i',g.read(regs['EDX'],16)))
    expected=[[0,0,192,96],[128,0,320,96],[0,160,192,256]][active['sample']];assert rect==expected
    ret=u32(regs['ESP']);base=next(m for m in loaded if m['name']=='xwnown.dll')['base'];pin('xwnown.dll',ret-base)
    active.update(pdev=d,rect=rect,entry_stack=regs['ESP'],return_address=ret,
      source=row_pages(d['ShadowBits'],rect,d['ScreenDelta']),destination=row_pages(d['ScreenPtr'],rect,d['ScreenDelta']))
    pending=ret;arm(ret);arm(bp['copy_call']);event['kind']='upload_entry'
   elif a==bp['copy_call']:
    d=active['pdev'];l,t,right,bottom=active['rect'];args=list(struct.unpack('<3I',g.read(regs['ESP'],12)));dst,src,n=args
    assert regs['EDI']==d['address'] and args==[d['ScreenPtr']+t*4096+l*4,d['ShadowBits']+t*4096+l*4,(right-l)*4]
    active.update(copy_arguments=args,source_before=g.read(src,n).hex(),copy_stack=regs['ESP']);arm(bp['rep_movsd']);event['kind']='copy_call'
   elif a==bp['rep_movsd']:
    dst,src,n=active['copy_arguments'];assert regs['ESI']==src and regs['EDI']==dst and regs['ECX']==n//4 and not regs['EFLAGS']&0x400
    active['rep_before']=regs;arm(bp['after_rep']);event['kind']='rep_movsd'
   elif a==bp['after_rep']:
    dst,src,n=active['copy_arguments'];assert regs['ECX']==0 and regs['ESI']==src+n and regs['EDI']==dst+n
    actual=g.read(dst,n);assert actual.hex()==active['source_before'];active.update(rep_after=regs,destination_after=actual.hex());arm(bp['copy_return']);event['kind']='after_rep'
   elif a==bp['copy_return']:
    assert regs['ESP']==active['copy_stack'] and regs['EAX']==active['copy_arguments'][0]
    active['copy_returned']=True;event['kind']='copy_return'
   elif a==pending:
    assert regs['ESP']==active['entry_stack']+4 and active['copy_returned'];after=pdev(active['pdev']['address']);before=active['pdev']
    assert after['ShadowUploads']==before['ShadowUploads']+1 and after['ShadowBytes']==before['ShadowBytes']+73728
    active.update(pdev_after=after,returned=True);pending=None;event['kind']='upload_return'
   else:raise AssertionError('Unrecognized owned stop')
  r['events'].append(event);save()
  if r.get('status')=='three_uploads_captured':break
  if a in armed:
   remove(a);step_observed();arm(a)
  g.send('c');stopped=False
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
 r.update(ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pending=pending,armed_breakpoints_remaining=sorted(armed));save();lock.close()
print(json.dumps({n:r[n] for n in ['status','error','guest_resumed'] if n in r},indent=2))
