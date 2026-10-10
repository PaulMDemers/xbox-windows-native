"""One bounded read-only executable-pinned Cromwell to FreeLdr handoff trace."""
import datetime,hashlib,json,re,socket,struct,sys,time,traceback
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='trace001'
out=k/case;run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/handoff225-runs/nt5-handoff225-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
iv=read(k/'inventory002.json');sites=iv['sites'];raw=ws/iv['binaries']['image-crom.bin']['path'];loader=ws/iv['binaries']['freeldr.sys']['path']
assert sha(raw)==iv['binaries']['image-crom.bin']['sha256'] and sha(loader)==iv['binaries']['freeldr.sys']['sha256']
raw=raw.read_bytes();loader=loader.read_bytes();regs_review=read(k.parent/'video-gpu-handoff216/model-inventory.json')['registers']
offsets=[v['offset'] for v in regs_review];names=[v['symbol'] for v in regs_review];assert len(offsets)==26 and len(set(offsets))==26
r=dict(scope=__doc__,case=case,debugger=True,physical_access=False,ordinary_qualified=False,gpu_ownership_qualified=False,debugger_memory_writes=False,started_utc=utc(),events=[],pins=[],passed=False)
g=None;lock=None;armed=set();stopped=False
def save():
 p=out/'trace.tmp';p.write_text(json.dumps(r,indent=2)+'\n');p.replace(out/'trace.json')
def blob(a,n):
 assert 0<n<=0x30000
 return b''.join(g.read(a+i,min(1024,n-i)) for i in range(0,n,1024))
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def arm(a):g.bp(a);armed.add(a)
def remove(a):g.bp(a,False);armed.remove(a)
def snapshot(label):
 values=[u32(0xfd000000+at) for at in offsets]
 row=dict(gpu_registers=dict(zip(names,values)),gpu_register_reads=len(values),artifacts=[])
 for name,a,n in [('ramin20k',0xfd710000,0x5000),('reserved_tail84k',0x03feb000,0x15000)]:
  data=blob(a,n);p=out/'artifacts'/(label+'-'+name+'.bin');assert not p.exists();p.write_bytes(data)
  row['artifacts'].append(dict(path=str(p.relative_to(ws)).replace('\\','/'),address=a,bytes=n,sha256=sha(p)))
 return row
def pin(a,label):
 if label=='freeldr_entry':expected=loader[a-iv['multiboot_header'][4]:a-iv['multiboot_header'][4]+64]
 else:expected=raw[a-0x03a00000:a-0x03a00000+64]
 actual=g.read(a,64);assert len(expected)==64 and actual==expected,(label,hex(a),'executing pin mismatch')
 r['pins'].append(dict(label=label,address=a,bytes=64,hex=actual.hex(),sha256=hashlib.sha256(actual).hexdigest()))
try:
 deadline=time.monotonic()+45
 while not (run/'startup-ready.json').exists():
  assert time.monotonic()<deadline and not (run/'cleanup.json').exists();time.sleep(.1)
 lock=acquire_monitor_lock(4594);command(4594,'stop');stopped=True
 g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 arm(sites['producer_exit_entry']);g.send('c');stopped=False;save();(out/'trace-armed.signal').touch(exist_ok=False)
 r['launch_barrier']='Breakpoints armed and CPU continued before launch observer is permitted to execute XBE'
 deadline=time.monotonic()+180;expected_order=list(sites)
 for label in expected_order:
  if label!='producer_exit_entry':g.send('c');stopped=False
  while True:
   g.s.settimeout(2)
   try:reply=g.recv();break
   except TimeoutError:
    if time.monotonic()>=deadline:
     g.s.settimeout(5);g.interrupt();stopped=True;raise TimeoutError('Bounded225 boot trace deadline')
  stopped=True;g.s.settimeout(5)
  vals=struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40]);regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP','EFL'],vals))
  a=regs['EIP'];assert a==sites[label],(label,hex(a));pin(a,label);remove(a)
  monitor=command(4594,'info registers');extra={n:int(v,16) for n,v in re.findall(r'\b(CR0|CR3|EFL)=([0-9a-fA-F]+)',monitor)}
  assert extra['CR0']&0x80000000==0,'Flat identity read prerequisite'
  row=dict(index=len(r['events']),label=label,utc=utc(),registers=regs,cpu=extra,stop_reply=reply,**snapshot(label));r['events'].append(row)
  if label=='producer_exit_entry':
   header=list(struct.unpack('<8I',g.read(regs['EAX'],32)));assert header==iv['multiboot_header']
   uploaded=blob(regs['EAX']-iv['multiboot_file_offset'],len(loader));assert uploaded==loader
   row['uploaded_loader_pin']=dict(address=regs['EAX']-iv['multiboot_file_offset'],bytes=len(uploaded),sha256=hashlib.sha256(uploaded).hexdigest())
  if label in ['interrupts_revoked','multiboot_transfer','freeldr_entry']:assert not regs['EFL']&0x200
  if label=='multiboot_transfer':
   assert regs['EAX']==0x2badb002 and u32(regs['ESP'])==sites['freeldr_entry']
   assert blob(0x200000,len(loader))==loader
   row['copied_loader_sha256']=hashlib.sha256(loader).hexdigest()
  if label in ['multiboot_transfer','freeldr_entry']:
   info=list(struct.unpack('<24I',g.read(regs['EBX'],96)));assert info[0]==0x43 and info[11]==48
   address=info[12];assert address==regs['EBX']+100
   # This launcher's count/size convention is preserved, not silently repaired.
   entries=list(struct.unpack('<12I',g.read(address-4,48)))
   assert entries==[24,0,0,0x3c00000,0,1,24,0x3c00000,0,0x400000,0,0]
   row['multiboot_info']=dict(address=regs['EBX'],words=info,mmap_storage_address=address-4,mmap_raw_words=entries)
   if label=='freeldr_entry':assert regs['EAX']==0x2badb002 and row['multiboot_info']==r['events'][-2]['multiboot_info']
  save()
  if label!='freeldr_entry':arm(sites[expected_order[expected_order.index(label)+1]])
 r.update(passed=True,status='five_actual_handoff_boundaries_observed');save()
except BaseException as exc:r.update(status='preserved_trace_failure',error=repr(exc),host_traceback=traceback.format_exc());save()
finally:
 if g:
  if not stopped:
   try:g.s.settimeout(5);g.interrupt();stopped=True
   except Exception as exc:r['interrupt_error']=repr(exc)
  if stopped:
   for a in list(armed):
    try:remove(a)
    except Exception as exc:r.setdefault('breakpoint_cleanup_errors',[]).append([hex(a),repr(exc)])
   try:g.send('c');stopped=False;r['guest_resumed']=True
   except Exception as exc:r['resume_error']=repr(exc)
  g.s.close()
 if lock:lock.close()
 r.update(remaining_breakpoints=sorted(armed),closed=True,closed_utc=utc());save();(out/'trace-finished.signal').touch(exist_ok=False)
print(json.dumps({n:r[n] for n in ['passed','status','closed','guest_resumed','error'] if n in r}))
