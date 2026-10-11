"""Single bounded five-checkpoint renderer diagnostic; never a physical/ordinary run."""
import importlib.util,ast,datetime,ftplib,hashlib,json,os,re,socket,struct,sys,time,traceback
from pathlib import Path
from atomic_json import write_json
from attest import Attestor,translate32
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'emu001'
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/ledger266/runs/nt5-ledger266-emu001')
assert (run/'instance.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
sys.path.insert(0,str(k.parent/'gpu-reset-banner152'));from ftp_deadline import DeadlineFTP
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
plan=json.loads((k/'attestation-inputs001.json').read_text());pes={}
for name,m in plan['modules'].items():
 p=ws/m['path'];assert sha(p)==m['sha256'];pes[name]=pefile.PE(str(p))
tree=ast.parse((k.parent/'native-windows-prebuild/launch_unleashx.py').read_text())
login=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='login')
for name,arg in zip(['XWN_EMULATOR_FTP_USER','XWN_EMULATOR_FTP_PASSWORD'],login.args):os.environ.setdefault(name,ast.literal_eval(arg))
r=dict(passed=False,debugger=True,physical_access=False,ordinary_qualified=False,native_gpu_ownership=False,
 started_utc=utc(),monitor=[],checkpoints=[],points=[],physical_reads=[],guest_memory_writes=False,guest_register_writes=False)
spec=importlib.util.spec_from_file_location('discovery',k/'kernel-discovery.py');discovery=importlib.util.module_from_spec(spec);spec.loader.exec_module(discovery)
symbols=json.loads((ws/'outputs/native-windows-nt5-kernel/kernel-publics.json').read_text());assert symbols['pdb_sha256']==plan['pdb_sha256']
trap_rvas={0:symbols['symbols']['_KiTrap00']['rva'],14:symbols['symbols']['_KiTrap0E']['rva']}
g=None;lock=None;stopped=False;point=False;frontend=False;reopened=False;path=None;physical_mode=False
checkpoint=plan['modules']['probe.exe']['preferred_base']+plan['checkpoint_rva']
def save():
 write_json(out/'trace.json',r)
def cmd(text):
 reply=command(4594,text);r['monitor'].append(dict(utc=utc(),command=text,reply=reply));save();return reply
def capture_pages(kind,report):
 pages=getnum(report,'pages');assert 0<pages<=704
 folder=out/(kind+'-pages');folder.mkdir(exist_ok=False)
 manifest=[];deadline=time.monotonic()+120
 prop='xwn-'+('ui265' if kind=='ui' else 'ledger265')+'-page'
 for page in range(pages):
  assert time.monotonic()<deadline
  response=command(4594,'qom-set -j '+path+' '+prop+' '+json.dumps(str(page)))
  assert 'Error' not in response
  reply=command(4594,'qom-get '+path+' '+prop)
  assert getnum(reply,'page')==page and getnum(reply,'pages')==pages and getnum(reply,'epoch')==1
  file=folder/(str(page).zfill(4)+'.txt');file.write_bytes(reply.encode('utf-8'))
  manifest.append(dict(page=page,file=file.relative_to(out).as_posix(),sha256=sha(file)))
 r[kind+'_pages']=manifest;save()
 # Verify first immutable page a second time, separate from terminal report.
 assert 'Error' not in command(4594,'qom-set -j '+path+' '+prop+' '+json.dumps('0'))
 assert command(4594,'qom-get '+path+' '+prop).encode('utf-8')==(out/manifest[0]['file']).read_bytes()
 r[kind+'_immutable_page_reread']=True;save()

def getnum(reply,key):
 m=re.search(r'(?<![\w])'+re.escape(key)+r'=(\d+)',reply);assert m,(key,reply[:1000]);return int(m[1])
def qpath(tree):
 stack=[];found=[]
 for line in tree.splitlines():
  m=re.match(r'^(\s*)/([^ ]*) \(([^)]+)\)',line)
  if not m:continue
  level=len(m[1]);name=m[2]
  while stack and stack[-1][0]>=level:stack.pop()
  if name:stack.append((level,name))
  if m[3]=='nv2a':found.append('/'+'/'.join(n for _,n in stack))
 assert len(found)==1;return found[0]
def physical_read(a,n):
 global physical_mode
 assert stopped and n==4 and 0<=a<0x4000000
 # Attestor checks that these are page-table addresses disjoint from the arena.
 assert g.ask('Qqemu.PhyMemMode:1')=='OK';physical_mode=True
 try:
  data=g.read(a,n);r['physical_reads'].append(dict(address=a,bytes=n,hex=data.hex(),purpose='page-table word'));return data
 finally:
  assert g.ask('Qqemu.PhyMemMode:0')=='OK' and g.ask('qqemu.PhyMemMode')=='0';physical_mode=False
