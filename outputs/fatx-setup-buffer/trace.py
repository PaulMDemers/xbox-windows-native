"""Capture only the reviewed SetupAPI string append routine in an owned emulator."""
import datetime,hashlib,json,socket,struct,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='001';out=k/case;art=out/'artifacts';art.mkdir(parents=True,exist_ok=True)
run=ws/('work/runs/nt5-fatx-setup-buffer-'+case);assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(ws/'outputs/native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
review=json.loads((k/'sites.json').read_text());sites={v['address']:v for v in review['sites']}
fields=json.loads((ws/'outputs/native-windows-nt5-kernel/process-layouts.json').read_text())['_EPROCESS']['fields'];owner_offset=json.loads((ws/'outputs/shutdown-popup-workload/site-review.json').read_text())['thread_owner_offset']
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();sha=lambda b:hashlib.sha256(b).hexdigest()
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,started_utc=utc(),source_sha256=sha(Path(__file__).read_bytes()),sites_sha256=sha((k/'sites.json').read_bytes()),records=[],hit_counts={},warning_flush_count=0)
g=None;armed=set();stopped=False;active={};lock=acquire_monitor_lock(4594)
def save():(out/'trace.json').write_text(json.dumps(r,indent=2)+'\n')
def u32(p):return struct.unpack('<I',g.read(p,4))[0]
try:
 command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 for a in sites:g.bp(a);armed.add(a)
 r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False);deadline=time.monotonic()+600
 for hit in range(2000):
  if time.monotonic()>=deadline:r['status']='capture_deadline';break
  g.send('c');stopped=False;g.s.settimeout(max(1,deadline-time.monotonic()));reply=g.recv();stopped=True;g.s.settimeout(5)
  vals=struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36]);regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],vals));a=regs['EIP'];assert a in sites,(reply,regs);site=sites[a]
  assert g.read(a,len(bytes.fromhex(site['bytes']))).hex()==site['bytes']
  r['hit_counts'][site['name']]=r['hit_counts'].get(site['name'],0)+1
  thread=u32(0xffdff124);process=u32(thread+owner_offset);key=(thread,regs['EBP']);name=site['name']
  if name=='seek_return':
   if key in active:r.setdefault('incomplete_records',[]).append(active[key]['index'])
   row=dict(index=len(r['records']),process=hex(process),thread=hex(thread),frame=hex(regs['EBP']),pid=u32(process+fields['UniqueProcessId']['offset']),image=g.read(process+fields['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace'),handle=hex(u32(regs['EBP']+8)),file_end=regs['EAX'],seek_utc=utc())
   r['records'].append(row);active[key]=row
  else:
   row=active.get(key)
   if row is None:r.setdefault('unpaired_hits',[]).append(dict(site=name,thread=hex(thread),frame=hex(regs['EBP']),utc=utc()))
   elif name=='write_call':
    args=struct.unpack('<5I',g.read(regs['ESP'],20));assert args[0]==int(row['handle'],16)
    n=args[2];assert 0<n<=8192 and 0x10000<=args[1] and args[1]+n<=0x80000000
    data=b''.join(g.read(args[1]+i,min(512,n-i)) for i in range(0,n,512));digest=sha(data);path=art/('buffer-'+digest+'.bin')
    if not path.exists():path.write_bytes(data)
    marker=b'An unsigned or incorrectly signed driver (c:\\xwninf99\\xwnvideo.inf) was installed'
    row.update(write_utc=utc(),buffer=hex(args[1]),length=n,bytes_written_pointer=hex(args[3]),overlapped=hex(args[4]),source_sha256=digest,buffer_file=path.name,warning_occurrences=data.count(marker))
   elif name=='write_return':row.update(write_return_utc=utc(),write_bool=regs['EAX'],bytes_written=u32(int(row['bytes_written_pointer'],16)))
   elif name=='flush_call':row.update(flush_called=True,flush_handle=hex(u32(regs['ESP'])),flush_call_utc=utc())
   elif name=='flush_return':
    if row.get('flush_called'):row.update(flush_bool=regs['EAX'],flush_return_utc=utc());r['warning_flush_count']+=row.get('warning_occurrences',0)
    else:row['flush_not_called']=True
    active.pop(key,None);save()
  if r['warning_flush_count']>=3:r['status']='three_warning_occurrences_flushed';break
  g.bp(a,False);armed.remove(a);assert g.ask('s').startswith(('T','S'));g.bp(a);armed.add(a)
 else:r['status']='hit_limit'
except Exception as exc:r.update(status='capture_incomplete',error=repr(exc))
finally:
 if g:
  try:
   if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
   for a in list(armed):g.bp(a,False);armed.remove(a)
   g.send('c');r['guest_resumed']=True
  except Exception as exc:
   r['resume_error']=repr(exc)
   try:command(4594,'cont');r['monitor_resumed']=True
   except Exception as err:r['monitor_resume_error']=repr(err)
  g.s.close()
 elif stopped:command(4594,'cont')
 r.update(ended_utc=utc(),active_records_remaining=[v['index'] for v in active.values()],armed_breakpoints_remaining=list(armed));save();lock.close()
print(json.dumps({key:r[key] for key in ['status','error','hit_counts','warning_flush_count','guest_resumed'] if key in r}))
