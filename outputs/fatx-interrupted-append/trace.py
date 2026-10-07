"""Interrupt the owned guest after the exact suffix write completes, before prefix writeback."""
import datetime,hashlib,json,socket,struct,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002','003']
out=k/case;art=out/'artifacts';art.mkdir(parents=True,exist_ok=True)
run=ws/('work/runs/nt5-fatx-interrupted-append-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(ws/'outputs/native-windows-nt5-kernel/trace-entry.py').read_text();ns={}
exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
review=json.loads((k/'sites.json').read_text());layout_path=k.parent/'fatx-install-buffer/write-layouts.json'
sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(layout_path.read_bytes())==review['layouts_sha256']
L=json.loads(layout_path.read_text())['offsets'];pub=json.loads((k.parent/'native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols']
owner=json.loads((k.parent/'shutdown-popup-workload/site-review.json').read_text())['thread_owner_offset']
P=json.loads((k.parent/'native-windows-nt5-kernel/process-layouts.json').read_text())['_EPROCESS']['fields']
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,started_utc=utc(),source_sha256=sha(Path(__file__).read_bytes()),sites_sha256=sha((k/'sites.json').read_bytes()),events=[],hit_counts={})
control=k.parent/'fatx-paging-buffer/002'
control_al=json.loads((control/'alignment.json').read_text())
control_log=(control/'artifacts/after-setupapi.log').read_bytes()
assert sha(control_log)==control_al['after_sha256']
target=control_al['desired_offset'];split=target+111;end=target+220
expected=control_log[target:end];assert len(expected)==220 and split==270336
r.update(control_log_sha256=sha(control_log),target=target,split=split,expected_warning_sha256=sha(expected),interrupted_state=True)
checkpoint_length=109 if case=='001' else 1524
r['checkpoint_length']=checkpoint_length
prefix_seen=False;checkpoint=False
g=None;armed=set();fixed={};pending={};cache={};stopped=False;lock=acquire_monitor_lock(4594)
from atomic_json import write_json
r['atomic_json_source_sha256']=sha((k/'atomic_json.py').read_bytes())
def save():
 write_json(out/'trace.json',r)
def u32(p):return struct.unpack('<I',g.read(p,4))[0]
def i64(p):return struct.unpack('<q',g.read(p,8))[0]
def uni(p):
 n,m,b=struct.unpack('<HHI',g.read(p,8));assert n<=m and n<=2048 and not n%2
 return g.read(b,n).decode('utf-16le') if n else ''
def fileinfo(file):
 fcb=u32(file+L['file_fcb']);return fcb,uni(fcb+L['fcb_path'])
def buffer(row,p,n):
 row.update(buffer=hex(p),length=n)
 if not n:return
 if not p or n>65536:row['buffer_unobserved']='null or over65536-byte bound';return
 try:
  data=b''.join(g.read(p+i,min(512,n-i)) for i in range(0,n,512));digest=sha(data);dest=art/('buffer-'+digest+'.bin')
  if not dest.exists():dest.write_bytes(data)
  row.update(buffer_file=dest.name,buffer_sha256=digest)
 except Exception as exc:row['buffer_error']=repr(exc)
def who(thread):
 proc=u32(thread+owner)
 return dict(thread=hex(thread),process=hex(proc),pid=u32(proc+P['UniqueProcessId']['offset']),image=g.read(proc+P['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace'))
def discover():
 K=review['kernel_base_expected'];assert g.read(K,2)==b'MZ'
 pe=K+u32(K+60);assert g.read(pe,4)==b'PE\0\0' and u32(pe+8)==review['kernel_timestamp']
 head=K+pub['_PsLoadedModuleList']['rva'];link=u32(head);modules=[];seen=set()
 while link!=head:
  assert link not in seen and len(seen)<128;seen.add(link)
  modules.append(dict(name=uni(link+44),base=u32(link+24),size=u32(link+32)));link=u32(link)
 assert modules[0]['base']==K
 driver=next(v for v in modules if v['name'].lower()=='xwnfatx.sys');D=driver['base']
 for site in review['sites']:
  if site['name'].startswith('cache_'):continue
  b=bytearray.fromhex(site['bytes'])
  if 'relocation_offset' in site:struct.pack_into('<I',b,site['relocation_offset'],D+site['iat_rva'])
  a=D+site['rva'];assert g.read(a,len(b))==bytes(b)
  fixed[a]=dict(name=site['name'],bytes=bytes(b).hex())
 r.update(kernel_base=hex(K),driver=driver,modules=modules,disabled_sites=['cache_call','cache_return'])
try:
 command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 gate=review['ntwrite_gate']['address'];g.bp(gate);armed.add(gate)
 r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False);deadline=time.monotonic()+600
 last_saved_events=-1
 for hit in range(100000):
  g.send('c');stopped=False
  while True:
   g.s.settimeout(2)
   try:reply=g.recv();break
   except TimeoutError:
    launch=out/'launch.json';returned=launch.exists() and any(v.get('dashboard_return') for v in json.loads(launch.read_text()).get('cycles',[]))
    if returned or time.monotonic()>=deadline:
     g.s.settimeout(5);reply=g.interrupt();r['status']='dashboard_observed' if returned else 'capture_deadline';break
  stopped=True;g.s.settimeout(5)
  if r['status'] in ['dashboard_observed','capture_deadline']:break
  regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
  a=regs['EIP'];assert a in armed
  if a==gate:
   assert g.read(a,len(bytes.fromhex(review['ntwrite_gate']['bytes']))).hex()==review['ntwrite_gate']['bytes']
   discover();r['status']='driver_sites_armed';name='ntwrite_gate'
  else:
   thread=u32(0xffdff124);key=(thread,regs['ESP'],a)
   if a in fixed:
    site=fixed[a];name=site['name'];assert g.read(a,len(bytes.fromhex(site['bytes']))).hex()==site['bytes']
    if name=='write_entry':
     ptr=u32(regs['ESP']+4);ctx=u32(ptr);file=u32(ctx+L['context_file']);fcb,path=fileinfo(file)
     if path.lower().endswith('\\setupapi.log'):
      irp=u32(ctx+L['context_irp']);stack=u32(ctx+L['context_stack']);n=u32(stack+L['stack_length']);mdl=u32(irp+L['irp_mdl'])
      row=dict(index=len(r['events']),kind=name,utc=utc(),**who(thread),path=path,context=hex(ctx),file=hex(file),irp=hex(irp),flags=u32(irp+L['irp_flags']),byteoffset=i64(stack+L['stack_offset']),file_size_at_entry=i64(fcb+L['fcb_size']),mdl=hex(mdl))
      if mdl:
       flags=struct.unpack('<H',g.read(mdl+L['mdl_flags'],2))[0];p=u32(mdl+L['mdl_mapped']) if flags&5 else 0;row['mdl_flags']=flags
      else:p=u32(irp+L['irp_user_buffer'])
      buffer(row,p,n);r['events'].append(row)
      ret=u32(regs['ESP']);pending_key=(thread,regs['ESP']+4,ret);assert pending_key not in pending
      pending[pending_key]=dict(index=row['index'],irp=irp,context=ctx)
    elif name=='buffer_ready':
     ctx=u32(regs['EBP']-100);file=u32(ctx+L['context_file']);_,path=fileinfo(file)
     if path.lower().endswith('\\setupapi.log'):
      irp=u32(ctx+L['context_irp']);entries=[v for key,v in pending.items() if key[0]==thread and v['context']==ctx];assert len(entries)==1
      row=dict(index=len(r['events']),kind=name,utc=utc(),**who(thread),path=path,context=hex(ctx),file=hex(file),irp=hex(irp),flags=u32(irp+L['irp_flags']),byteoffset=i64(regs['EBP']-96),write_entry_index=entries[0]['index'])
      buffer(row,regs['EAX'],u32(regs['EBP']-124));r['events'].append(row)
      if row['byteoffset']<split and row['byteoffset']+row['length']>target:prefix_seen=True
      if row['byteoffset']==split and row['length']==checkpoint_length and row.get('buffer_file'):
       data=(art/row['buffer_file']).read_bytes()
       if data[:109]==expected[111:]:entries[0]['suffix_buffer_index']=row['index']
    elif name=='cache_call':
     file,offset,n,wait,p=struct.unpack('<5I',g.read(regs['ESP'],20));_,path=fileinfo(file)
     if path.lower().endswith('\\setupapi.log'):
      cachekey=(thread,regs['EBP']);assert cachekey not in cache
      row=dict(index=len(r['events']),kind=name,utc=utc(),**who(thread),path=path,file=hex(file),byteoffset=i64(offset),wait=wait)
      buffer(row,p,n);r['events'].append(row);cache[cachekey]=row['index']
    else:
     index=cache.pop((thread,regs['EBP']),None)
     if index is not None:r['events'].append(dict(index=len(r['events']),kind=name,utc=utc(),entry_index=index,returned_boolean=bool(regs['EAX']&255)))
   else:
    name='write_return';entry=pending.pop(key,None)
    if entry:
     row=dict(index=len(r['events']),kind=name,utc=utc(),entry_index=entry['index'],status=regs['EAX'])
     if regs['EAX']==0:row['iosb_information_before_dispatch_completion']=u32(entry['irp']+L['irp_status']+4)
     r['events'].append(row)
     if 'suffix_buffer_index' in entry and row['status']==0 and row.get('iosb_information_before_dispatch_completion')==checkpoint_length:
      assert not prefix_seen, 'Prefix already observed: do not claim an interrupted split'
      assert not pending and not cache, 'Other log writes are still pending'
      checkpoint=True
      r.update(status='suffix_completed_guest_stopped',checkpoint_return_index=row['index'],checkpoint_buffer_index=entry['suffix_buffer_index'],prefix_write_observed=False,checkpoint_registers=regs,checkpoint_utc=utc())
  r['hit_counts'][name]=r['hit_counts'].get(name,0)+1
  if hit%50==0 or len(r['events'])!=last_saved_events:save();last_saved_events=len(r['events'])
  if checkpoint:break
  g.bp(a,False);armed.remove(a);assert g.ask('s').startswith(('T','S'))
  desired=set(fixed)|{v[2] for v in pending}
  if not fixed:desired.add(gate)
  for a in list(armed-desired):g.bp(a,False);armed.remove(a)
  for a in desired-armed:g.bp(a);armed.add(a)
  if time.monotonic()>=deadline:r['status']='capture_deadline';break
 else:r['status']='hit_limit'
except Exception as exc:r.update(status='capture_incomplete',error=repr(exc))
finally:
 if g:
  try:
   if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
   for a in list(armed):g.bp(a,False);armed.remove(a)
   if checkpoint:
    # Do not step, continue, or detach. Keep GDB connected until HMP quit.
    r['monitor_status_before_exit']=command(4594,'info status')
    assert 'VM status: paused' in r['monitor_status_before_exit']
    r.update(guest_resumed=False,guest_held_stopped=True,exit_method='HMP quit with GDB attached and guest paused',quit_requested_utc=utc());save()
    try:r['quit_reply']=command(4594,'quit')
    except ConnectionResetError as exc:r['quit_monitor_disconnect']=repr(exc)
    except RuntimeError as exc:
     assert str(exc)=='Monitor disconnected';r['quit_monitor_disconnected']=True
   else:
    g.send('c');r['guest_resumed']=True
  except Exception as exc:r['resume_error']=repr(exc)
  g.s.close()
 elif stopped:command(4594,'cont')
 r.update(checkpoint_reached=checkpoint,ended_utc=utc(),pending_write_count=len(pending),pending_cache_count=len(cache),armed_breakpoints_remaining=list(armed));save();lock.close()
print(json.dumps({key:r[key] for key in ['status','error','hit_counts','guest_resumed'] if key in r}))
