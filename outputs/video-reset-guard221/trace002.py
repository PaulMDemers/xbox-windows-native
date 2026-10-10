"""Bounded actual guest reset/crash trace with host-seeded excluded-tail guard."""
import datetime,hashlib,json,re,socket,struct,sys,time,traceback
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['control002','candidate002'];out=k/case
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/reset221-runs/nt5-reset221-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
sys.path.insert(0,str(ws/'outputs/video-upload-address'));from discover_kernel import discover
code=(ws/'outputs/native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
review=read(k/'review.json');provider=review['providers'][case.replace('002','001')];symbols=provider['symbols']
kernel=ws/'outputs/video-upload-runtime211/artifacts/F/winnt/system32/ntoskrnl.exe';assert sha(kernel)==review['kernel_sha256'];kernel_pe=pefile.PE(str(kernel))
pub=read(ws/'outputs/native-windows-nt5-kernel/kernel-publics.json')['symbols']
binary=ws/'outputs/video-boot-layout219/artifacts/build001'/case.replace('002','001')/'xboxbvid.dll';assert sha(binary)==provider['sha256'];boot_pe=pefile.PE(str(binary))
trigger=k/'artifacts/trigger.sys';assert sha(trigger)==review['helpers']['trigger.sys']['sha256'];trigger_pe=pefile.PE(str(trigger))
r=dict(scope=__doc__,case=case,physical_access=False,ordinary_qualified=False,intentional_crash=True,host_seeded_guard=True,started_utc=utc(),events=[],pins=[],discovery_attempts=[],guard_checks=[],passed=False)
g=None;lock=None;stopped=False;armed=set();pairs={};B=None;K=None;frame=None;tail=None
def save():
 p=out/'trace.tmp';p.write_text(json.dumps(r,indent=2)+'\n');p.replace(out/'trace.json')
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def words(a,n):
 text=command(4594,'x /%dwx 0x%x'%(n,a));v=[]
 for line in text.replace('\r','').splitlines():
  if re.match(r'^(?:0x)?[0-9a-fA-F]+:\s+',line):v.extend(int(s,16) for s in re.findall(r'0x([0-9a-fA-F]{8})',line.split(':',1)[1]))
 assert len(v)==n,(hex(a),n,text[-100:]);return v
def hread(a,n):
 assert 0<n<=1024;aligned=a&~3;skip=a-aligned;count=(skip+n+3)//4
 return struct.pack('<%dI'%count,*words(aligned,count))[skip:skip+n]
def arm(a):
 if a not in armed:g.bp(a);armed.add(a)
def remove(a):
 if a in armed:g.bp(a,False);armed.remove(a)
def pin(a,pe,base,label,n=64):
 expected=pe.get_data(a-base,n);actual=g.read(a,n);assert actual==expected,(label,hex(a-base),'resident mismatch')
 row=dict(module=label,address=a,rva=a-base,bytes=n,sha256=hashlib.sha256(actual).hexdigest());r['pins'].append(row);return len(r['pins'])-1
def state():
 names=['_FrameBufferStart','_BackBuffer','_Owner','_References','_Ready']
 if '_BootWritableBytes' in symbols:names.append('_BootWritableBytes')
 return dict(globals={n:u32(B+symbols[n]) for n in names},published=list(struct.unpack('<11I',g.read(B+symbols['_Published'],44))))
def blob(a,n):return b''.join(g.read(a+i,min(1024,n-i)) for i in range(0,n,1024))
pattern=bytes(((i*73+(i>>8)*19+0x5b)&255) for i in range(0x15000))
def guard(label):
 actual=blob(tail,len(pattern));saved=blob(u32(B+symbols['_BackBuffer'])+640*480,640*14)
 raw=out/'artifacts'/('guard-'+label+'.bin');assert not raw.exists();raw.write_bytes(actual)
 saved_path=out/'artifacts'/('saved-row-'+label+'.bin');assert not saved_path.exists();saved_path.write_bytes(saved)
 row=dict(stage=label,tail_bytes=len(actual),tail_sha256=hashlib.sha256(actual).hexdigest(),guard_equal=actual==pattern,zero_tail=not any(actual),different_bytes=sum(a!=b for a,b in zip(actual,pattern)),saved_row_bytes=len(saved),saved_row_sha256=hashlib.sha256(saved).hexdigest(),saved_row_last64=saved[-64:].hex(),state=state())
 row.update(raw_guard_path=raw.name,raw_saved_row_path=saved_path.name)
 r['guard_checks'].append(row);return row
try:
 # NT5 is not running in the dashboard. Discover from live IDT only after launch.
 deadline=time.monotonic()+240
 while time.monotonic()<deadline:
  assert not (run/'cleanup.json').exists();temporary=acquire_monitor_lock(4594)
  try:
   K,discovery=discover(hread,command(4594,'info registers'),kernel_pe,pub);r['kernel_discovery']=discovery;break
  except Exception as exc:r['discovery_attempts'].append(dict(utc=utc(),error=repr(exc)));save()
  finally:temporary.close()
  time.sleep(2)
 else:raise RuntimeError('No actual pinned NT5 kernel before bounded deadline')
 lock=acquire_monitor_lock(4594);command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 # Revalidate stopped CPU's actual gates and kernel before planting code breakpoints.
 K,discovery=discover(g.read,command(4594,'info registers'),kernel_pe,pub);r['stopped_kernel_discovery']=discovery;kernel_pe.relocate_image(K)
 site=read(k/'kernel-site-review.json');assert site['call_target_rva']==pub[site['target_public']]['rva']
 bc=K+pub['_KeBugCheckEx@20']['rva'];render_done=K+site['rva'];pin(bc,kernel_pe,K,'ntoskrnl.exe');pin(render_done,kernel_pe,K,'ntoskrnl.exe',16)
 actual_call=g.read(render_done,5);assert actual_call==bytes.fromhex(site['bytes']) and render_done+5+struct.unpack('<i',actual_call[1:])[0]==K+site['call_target_rva'];arm(bc)
 r['status']='armed_actual_kernel';save();(out/'trace-armed.signal').touch(exist_ok=False)
 deadline=time.monotonic()+240;render_sites={};resets=set();strings=set();fills=set();completed=set()
 for hit in range(80):
  g.send('c');stopped=False
  while True:
   g.s.settimeout(2)
   try:reply=g.recv();break
   except TimeoutError:
    if time.monotonic()>=deadline:
     g.s.settimeout(5);g.interrupt();stopped=True
     raise TimeoutError('Bounded rendering capture timed out')
  stopped=True;g.s.settimeout(5)
  regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
  a=regs['EIP'];assert a in armed;thread=u32(0xffdff124);row=dict(index=len(r['events']),utc=utc(),registers=regs,thread=thread,irql=g.read(0xffdff024,1)[0]);r['events'].append(row)
  if a==bc:
   row['kind']='bugcheck_entry';row['arguments']=list(struct.unpack('<5I',g.read(regs['ESP']+4,20)))
   assert row['arguments']==[0xe058d221,0x44554d50,0x221,0x10000,1],row['arguments'];remove(bc)
   head=K+pub['_PsLoadedModuleList']['rva'];link=u32(head);seen=set();loaded=[];trigger_base=None
   while link!=head:
    assert link not in seen and len(seen)<128;seen.add(link);data=g.read(link,56);vals=struct.unpack('<14I',data);length=vals[11]&65535;maximum=vals[11]>>16;assert length<=maximum and length<=512 and not length%2
    name=g.read(vals[12],length).decode('utf-16le') if length else ''
    loaded.append(dict(name=name,base=vals[6],size=vals[8]))
    if name.lower()=='bootvid.dll':B=vals[6]
    if name.lower()=='trigger.sys':trigger_base=vals[6]
    link=vals[0]
   r['loaded_modules']=loaded;assert trigger_base is not None
   nt=u32(trigger_base+60);assert g.read(trigger_base,2)==b'MZ' and u32(trigger_base+nt+8)==trigger_pe.FILE_HEADER.TimeDateStamp and u32(trigger_base+nt+80)==trigger_pe.OPTIONAL_HEADER.SizeOfImage
   caller=u32(regs['ESP']);assert trigger_base<=caller<trigger_base+trigger_pe.OPTIONAL_HEADER.SizeOfImage
   trigger_pe.relocate_image(trigger_base);row['caller_pin']=pin(caller,trigger_pe,trigger_base,'trigger.sys',32);row['actual_trigger_sha256']=review['helpers']['trigger.sys']['sha256']
   assert B is not None and g.read(B,2)==b'MZ';nt=u32(B+60);assert u32(B+nt+8)==provider['timestamp'] and u32(B+nt+80)==provider['image_size'];boot_pe.relocate_image(B)
   r['boot_base']=B;r['before_seed']=state();frame=r['before_seed']['globals']['_FrameBufferStart'];back=r['before_seed']['globals']['_BackBuffer'];assert frame and frame%4096==0
   hidden=0x39dd00 if case=='candidate002' else 0x3b2d00;assert back-frame==hidden
   assert r['before_seed']['published']==[44,1,frame,0x03c00000,0x400000,1024*576*4,1024,576,4096,hidden,0]
   assert r['before_seed']['globals']['_Ready']==1 and r['before_seed']['globals']['_References']==1 and r['before_seed']['globals']['_Owner']
   if case=='candidate002':assert r['before_seed']['globals']['_BootWritableBytes']==0x3eb000
   r['indexed_end']=back+316160;r['tail_start']=tail=frame+0x3eb000
   assert r['indexed_end']==(tail if case=='candidate002' else frame+0x400000)
   pteaddr=0xc0000000+(tail>>12)*4;entries=words(pteaddr,21);assert entries==words(pteaddr,21)
   for i,pte in enumerate(entries):assert pte&1 and pte&16 and (pte&0xfffff000)==0x03feb000+i*4096
   r['tail_mapping']=dict(pte_address=pteaddr,ptes=entries,physical_start=0x03feb000,physical_end=0x04000000)
   for name,rv in [('ResetDisplay',symbols['_ResetDisplay']),('VidResetDisplay',provider['exports']['VidResetDisplay']),('VidSolidColorFill',provider['exports']['VidSolidColorFill']),('VidDisplayString',provider['exports']['VidDisplayString'])]:
    addr=B+rv;pin(addr,boot_pe,B,'bootvid.dll');render_sites[addr]=name;arm(addr)
   for i in range(0,len(pattern),1024):g.write(tail+i,pattern[i:i+1024])
   seeded=guard('seeded_at_intended_bugcheck');assert seeded['guard_equal'];r['guard_pattern_sha256']=hashlib.sha256(pattern).hexdigest();arm(render_done)
  elif a in render_sites:
   name=render_sites[a];row.update(kind='render_entry',function=name,state=state());row['argument_words']=list(struct.unpack('<5I',g.read(regs['ESP']+4,20)));remove(a)
   ret=u32(regs['ESP']);assert ret not in pairs;pin(ret,kernel_pe if K<=ret<K+kernel_pe.OPTIONAL_HEADER.SizeOfImage else boot_pe,K if K<=ret<K+kernel_pe.OPTIONAL_HEADER.SizeOfImage else B,'caller',16)
   # Private ResetDisplay is cdecl (argument is removed by caller); exported
   # NT5 exported reset wrapper takes no arguments (ret), other exports
   # use their actual reviewed stdcall parameter count.
   delta={'ResetDisplay':4,'VidResetDisplay':4,'VidDisplayString':8,'VidSolidColorFill':24}[name]
   pairs[ret]=dict(function=name,thread=thread,stack=regs['ESP'],delta=delta);row['return_pair']=pairs[ret];arm(ret)
  elif a in pairs:
   pair=pairs.pop(a);assert pair['thread']==thread and regs['ESP']==pair['stack']+pair['delta'],(pair,regs['ESP']);row.update(kind='render_return',function=pair['function'],return_pair=pair,state=state());remove(a);completed.add(pair['function'])
   if pair['function']=='ResetDisplay':
    row['guard']=guard('private_reset_return');assert row['guard']['guard_equal'] if case=='candidate002' else row['guard']['zero_tail']
   if pair['function']=='VidResetDisplay':row['guard']=guard('public_reset_return')
  elif a==render_done:
   row['kind']='crash_text_complete_before_callbacks';row['guard']=guard('crash_text_complete');remove(a)
   assert not pairs and {'ResetDisplay','VidResetDisplay','VidSolidColorFill','VidDisplayString'}<=completed,completed
   assert row['guard']['guard_equal'] if case=='candidate002' else not row['guard']['guard_equal']
   assert state()==r['before_seed'],'Published provider state changed';r.update(passed=True,status='reset_crash_guard_observed',completed_functions=sorted(completed));save();break
  save()
 else:raise RuntimeError('Bounded hit limit')
except BaseException as exc:r.update(error=repr(exc),status='preserved_trace_failure',host_traceback=traceback.format_exc());save()
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
