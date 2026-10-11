"""ONE actual guest IRQ acknowledgement and two pinned loader entry stops."""
import datetime,ftplib,hashlib,json,os,re,socket,struct,sys,time,traceback
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='trace001'
out=k/case;run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/guest236-runs/nt5-guest236-'+case)
assert (run/'instance.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
sys.path.insert(0,str(k.parent/'gpu-reset-banner152'));from ftp_deadline import DeadlineFTP
sys.path.insert(0,str(ws/'work/python-packages'));import capstone
from parsing import span,after_write_instruction,journal_ack
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,debugger=True,physical_access=False,gpu_ownership_qualified=False,ordinary_qualified=False,debugger_memory_writes=False,debugger_register_writes=False,passed=False,dirty_surface_coverage=False,started_utc=utc(),monitor=[],events=[],gdb_requests=[])
g=None;lock=None;stopped=False;armed=[];quarantined=False
def save():
 p=out/'trace.tmp';p.write_text(json.dumps(r,indent=2)+'\n');p.replace(out/'trace.json')
def cmd(s):
 value=command(4594,s);r['monitor'].append(dict(utc=utc(),command=s,reply=value));save();return value
def ask(s):
 value=g.ask(s);r['gdb_requests'].append(dict(command=s,reply=value));save();return value
def regs():
 raw=bytes.fromhex(ask('g'));assert len(raw)>=40;return list(struct.unpack('<10I',raw[:40]))
def qom_path(tree):
 stack=[];found=[]
 for line in tree.splitlines():
  m=re.match(r'^(\s*)/([^ ]*) \(([^)]+)\)',line)
  if not m:continue
  level=len(m[1]);name=m[2]
  while stack and stack[-1][0]>=level:stack.pop()
  if name:stack.append((level,name))
  if m[3]=='nv2a':found.append('/'+'/'.join(v for _,v in stack))
 assert len(found)==1;return found[0]
def wait_dashboard(deadline):
 attempts=0
 while True:
  attempts+=1
  try:
   with DeadlineFTP(min(deadline,time.monotonic()+6)) as ftp:
    ftp.connect('127.0.0.1',4596,timeout=ftp.budget());ftp.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD'])
    return dict(utc=utc(),reply=ftp.sendcmd('NOOP'),attempts=attempts,physical_access=False)
  except ftplib.all_errors:
   if time.monotonic()>=deadline:raise
   time.sleep(min(.2,max(0,deadline-time.monotonic())))
def restore_physical_mode(remote,record):
 if not record.get('physical_mode_restore_required'):return True
 try:
  ok=remote.ask('Qqemu.PhyMemMode:0')=='OK' and remote.ask('qqemu.PhyMemMode')=='0';record['physical_mode_restored']=ok
  if ok:record['physical_read_mode']=False;record['physical_mode_restore_required']=False
  return ok
 except Exception as exc:record['physical_mode_restore_error']=repr(exc);record['physical_mode_restored']=False;return False
def arm(kind,address,n):
 item=(kind,address,n);armed.append(item);r['armed_debugger_points']=armed.copy();save()
 assert ask(f'Z{kind},{address:x},{n:x}')=='OK'
def remove(item):
 kind,address,n=item;assert ask(f'z{kind},{address:x},{n:x}')=='OK';armed.remove(item);r['armed_debugger_points']=armed.copy();save()
def continue_stop(seconds):
 global stopped
 assert stopped and time.monotonic()+seconds<=overall+1
 g.s.settimeout(seconds);g.send('c');stopped=False
 try:reply=g.recv();stopped=True;return reply
 except socket.timeout:
  g.s.settimeout(5);reply=g.interrupt();stopped=True;raise AssertionError('Bounded guest stop not reached: '+reply)
 finally:g.s.settimeout(5)
def resident(name,address,n):
 data=g.read(address,n);p=out/'artifacts'/(name+'.bin');p.write_bytes(data)
 return data,dict(address=address,bytes=n,sha256=sha(p),path=p.relative_to(ws).as_posix())
