"""One bounded owned PC boot; unchanged desktop mode. Never repeat phase1."""
import argparse,datetime,json,os,socket,subprocess,sys,time
from launch_gate import launch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'crypto-persistence423'))
from ntfs_read002 import sha
K=Path(__file__).resolve().parent;W=K.parents[1]
P=Path('/home/paul/xbox-windows-native/d3d-window546-pc001')
R=Path('/home/paul/xbox-windows-native/toolchains/qemu-pc/root')
sys.path.insert(0,str(K.parent/'clean-media404'));from importlib import import_module
Qmp=import_module('pc-run001').Qmp
sys.path.insert(0,str(W/'tools'));from build_space import require_space
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
p=argparse.ArgumentParser();p.add_argument('action',choices=['run','screen','key','type','status']);p.add_argument('--phase',type=int,choices=[1],required=True);p.add_argument('--text');a=p.parse_args()
folder=P/f'phase{a.phase}';sock=folder/'qmp.sock';record=K/f'ntfs-phase{a.phase}.json'
if a.action!='run':
 state=json.loads(record.read_text());assert not state['closed'] and f'xwn-d3d-window546-pc-phase{a.phase}' in Path(f"/proc/{state['pid']}/cmdline").read_bytes().decode()
 with Qmp(sock) as q:
  if a.action=='screen':
   dest=folder/f'screen-{time.time_ns()}.png';q.call('screendump',{'filename':str(dest),'format':'png'});print(dest)
  elif a.action=='status':print(q.call('query-status'))
  else:
   assert a.text;keys=[a.text] if a.action=='key' else [{'\\':'backslash',':':'shift-semicolon','.':'dot',' ':'spc','-':'minus','/':'slash'}.get(c,c) for c in a.text]
   journal=folder/f'input-{time.time_ns()}.json';journal.write_text(json.dumps({'action':a.action,'text':a.text,'utc':utc(),'sent':False}))
   for key in keys:q.call('human-monitor-command',{'command-line':'sendkey '+key+' 20'});time.sleep(.2)
   journal.write_text(json.dumps({'action':a.action,'text':a.text,'utc':utc(),'sent':True}))
 sys.exit(0)
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
assert not folder.exists() and not record.exists()
prep=json.loads((K/'ntfs-preparation001.json').read_text());assert sha(Path(prep['source']))==prep['source_sha256']
assert sha(P/'probe.img')==prep['floppy_sha256']
for name,h in prep['inputs'].items():assert sha(K/name)==h,name
for name,h in prep['runtime_pins'].items():assert sha(Path(name))==h
if a.phase==1:assert sha(P/'disk.qcow2')==prep['child_sha256']
else:
 prev=json.loads((K/'ntfs-phase1.json').read_text());cold=json.loads((K/'ntfs-cold1-002.json').read_text())
 assert prev['closed'] and prev['exit_code']==0 and not prev['deadline'] and cold['normal_shutdown_delta']==1 and cold['complete']
 assert sha(P/'disk.qcow2')==cold['disk_sha256']
space=require_space(P,20+128/1024);folder.mkdir()
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(R/'usr/lib/x86_64-linux-gnu')
cmd=[str(R/'usr/bin/qemu-system-i386'),'-name',f'xwn-d3d-window546-pc-phase{a.phase}','-L',str(R/'usr/share/qemu'),'-bios',str(R/'usr/share/seabios/bios.bin'),'-machine','pc,acpi=off,hpet=off','-accel','tcg,thread=single','-cpu','pentium3','-smp','1','-m','64','-vga','cirrus','-display','none','-nic','none','-drive',f'file={P}/disk.qcow2,format=qcow2,if=ide,index=0','-drive',f'file={P}/probe.img,format=raw,if=floppy,readonly=on','-boot','order=c','-qmp',f'unix:{sock},server=on,wait=off','-rtc','base=utc','-no-reboot']
state={'command':cmd,'started_utc':utc(),'closed':False,'phase':a.phase,'space':space,'physical_access':False,'network_device':False}
def save():record.write_text(json.dumps(state,indent=2)+'\n')
with (folder/'qemu.log').open('xb') as log:
 proc=launch(K/'preflight001.json',K,P,'d3d-window546-pc001',cmd,popen=subprocess.Popen,env=env,stdout=log,stderr=subprocess.STDOUT);state['pid']=proc.pid;save();deadline=time.monotonic()+600;capture=time.monotonic()+35
 try:
  while proc.poll() is None and time.monotonic()<deadline:
   time.sleep(1)
   if time.monotonic()>=capture:
    try:
     with Qmp(sock) as q:q.call('screendump',{'filename':str(folder/f'auto-{time.time_ns()}.png'),'format':'png'})
    except Exception as e:state['capture_error']=repr(e)
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
  state.update(closed=True,exit_code=proc.returncode,ended_utc=utc(),disk_sha256=sha(P/'disk.qcow2'),source_unchanged=sha(Path(prep['source']))==prep['source_sha256'],floppy_unchanged=sha(P/'probe.img')==prep['floppy_sha256']);save()
  if sock.exists():sock.unlink()
print(json.dumps({k:state[k] for k in ['closed','exit_code','deadline','source_unchanged','floppy_unchanged']}))
