"""MIT. Owned bounded NT5 retail installer/game observation via QMP."""
from input_transport001 import plan
import argparse,datetime,hashlib,importlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(K.parent/'clean-media404'));Qmp=importlib.import_module('pc-run001').Qmp
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
a=argparse.ArgumentParser();a.add_argument('number',type=int,choices=[584]);a.add_argument('action',choices=['run','screen','key','type','mouse','status','block','eject']);a.add_argument('--text');a.add_argument('--x',type=int);a.add_argument('--y',type=int);a.add_argument('--width',type=int,default=800);a.add_argument('--height',type=int,default=600);a.add_argument('--click',action='store_true');a.add_argument('--button',choices=['left','right'],default='left');a.add_argument('--hold-ms',type=int,default=40);a.add_argument('--drag-x',type=int);a.add_argument('--drag-y',type=int);args=a.parse_args();assert 1<=args.hold_ms<=5000
T=K.parent/f'rct{args.number}';P=Path(json.loads((T/'edition.json').read_text())['fixture']);F=P/'phase1';sock=Path(f'/tmp/xwn-rct{args.number}-phase1.sock');record=T/'ntfs-phase1.json';name=f'xwn-rct{args.number}-pc-phase1'
if args.action!='run':
 r=json.loads(record.read_text());assert not r['closed'] and name.encode() in Path(f"/proc/{r['pid']}/cmdline").read_bytes()
 with Qmp(sock) as q:
  if args.action=='screen':
   dest=F/f'screen-{time.time_ns()}.png';q.call('screendump',{'filename':str(dest),'format':'png'});print(dest)
  elif args.action=='status':print(q.call('query-status'))
  elif args.action=='block':print(json.dumps(q.call('query-block')))
  elif args.action=='eject':
   assert args.text in ['ide1-cd0','ide1-cd1'];q.call('eject',{'device':args.text,'force':False});print(json.dumps(q.call('query-block')))
  else:
   j=F/f'input-{time.time_ns()}.json';r=dict(action=args.action,text=args.text,x=args.x,y=args.y,click=args.click,button=args.button,hold_ms=args.hold_ms,drag_x=args.drag_x,drag_y=args.drag_y,utc=utc(),sent=False);j.write_text(json.dumps(r))
   if args.action=='mouse':
    assert 0<=args.x<args.width and 0<=args.y<args.height
    events=[{'type':'abs','data':{'axis':'x','value':round(args.x*32767/(args.width-1))}},{'type':'abs','data':{'axis':'y','value':round(args.y*32767/(args.height-1))}}]
    q.call('input-send-event',{'events':events})
    if args.drag_x is not None or args.drag_y is not None:
     assert args.drag_x is not None and args.drag_y is not None and 0<=args.drag_x<args.width and 0<=args.drag_y<args.height
     q.call('input-send-event',{'events':[{'type':'btn','data':{'down':True,'button':args.button}}]});time.sleep(.15)
     try:
      for step in range(1,11):
       x=args.x+(args.drag_x-args.x)*step/10;y=args.y+(args.drag_y-args.y)*step/10
       q.call('input-send-event',{'events':[{'type':'abs','data':{'axis':'x','value':round(x*32767/(args.width-1))}},{'type':'abs','data':{'axis':'y','value':round(y*32767/(args.height-1))}}]});time.sleep(.1)
     finally:q.call('input-send-event',{'events':[{'type':'btn','data':{'down':False,'button':args.button}}]})
    elif args.click:
     for down in [True,False]:q.call('input-send-event',{'events':[{'type':'btn','data':{'down':down,'button':args.button}}]});time.sleep(.12)
   else:
    assert args.text
    mapping={'\\':'0x2b',':':'shift-semicolon','.':'dot',' ':'spc','-':'minus','/':'slash','_':'shift-minus'}
    keys=[args.text] if args.action=='key' else plan(args.text)
    for key in keys:
     response=q.call('human-monitor-command',{'command-line':'sendkey '+key+' '+str(args.hold_ms)})
     if response!='':raise RuntimeError('HMP textual error: '+repr(response))
     time.sleep(.15)
   r['sent']=True;j.write_text(json.dumps(r))
 sys.exit()
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive' and not F.exists() and not record.exists() and not sock.exists()
prep=json.loads((T/'ntfs-preparation001.json').read_text());cold=json.loads((T/'ntfs-cold0-002.json').read_text())
assert cold['complete'] and cold['audit_unchanged'] and cold['source_unchanged']
assert sha(P/'disk.qcow2')==prep['child_sha256']==cold['disk_sha256']
assert sha(prep['source'])==prep['source_sha256'] and sha(prep['helper_media'])==prep['helper_sha256']
assert sha(prep['retail_media'])==prep['retail_sha256']
for n,h in {**prep['runtime_pins'],**prep['inputs']}.items():assert sha(n)==h,n
space=require_space(P,21);F.mkdir()
R=Path('/home/paul/xbox-windows-native/toolchains/qemu-pc/root')
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(R/'usr/lib/x86_64-linux-gnu')
cmd=[str(R/'usr/bin/qemu-system-i386'),'-name',name,'-L',str(R/'usr/share/qemu'),'-bios',str(R/'usr/share/seabios/bios.bin'),'-machine','pc,acpi=off,hpet=off','-accel','tcg,thread=single','-cpu','pentium3','-smp','1','-m','64','-vga','cirrus','-display','none','-nic','none','-drive',f'file={P}/disk.qcow2,format=qcow2,if=ide,index=0','-drive',f"file={prep['helper_media']},media=cdrom,readonly=on,if=ide,index=2",'-drive',f"file={prep['retail_media']},media=cdrom,readonly=on,if=ide,index=3",'-usb','-device','usb-tablet','-boot','order=c','-qmp',f'unix:{sock},server=on,wait=off','-rtc','base=utc','-no-reboot']
state=dict(command=cmd,started_utc=utc(),closed=False,space=space,physical_access=False,network_device=False,phase=1)
def save():record.write_text(json.dumps(state,indent=2)+'\n')
with (F/'qemu.log').open('xb') as log:
 save();proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT);state['pid']=proc.pid;save();deadline=time.monotonic()+1800;capture=time.monotonic()+30
 try:
  while proc.poll() is None and time.monotonic()<deadline:
   time.sleep(1)
   if shutil.disk_usage('/mnt/c').free<20.125*1024**3:state['space_stop']=True;break
   if time.monotonic()>=capture:
    try:
     with Qmp(sock) as q:q.call('screendump',{'filename':str(F/f'auto-{time.time_ns()}.png'),'format':'png'})
    except Exception as e:state.setdefault('capture_errors',[]).append(dict(error=type(e).__name__,utc=utc(),process_exit=proc.poll()))
    capture=time.monotonic()+5
 finally:
  state['deadline']=time.monotonic()>=deadline
  if proc.poll() is None:
   try:
    with Qmp(sock) as q:q.call('quit')
    state['host_quit']=True
   except Exception:proc.terminate();state['host_terminate']=True
   try:proc.wait(timeout=15)
   except subprocess.TimeoutExpired:proc.kill();proc.wait();state['host_kill']=True
  state.update(closed=True,exit_code=proc.returncode,ended_utc=utc(),disk_sha256=sha(P/'disk.qcow2'),source_unchanged=sha(prep['source'])==prep['source_sha256'],iso_unchanged=sha(prep['helper_media'])==prep['helper_sha256']);save()
  if sock.exists():sock.unlink()
print(json.dumps(state))

if state['exit_code']!=0:sys.exit(state['exit_code'])