try:
 deadline=time.monotonic()+45
 while not (run/'startup-ready.json').exists():
  assert time.monotonic()<deadline and not (run/'cleanup.json').exists();time.sleep(.1)
 r['dashboard_barrier']=wait_dashboard(deadline);lock=acquire_monitor_lock(4594)
 cmd('stop');stopped=True;g=Remote(4595);r['features']=ask('qSupported');r['initial_stop']=ask('?')
 r['prior_physical_mode']=ask('qqemu.PhyMemMode');assert r['prior_physical_mode']=='0';r['physical_mode_restored']=True
 overall=time.monotonic()+60
 inventory=read(k/'inventory001.json');r['inventory_sha256']=sha(k/'inventory001.json');r['capstone_version']=capstone.__version__
 arm(2,0xfd400100,4);reply=continue_stop(5);assert re.search(r'(?<![ra])watch:fd400100;',reply),reply
 values=regs();eip=values[8];data,pin=resident('irq-post-write-code',eip-32,64)
 row=dict(name='guest_irq_write_completed',stop=reply,registers=values,post_write_eip=eip,code_pin=pin)
 candidates=after_write_instruction(data,eip-32,eip,values,capstone);row['writer_candidates']=candidates
 _,row['stack_pin']=resident('irq-stack',values[4],64)
 try:
  headers,row['kernel_header_pin']=resident('irq-kernel-headers',0x80010000,4096)
  row['kernel_mz']=headers[:2]==b'MZ'
 except Exception as e:row['kernel_header_read_error']=repr(e)
 dashboard=(k/'artifacts/inputs/dashboard.xbe').read_bytes()
 try:
  expected=span(dashboard,inventory['dashboard'],eip-32,64);row['dashboard_code_match']=expected==data
 except AssertionError:row['dashboard_code_match']=False
 row['binary_owner']='cold owned dashboard XBE' if row['dashboard_code_match'] else 'not established; resident bytes and owned firmware input only'
 r['events'].append(row);save();assert len(candidates)==1,'Writer decode not uniquely identified'
 assert candidates[0]['value']&0x100000,'Watched write did not acknowledge ERROR'
 remove((2,0xfd400100,4))
 path=qom_path(cmd('info qom-tree'));r['nv2a_qom_path']=path
 assert 'state=0' in cmd('qom-get '+path+' xwn-snapshot234-report')
 r['snapshot_request_may_be_accepted']=True;save();response=cmd('qom-set '+path+' xwn-snapshot234 true');assert 'Error' not in response,response
 deadline=time.monotonic()+8
 while True:
  report=cmd('qom-get '+path+' xwn-snapshot234-report');m=re.search(r'state=(\d+)',report);assert m,report;state=int(m[1])
  if state in [3,5]:break
  assert time.monotonic()<deadline;time.sleep(.025)
 assert state==3 and 'tuple_published=1' in report,'Worker snapshot timed out'
 r['wait_irq_snapshot']=dict(reply=report);save()
 r['completed_write_corroboration']=journal_ack(report,candidates[0]['value']);save()
 launcher=inventory['launcher'];freeldr=inventory['freeldr'];entry=launcher['entry'];mbentry=int(freeldr['entry_address'],16)
 arm(0,entry,1)
 # Trace, not supervisor, owns the one authorized loopback launch.
 row=dict(cycle=1,status='requesting',launch_requested_utc=utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe');r['loader_launch']=row;save()
 g.send('c');stopped=False
 with DeadlineFTP(time.monotonic()+6) as ftp:
  ftp.connect('127.0.0.1',4596,timeout=ftp.budget());ftp.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD'])
  row['reply']=ftp.sendcmd(row['command']);row['status']='accepted';save()
 g.s.settimeout(20)
 try:reply=g.recv();stopped=True
 except socket.timeout:g.s.settimeout(5);g.interrupt();stopped=True;raise AssertionError('XBE entry stop bound')
 finally:g.s.settimeout(5)
 values=regs();assert values[8]==entry,(reply,values)
 data,pin=resident('xbe-entry',entry,32);expected=span((k/'artifacts/inputs/xromwell.xbe').read_bytes(),launcher,entry,32)
 r['events'].append(dict(name='actual_xromwell_xbe_entry',stop=reply,registers=values,pin=pin,expected_sha256=hashlib.sha256(expected).hexdigest(),resident_bytes_match=data==expected));save();assert data==expected
 remove((0,entry,1));arm(0,mbentry,1);reply=continue_stop(20);values=regs();assert values[8]==mbentry,(reply,values)
 data,pin=resident('freeldr-multiboot-entry',mbentry,32);raw=(k/'artifacts/inputs/freeldr.sys').read_bytes();offset=mbentry-int(freeldr['staging_address'],16);expected=raw[offset:offset+32];assert len(expected)==32
 r['events'].append(dict(name='actual_freeldr_multiboot_entry',stop=reply,registers=values,pin=pin,expected_sha256=hashlib.sha256(expected).hexdigest(),resident_bytes_match=data==expected));save();assert data==expected
 remove((0,mbentry,1));r.update(passed=True,status='actual_guest_writer_and_loader_entries_observed');save()
except BaseException as exc:r.update(status='preserved_guest_trace_failure',error=repr(exc),host_traceback=traceback.format_exc());save()
finally:
 if g:
  if not stopped:
   try:g.s.settimeout(5);g.interrupt();stopped=True
   except Exception as exc:r['interrupt_error']=repr(exc);quarantined=True
  if stopped:
   for item in armed.copy():
    try:remove(item)
    except Exception as exc:r['point_cleanup_error']=repr(exc);quarantined=True
   try:
    if ask('qqemu.PhyMemMode')!='0':quarantined=True;r['physical_mode_restored']=False
   except Exception as exc:
    r['mode_verification_error']=repr(exc);r['physical_mode_restored']=False;quarantined=True
   if quarantined:
    r['guest_resumed']=False;r['quarantine_retained_until_owned_process_exit']=True
    try:cmd('quit')
    except Exception as exc:r['quit_reply_error']=repr(exc)
   else:
    try:g.send('c');stopped=False;r['guest_resumed']=True
    except Exception as exc:r['resume_error']=repr(exc)
  g.s.close()
 if lock:lock.close()
 r.update(remaining_breakpoints=armed.copy(),closed=True,closed_utc=utc());save();(out/'trace-finished.signal').touch(exist_ok=False)
print(json.dumps({n:r[n] for n in ['passed','status','guest_resumed','error'] if n in r}))
