"""Bounded read-only syscall buffer capture; owned debugger diagnostic, never ordinary validation."""
import datetime,hashlib,json,socket,struct,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002','003'];out=k/case;art=out/'artifacts';art.mkdir(parents=True,exist_ok=True)
run=ws/('work/runs/nt5-fatx-target-buffer-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
code=(ws/'outputs/native-windows-nt5-kernel/trace-entry.py').read_text();ns={}
exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
review=json.loads((k/'sites.json').read_text());sites={s['address']:s for s in review['sites']}
layout=json.loads((ws/'outputs/native-windows-nt5-kernel/process-layouts.json').read_text())['_EPROCESS']['fields']
owner_offset=json.loads((ws/'outputs/shutdown-popup-workload/site-review.json').read_text())['thread_owner_offset']
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),sites_sha256=hashlib.sha256((k/'sites.json').read_bytes()).hexdigest(),started_utc=utc(),events=[],write_entry_count=0,warning_entry_count=0,warning_return_count=0,warning_occurrence_return_count=0,hit_counts={})
g=None;armed=set();stopped=False;pending={};watched=set();lock=acquire_monitor_lock(4594)
def save(): (out/'trace.json').write_text(json.dumps(r,indent=2)+'\n')
def u32(p):return struct.unpack('<I',g.read(p,4))[0]
def read_buffer(p,n):
 assert 0<n<=8192 and 0x10000<=p and p+n<=0x80000000
 return b''.join(g.read(p+i,min(512,n-i)) for i in range(0,n,512))
try:
 command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 for a,s in sites.items():
  if s['name']=='NtWriteFile':g.bp(a);armed.add(a)
 r['retention']='Only matching warning buffers and return/handle events; other writes counted';r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
 deadline=time.monotonic()+720
 for hit in range(250000):
  if time.monotonic()>=deadline:r['status']='capture_deadline';break
  g.send('c');stopped=False;g.s.settimeout(max(1,deadline-time.monotonic()));
  while True:
   g.s.settimeout(2)
   try:reply=g.recv();break
   except TimeoutError:
    launch=out/'launch.json'
    returned=launch.exists() and any(v.get('dashboard_return') for v in json.loads(launch.read_text()).get('cycles',[]))
    if returned or time.monotonic()>=deadline:
     reply=g.interrupt();r['status']='dashboard_return_no_full_target' if returned else 'capture_deadline';break
  stopped=True;g.s.settimeout(5)
  if r['status'] in ['dashboard_return_no_full_target','capture_deadline']:break
  packet=bytes.fromhex(g.ask('g'));vals=struct.unpack('<9I',packet[:36]);regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],vals));address=regs['EIP'];assert address in sites,(reply,regs)
  site=sites[address];r['hit_counts'][site['name']]=r['hit_counts'].get(site['name'],0)+1;actual=g.read(address,len(bytes.fromhex(site['bytes']))).hex();assert actual==site['bytes'],('site mismatch',site['name'],actual)
  thread=u32(0xffdff124);process=u32(thread+owner_offset);pid=u32(process+layout['UniqueProcessId']['offset']);image=g.read(process+layout['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace')
  key=(thread,regs['ESP']);event=dict(index=len(r['events']),function=site['name'],utc=utc(),thread=hex(thread),process=hex(process),pid=pid,image=image,esp=hex(regs['ESP']))
  keep=False;finish=False
  if site['name']=='NtWriteFile':
   args=struct.unpack('<10I',g.read(regs['ESP'],40));r['write_entry_count']+=1
   event.update(caller=hex(args[0]),handle=hex(args[1]),buffer=hex(args[6]),length=args[7],iosb=hex(args[5]),byteoffset_pointer=hex(args[8]),apc_routine=hex(args[3]))
   try:
    event['byteoffset']=struct.unpack('<q',g.read(args[8],8))[0] if args[8] else None
    if 0<args[7]<=8192:
     data=read_buffer(args[6],args[7]);digest=hashlib.sha256(data).hexdigest();path=art/('buffer-'+digest+'.bin')
     event.update(buffer_sha256=digest,buffer_file=path.name,buffer_captured=True)
     warning=b'An unsigned or incorrectly signed driver (c:\\xwninf99\\xwnvideo.inf) was installed' in data
     event['target_warning']=warning;event['warning_occurrences']=data.count(b'An unsigned or incorrectly signed driver (c:\\xwninf99\\xwnvideo.inf) was installed')
     if warning:
      r['warning_entry_count']+=1;watched.add((process,args[1]))
      if not path.exists():path.write_bytes(data)
    else:event.update(buffer_captured=False,target_warning=False)
   except Exception as exc:event.update(buffer_error=repr(exc),target_warning=False)
   keep=event['target_warning']
   if 'buffer_error' in event:
    r['buffer_read_error_count']=r.get('buffer_read_error_count',0)+1
    if len(r.setdefault('buffer_error_examples',[]))<20:r['buffer_error_examples'].append(event)
   if event['target_warning']:
    if key in pending:r.setdefault('missed_target_returns',[]).append(pending.pop(key))
    pending[key]=dict(event_index=event['index'],iosb=args[5],warning=True,occurrences=event.get('warning_occurrences',0),handle=args[1])
  elif site['name']=='NtWriteFile_return':
   entry=pending.pop(key,None)
   if entry:
    event.update(entry_index=entry['event_index'],eax=hex(regs['EAX']))
    try:event['iosb_status'],event['iosb_information']=struct.unpack('<II',g.read(entry['iosb'],8))
    except Exception as exc:event['iosb_error']=repr(exc)
    if entry['warning']:r['warning_return_count']+=1;r['warning_occurrence_return_count']+=entry['occurrences']
    keep=True
   else:r['unpaired_returns']=r.get('unpaired_returns',0)+1
  elif site['name'] in ['NtFlushBuffersFile','NtClose']:
   args=struct.unpack('<'+'I'*(site['argc']+1),g.read(regs['ESP'],4*(site['argc']+1)))
   if (process,args[1]) in watched:
    keep=True;event.update(caller=hex(args[0]),handle=hex(args[1]))
    if site['name']=='NtClose':
     watched.remove((process,args[1]));finish=r['warning_occurrence_return_count']>=3
  if keep:r['events'].append(event)
  if keep or hit%1000==0:save()
  if r['warning_occurrence_return_count']>=3:r['status']='three_warning_occurrences_returned';save();break
  g.bp(address,False);armed.remove(address);assert g.ask('s').startswith(('T','S'))
  desired={a for a,s in sites.items() if s['name']=='NtWriteFile' or (s['name']=='NtWriteFile_return' and pending) or (s['name'] in ['NtFlushBuffersFile','NtClose'] and watched)}
  for a in list(armed-desired):g.bp(a,False);armed.remove(a)
  for a in desired-armed:g.bp(a);armed.add(a)
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
 r.update(ended_utc=utc(),pending_write_count=len(pending),armed_breakpoints_remaining=list(armed));save();lock.close()
print(json.dumps({name:r[name] for name in ['status','error','write_entry_count','warning_entry_count','warning_return_count','guest_resumed'] if name in r}))