def bp(add):
 global point
 assert stopped
 if add:point=True
 text=f'{"Z" if add else "z"}1,{checkpoint:x},1';reply=g.ask(text);r['points'].append(dict(command=text,reply=reply));save();assert reply=='OK'
 if not add:point=False
def wait_stop(seconds,step=False):
 global stopped
 assert stopped;g.s.settimeout(seconds);g.send('s' if step else 'c');stopped=False
 try:reply=g.recv();stopped=True;return reply
 except socket.timeout:g.s.settimeout(5);g.interrupt();stopped=True;raise AssertionError('Bounded checkpoint not reached')
 finally:g.s.settimeout(5)
def ftp(deadline):
 f=DeadlineFTP(min(deadline,time.monotonic()+5))
 try:f.connect('127.0.0.1',4596,timeout=f.budget());f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);return f
 except Exception:f.close();raise
try:
 deadline=time.monotonic()+60
 while True:
  assert time.monotonic()<deadline and not (run/'cleanup.json').exists()
  try:f=ftp(deadline);f.close();break
  except ftplib.all_errors:time.sleep(.2)
 lock=acquire_monitor_lock(4594);cmd('stop');stopped=True;g=Remote(4595)
 r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?');assert g.ask('qqemu.PhyMemMode')=='0'
 path=qpath(cmd('info qom-tree'));r['nv2a_path']=path
 assert getnum(cmd('qom-get '+path+' xwn-pattern260-report'),'current')==0
 assert getnum(cmd('qom-get '+path+' xwn-worker247-report'),'state')==0
 assert getnum(cmd('qom-get '+path+' xwn-ledger265-report'),'state')==0
 r['open_ui_refusal']=cmd('qom-set -j '+path+' xwn-ledger265 '+json.dumps('capture,1'))
 assert 'Error: 265 requires' in r['open_ui_refusal']
 assert getnum(cmd('qom-get '+path+' xwn-ledger265-report'),'state')==0
 bp(True)
 launch=dict(command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe',requested_utc=utc(),status='requesting')
 r['launch']=launch;save();g.send('c');stopped=False
 # Retry connection/login only; never retry SITE EXEC after it is sent.
 deadline=time.monotonic()+30;launch['connection_attempts']=[]
 while True:
  try:f=ftp(deadline);break
  except ftplib.all_errors as error:
   launch['connection_attempts'].append(dict(utc=utc(),error=repr(error)));save()
   if time.monotonic()>=deadline:raise
   time.sleep(.2)
 # Independent bounded command exchange after successful bounded login.
 f.deadline=time.monotonic()+20
 launch.update(status='sending_once',sent_utc=utc(),reply_budget_seconds=20);save()
 with f:launch.update(reply=f.sendcmd(launch['command']),status='accepted')
 save();g.s.settimeout(100)
 try:stop=g.recv();stopped=True
 except socket.timeout:g.s.settimeout(5);g.interrupt();stopped=True;raise AssertionError('Initial native checkpoint timeout')
 finally:g.s.settimeout(5)
 for stage in range(1,3):
  bp(False)
  text=cmd('info registers');registers={n.lower():int(v,16) for n,v in re.findall(r'\b(EIP|ESP|CR3|CR4)=([0-9a-fA-F]+)',text)}
  raw=g.ask('g');assert struct.unpack_from('<I',bytes.fromhex(raw),32)[0]==registers['eip']
  row=dict(stage=stage,stop=stop,utc=utc(),registers=registers,reads=[],partial_pins=[]);r['checkpoints'].append(row);save()
  def observed_read(a,n):
   assert stopped and 0<n<=16384 and len(row['reads'])<2048
   item=dict(address=a,bytes=n,status='requested');row['reads'].append(item);save()
   try:
    data=g.read(a,n);item.update(status='read',sha256=hashlib.sha256(data).hexdigest())
    if n<=32:item['hex']=data.hex()
    return data
   except BaseException as error:
    item.update(status='failed',error=repr(error))
    # Diagnose only the failing mapping, never read its physical payload.
    try:
     pa,walk=translate32(physical_read,registers['cr3'],registers['cr4'],a,(0,0))
     item['translation']=dict(physical=pa,walk=walk)
    except BaseException as cause:item['translation_error']=repr(cause)
    raise
   finally:save()
  idt=re.search(r'IDT=\s*([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',text);assert idt,'Actual stopped IDTR required'
  row['idtr']=dict(base=int(idt[1],16),limit=int(idt[2],16));save()
  kernel,gates=discovery.discover(observed_read,row['idtr']['base'],row['idtr']['limit'],trap_rvas)
  row['kernel_discovery']=dict(base=kernel,gates=gates);save()
  live_plan=dict(plan,kernel_base_lead=kernel)
  inspector=Attestor(live_plan,pes,observed_read,physical_read)
  try:
   inspector.header('ntoskrnl.exe',kernel)
   for vector,rva in trap_rvas.items():inspector.pin('ntoskrnl.exe',kernel,rva,16)
   row['trap_pins']=inspector.pins.copy();save()
   att=inspector.checkpoint(stage,registers,registers['cr3'],registers['cr4'])
   row['attestation']=att
  finally:row['partial_pins']=inspector.pins.copy();save()

  if stage==1:
   frontend=True;r['frontend_close_requested']=True;save()
   assert 'Error' not in cmd('qom-set '+path+' xwn-frontend246-close true')
   deadline=time.monotonic()+8
   while True:
    report=cmd('qom-get '+path+' xwn-frontend246-report');state=getnum(report,'state')
    if state in [2,3]:break
    assert time.monotonic()<deadline;time.sleep(.03)
   assert state==2 and all(getnum(report,n)==0 for n in ['loan','bql','error'])
   r['frontend_closed_report']=report
   r['ui_report']=cmd('qom-get '+path+' xwn-ui265-report')
   assert all(getnum(r['ui_report'],n)==v for n,v in [('ready',1),('epoch',1),('error',0),('overflow',0)])
   capture_pages('ui',r['ui_report'])
  else:
   first=r['checkpoints'][0]['attestation']
   for name in ['thread','process','pid','probe_base','file_object','device_object','driver_object','physical','virtual','generation','pages']:
    assert att[name]==first[name],('Lifetime changed',name)
  if stage==1:
   row['request_may_be_accepted']=True;save()
   response=cmd('qom-set -j '+path+' xwn-ledger265 '+json.dumps('capture,1'))
   row['request_reply']=response;save();assert 'Error' not in response
   deadline=time.monotonic()+12
   while True:
    report=cmd('qom-get '+path+' xwn-ledger265-report');state=getnum(report,'state')
    if state in [5,6]:break
    assert time.monotonic()<deadline;time.sleep(.03)
   row['ledger_report']=report;row['state']=state;save()
   # Preserve even a partial failed capture; never reinterpret it as complete.
   if getnum(report,'pages'):capture_pages('ledger',report)
   assert state==5 and all(getnum(report,n)==0 for n in ['reason','overflow','pending'])
   for side in [0,1]:
    assert getnum(report,f'cpu{side}_done')==1 and getnum(report,f'cpu{side}_reason')==0
   assert cmd('qom-get '+path+' xwn-ledger265-report')==report
   row['immutable_reread']=True;save()
  if stage<2:
   row['step_reply']=wait_stop(5,True);bp(True);stop=wait_stop(30)
 r['final_report']=cmd('qom-get '+path+' xwn-ledger265-report')
 assert 'Error' not in cmd('qom-set '+path+' xwn-frontend246-close false')
 deadline=time.monotonic()+8
 while True:
  report=cmd('qom-get '+path+' xwn-frontend246-report')
  if getnum(report,'state')==5:break
  assert time.monotonic()<deadline;time.sleep(.03)
 reopened=True;r.update(frontend_reopened_report=report,passed=True,status='two_attested_observation_checkpoints_completed');save()
except BaseException as e:
 r.update(error=repr(e),host_traceback=traceback.format_exc(),status='preserved_diagnostic_failure');save()
 try:r['failure_registers']=cmd('info registers');r['failure_ledger']=cmd('qom-get '+path+' xwn-ledger265-report')
 except BaseException as capture:r['failure_capture_error']=repr(capture)
 save()
finally:
 if g:
  if not stopped:
   try:g.s.settimeout(5);g.interrupt();stopped=True
   except Exception as e:r['interrupt_error']=repr(e)
  if stopped and point:
   try:bp(False)
   except Exception as e:r['point_cleanup_error']=repr(e)
  if stopped:
   try:
    if physical_mode:assert g.ask('Qqemu.PhyMemMode:0')=='OK'
    r['physical_mode_restored']=g.ask('qqemu.PhyMemMode')=='0'
   except Exception as e:r['physical_mode_error']=repr(e)
  if frontend and not reopened:
   try:
    r['frontend_cleanup_reply']=cmd('qom-set '+path+' xwn-frontend246-close false')
   except Exception as e:r['frontend_cleanup_error']=repr(e)
  if r['passed'] and not point and r.get('physical_mode_restored'):
   g.send('c');stopped=False;r['guest_resumed']=True
  else:
   r['guest_resumed']=False;r['quarantined_until_owned_exit']=True
   try:cmd('quit')
   except Exception as e:r['quit_reply_error']=repr(e)
  g.s.close()
 if lock:lock.close()
 r.update(closed=True,remaining_breakpoints=int(point),closed_utc=utc());save();(out/'trace-finished.signal').touch(exist_ok=False)
print(json.dumps({n:r[n] for n in ['passed','status','error','guest_resumed'] if n in r}),flush=True)
