"""Observe Paint Win32 file calls with emulator breakpoints; no execution edits."""
import argparse,datetime,hashlib,json,pathlib,select,socket,struct,sys,time
k=pathlib.Path(__file__).resolve().parent;ws=k.parents[1]
sys.path[:0]=[str(ws/'work/python-packages'),str(k.parent/'native-windows-physical-mmcomplete'),str(k.parent/'native-windows-prebuild')]
import pefile
from debug_remote import Remote
from monitor_capture import command,acquire_monitor_lock
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
assert a.run=='nt5-paint-trace-001'
run=ws/'work/runs'/a.run;out=run/'paint-api-trace.json';assert not out.exists() and not (run/'cleanup.json').exists()
root=k.parent/'native-windows-physical-f/package/F/winnt/system32'
paint=pefile.PE(str(root/'mspaint.exe'));kernel=pefile.PE(str(root/'kernel32.dll'));mfc=pefile.PE(str(root/'mfc42u.dll'))
spec={'CreateFileW':7,'CreateFileA':7,'WriteFile':5,'FlushFileBuffers':1,'CloseHandle':1,'SetEndOfFile':1,'SetFilePointer':4}
points={kernel.OPTIONAL_HEADER.ImageBase+e.address:(e.name.decode(),spec[e.name.decode()],e.address) for e in kernel.DIRECTORY_ENTRY_EXPORT.symbols if e.name and e.name.decode() in spec}
entry=mfc.OPTIONAL_HEADER.ImageBase+0x550ab
result=dict(scope=__doc__,run=a.run,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),events=[],modules={},breakpoint_hits=0,completed=False,cleanup=False,
 limitations=['Breakpoints change scheduling; this is not unassisted timing evidence.','Paint context is matched by PE header identity, not a full live image hash.','Missed or unreturned calls remain explicit; no forced successful returns.'])
active=set();pending=[];g=None;stopped=False
def save():out.write_text(json.dumps(result,indent=2)+'\n')
def words(addr,n):return list(struct.unpack('<'+'I'*n,g.read(addr,n*4)))
def paint_context():
 try:
  base=paint.OPTIONAL_HEADER.ImageBase;off=words(base+60,1)[0]
  return off==paint.DOS_HEADER.e_lfanew and g.read(base+off,4)==b'PE\0\0' and words(base+off+8,1)[0]==paint.FILE_HEADER.TimeDateStamp and words(base+off+24+56,1)[0]==paint.OPTIONAL_HEADER.SizeOfImage
 except (ValueError,AssertionError):return False
def verify(label,pe,base,rva):
 try:actual=g.read(base+rva,12)
 except ValueError:
  result['unmapped_entry_stops']=result.get('unmapped_entry_stops',0)+1
  return False # xemu can stop before the instruction's demand-page fault.
 header=False
 try:off=words(base+60,1)[0]
 except ValueError:off=None
 if off is not None:
  assert off==pe.DOS_HEADER.e_lfanew
  assert words(base+off+8,1)[0]==pe.FILE_HEADER.TimeDateStamp
  assert words(base+off+24+56,1)[0]==pe.OPTIONAL_HEADER.SizeOfImage
  header=True
 expected=pe.get_data(rva,12);assert actual==expected,(label,hex(base+rva))
 result['modules'][label]=dict(base=hex(base),timestamp=pe.FILE_HEADER.TimeDateStamp,size=pe.OPTIONAL_HEADER.SizeOfImage,local_reference_sha256=hashlib.sha256(pe.__data__).hexdigest(),header_verified=header,executing_bytes_verified=12)
 return True
def string(ptr,wide):
 data=bytearray();step=2 if wide else 1
 for i in range(520):
  b=g.read(ptr+i*step,step)
  if b==bytes(step):break
  data+=b
 return data.decode('utf-16le' if wide else 'latin1',errors='replace')
def add(addr):
 if addr not in active:g.bp(addr);active.add(addr)
def remove(addr):
 if addr in active:g.bp(addr,False);active.remove(addr)
try:
 with acquire_monitor_lock(4594):command(4594,'stop')
 g=Remote(4595);g.ask('qSupported');g.ask('?');stopped=True
 for addr in [*points,entry]:add(addr)
 save();g.send('c');stopped=False;start=time.monotonic()
 while time.monotonic()-start<300 and result['breakpoint_hits']<20000:
  if (run/'trace-complete.signal').exists():result['stop_reason']='operator finished Save workload';break
  if not select.select([g.s],[],[],.5)[0]:continue
  if g.s.recv(1,socket.MSG_PEEK) in (b'+',b'-'):
   g.s.recv(1);continue
  reply=g.recv();stopped=True;regs=g.regs();pc=regs['eip'];result['breakpoint_hits']+=1
  own=paint_context()
  if own:
   for call in list(pending):
    if pc==call['return'] and regs['esp']==call['return_esp']:
     event=dict(kind='return',call_id=call['id'],api=call['api'],eax=regs['eax'],esp=regs['esp'])
     if call['api']=='WriteFile' and call['args'][3]:event['written']=words(call['args'][3],1)[0]
     result['events'].append(event);pending.remove(call)
     if pc not in points and pc!=entry and not any(c['return']==pc for c in pending):remove(pc)
   if pc in points and verify('kernel32',kernel,kernel.OPTIONAL_HEADER.ImageBase,points[pc][2]):
    name,n,rva=points[pc]
    stack=words(regs['esp'],n+1);args=stack[1:];event=dict(kind='entry',api=name,id=len(result['events']),pc=pc,esp=regs['esp'],args=args,return_address=stack[0])
    if name.startswith('CreateFile'):event['filename']=string(args[0],name.endswith('W'))
    if name=='WriteFile':event['prefix']=g.read(args[1],min(args[2],64)).hex() if args[2] else ''
    result['events'].append(event);call=dict(id=event['id'],api=name,args=args,return_esp=regs['esp']+4+n*4,**{'return':stack[0]});pending.append(call);add(stack[0])
   elif pc==entry and verify('mfc42u',mfc,mfc.OPTIONAL_HEADER.ImageBase,0x550ab):
    result['events'].append(dict(kind='mfc_write',pc=pc,stack=words(regs['esp'],3),object=regs['ecx'],handle=words(regs['ecx']+4,1)[0]))
   save()
  if pc not in active and pc not in points and pc!=entry:
   # A just-consumed dynamic return breakpoint was removed above.
   pass
  elif pc in active:
   remove(pc);g.send('s');g.recv()
   if pc in points or pc==entry or any(c['return']==pc for c in pending):add(pc)
  g.send('c');stopped=False
 else:result['stop_reason']='time or breakpoint bound reached'
 result['pending_calls']=pending;result['completed']=not pending and result.get('stop_reason')=='operator finished Save workload'
except Exception as e:
 result['error']=repr(e);raise
finally:
 if g:
  try:
   if not stopped:g.s.sendall(b'\x03');g.recv();stopped=True
   for addr in list(active):remove(addr)
   g.send('c');stopped=False;result['cleanup']=True
  finally:g.s.close()
 save()
print('Trace:',len(result['events']),'events;',result.get('stop_reason'),'cleanup',result['cleanup'])
