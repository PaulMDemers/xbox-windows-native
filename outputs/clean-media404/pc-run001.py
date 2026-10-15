"""One bounded owned setup phase; each next reboot phase needs a fresh record."""
import argparse,datetime,hashlib,json,os,socket,subprocess,time
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/home/paul/xbox-windows-native/clean-media404-oem001')
R=Path('/home/paul/xbox-windows-native/toolchains/qemu-pc/root')
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Qmp:
 def __init__(self,path):self.path=path
 def __enter__(self):
  self.sock=socket.socket(socket.AF_UNIX);self.sock.settimeout(10);self.sock.connect(str(self.path));self.f=self.sock.makefile('rwb',buffering=0);json.loads(self.f.readline());self.call('qmp_capabilities');return self
 def call(self,name,args=None):
  self.f.write((json.dumps({'execute':name,'arguments':args or {}})+'\n').encode())
  while True:
   row=json.loads(self.f.readline())
   if 'error' in row:raise RuntimeError(row['error'])
   if 'return' in row:return row['return']
 def __exit__(self,*args):self.f.close();self.sock.close()
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['run','capture','key','quit','status']);p.add_argument('--phase',type=int,required=True,choices=range(1,5));p.add_argument('--keys');a=p.parse_args()
 folder=P/('phase%02d'%a.phase);sock=folder/'qmp.sock';record=K/('oem001-phase%02d.json'%a.phase)
 if a.action!='run':
  with Qmp(sock) as q:
   if a.action=='capture':
    target=folder/('screen-'+str(time.time_ns())+'.png');q.call('screendump',{'filename':str(target),'format':'png'});print(target)
   elif a.action=='key':assert a.keys;print(q.call('human-monitor-command',{'command-line':'sendkey '+a.keys}))
   elif a.action=='quit':q.call('quit')
   else:print(json.dumps(q.call('query-status')))
  return
 assert os.environ.get('XBOX_XEMU_MODE')=='exclusive','Hold the cooperative emulator lease'
 assert not record.exists() and not folder.exists()
 preparation=json.loads((K/'preparation001.json').read_text());media=Path(preparation['media']);assert sha(media)==preparation['iso_sha256']
 for name,h in preparation['runtime_pins'].items():assert sha(Path(name))==h
 if a.phase>1:
  before=json.loads((K/('oem001-phase%02d.json'%(a.phase-1))).read_text());assert before['closed'] and before['exit_code']==0
 folder.mkdir()
 env=os.environ.copy();env['LD_LIBRARY_PATH']=str(R/'usr/lib/x86_64-linux-gnu')
 cmd=[str(R/'usr/bin/qemu-system-i386'),'-name','xwn-clean404-oem001-phase'+str(a.phase),'-L',str(R/'usr/share/qemu'),'-bios',str(R/'usr/share/seabios/bios.bin'),'-machine','pc,acpi=off,hpet=off','-accel','tcg,thread=single','-cpu','pentium3','-smp','1','-m','64','-vga','cirrus','-display','none','-nic','none','-drive',f'file={P}/disk.qcow2,format=qcow2,if=ide,index=0']
 if a.phase<4:cmd+=['-drive',f'file={media},media=cdrom,readonly=on,if=ide,index=2','-drive',f'file={P}/answer.img,format=raw,if=floppy,readonly=on']
 cmd+=['-boot','once=d' if a.phase==1 else 'order=c','-qmp',f'unix:{sock},server=on,wait=off','-rtc','base=utc','-no-reboot']
 state={'command':cmd,'started_utc':utc(),'phase':a.phase,'disk_only':a.phase==4,'iso_sha256':preparation['iso_sha256'],'physical_access':False,'network_device':False,'closed':False}
 def save():record.write_text(json.dumps(state,indent=2)+'\n')
 with (folder/'qemu.log').open('xb') as log:
  proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT);state['pid']=proc.pid;save();deadline=time.monotonic()+1200;nextscreen=time.monotonic()+30
  try:
   while proc.poll() is None and time.monotonic()<deadline:
    time.sleep(1)
    if time.monotonic()>=nextscreen:
     try:
      with Qmp(sock) as q:q.call('screendump',{'filename':str(folder/('auto-'+str(time.time_ns())+'.png')),'format':'png'})
     except Exception as e:state['capture_error']=type(e).__name__
     nextscreen=time.monotonic()+60
  finally:
   state['deadline']=time.monotonic()>=deadline
   if proc.poll() is None:
    try:
     with Qmp(sock) as q:q.call('quit')
     state['host_quit']=True
    except Exception:proc.terminate();state['host_terminate']=True
    try:proc.wait(timeout=15)
    except subprocess.TimeoutExpired:proc.kill();proc.wait();state['host_kill']=True
   state.update(exit_code=proc.returncode,closed=True,ended_utc=utc(),disk_sha256=sha(P/'disk.qcow2'));save()
   if sock.exists():sock.unlink()
 print(json.dumps({n:state[n] for n in ['phase','closed','exit_code','deadline']}))
if __name__=='__main__':main()
