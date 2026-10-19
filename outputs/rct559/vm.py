"""MIT. Owned bounded NT5 retail installer/game observation via QMP."""
import argparse,datetime,hashlib,importlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(K.parent/'clean-media404'));Qmp=importlib.import_module('pc-run001').Qmp
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
a=argparse.ArgumentParser();a.add_argument('number',type=int,choices=[560,561,562]);a.add_argument('action',choices=['run','screen','key','type','mouse','status']);a.add_argument('--text');a.add_argument('--x',type=int);a.add_argument('--y',type=int);a.add_argument('--width',type=int,default=800);a.add_argument('--height',type=int,default=600);a.add_argument('--click',action='store_true');args=a.parse_args()
T=K.parent/f'rct{args.number}';P=Path(json.loads((T/'edition.json').read_text())['fixture']);F=P/'phase1';sock=F/'qmp.sock';record=T/'ntfs-phase1.json';name=f'xwn-rct{args.number}-pc-phase1'
if args.action!='run':
 r=json.loads(record.read_text());assert not r['closed'] and name.encode() in Path(f"/proc/{r['pid']}/cmdline").read_bytes()
 with Qmp(sock) as q:
  if args.action=='screen':
   dest=F/f'screen-{time.time_ns()}.png';q.call('screendump',{'filename':str(dest),'format':'png'});print(dest)
  elif args.action=='status':print(q.call('query-status'))
  else:
   j=F/f'input-{time.time_ns()}.json';r=dict(action=args.action,text=args.text,x=args.x,y=args.y,click=args.click,utc=utc(),sent=False);j.write_text(json.dumps(r))
   if args.action=='mouse':
    assert 0<=args.x<args.width and 0<=args.y<args.height
    events=[{'type':'abs','data':{'axis':'x','value':round(args.x*32767/(args.width-1))}},{'type':'abs','data':{'axis':'y','value':round(args.y*32767/(args.height-1))}}]
    q.call('input-send-event',{'events':events})
    if args.click:
     for down in [True,False]:q.call('input-send-event',{'events':[{'type':'btn','data':{'down':down,'button':'left'}}]});time.sleep(.12)
   else:
    assert args.text
    mapping={'\\':'backslash',':':'shift-semicolon','.':'dot',' ':'spc','-':'minus','/':'slash','_':'shift-minus'}
    keys=[args.text] if args.action=='key' else [mapping.get(c,'shift-'+c.lower() if c.isupper() else c) for c in args.text]
    for key in keys:q.call('human-monitor-command',{'command-line':'sendkey '+key+' 40'});time.sleep(.15)
   r['sent']=True;j.write_text(json.dumps(r))
 sys.exit()
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive' and not F.exists() and not record.exists()
prep=json.loads((T/'ntfs-preparation001.json').read_text());cold=json.loads((T/'ntfs-cold0-002.json').read_text())
assert cold['complete'] and cold['audit_unchanged'] and cold['source_unchanged']
assert sha(P/'disk.qcow2')==prep['child_sha256']==cold['disk_sha256']
assert sha(prep['source'])==prep['source_sha256'] and sha(prep['media'])==prep['iso_sha256']
for n,h in {**prep['runtime_pins'],**prep['inputs']}.items():assert sha(n)==h,n
space=require_space(P,21);F.mkdir()
R=Path('/home/paul/xbox-windows-native/toolchains/qemu-pc/root')
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(R/'usr/lib/x86_64-linux-gnu')
cmd=[str(R/'usr/bin/qemu-system-i386'),'-name',name,'-L',str(R/'usr/share/qemu'),'-bios',str(R/'usr/share/seabios/bios.bin'),'-machine','pc,acpi=off,hpet=off','-accel','tcg,thread=single','-cpu','pentium3','-smp','1','-m','64','-vga','cirrus','-display','none','-nic','none','-drive',f'file={P}/disk.qcow2,format=qcow2,if=ide,index=0','-drive',f"file={prep['media']},media=cdrom,readonly=on,if=ide,index=2",'-usb','-device','usb-tablet','-boot','order=c','-qmp',f'unix:{sock},server=on,wait=off','-rtc','base=utc','-no-reboot']
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
    except Exception as e:state['capture_error']=type(e).__name__
    capture=time.monotonic()+45
 finally:
  state['deadline']=time.monotonic()>=deadline
  if proc.poll() is None:
   try:
    with Qmp(sock) as q:q.call('quit')
    state['host_quit']=True
   except Exception:proc.terminate();state['host_terminate']=True
   try:proc.wait(timeout=15)
   except subprocess.TimeoutExpired:proc.kill();proc.wait();state['host_kill']=True
  state.update(closed=True,exit_code=proc.returncode,ended_utc=utc(),disk_sha256=sha(P/'disk.qcow2'),source_unchanged=sha(prep['source'])==prep['source_sha256'],iso_unchanged=sha(prep['media'])==prep['iso_sha256']);save()
  if sock.exists():sock.unlink()
print(json.dumps(state))
