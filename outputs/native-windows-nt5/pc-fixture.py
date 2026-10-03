"""Bounded private PC fixture launcher and QMP controller. Run under WSL.

Uses a dedicated Unix socket; no network interface or TCP control port.
The launcher owns its QEMU child and terminates only that child in finally.
"""
import argparse, hashlib, json, os, pathlib, socket, subprocess, time
ROOT=pathlib.Path('/home/paul/xbox-windows-native')
WORKSPACE=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
VM=ROOT/'fixtures/pc-win2000'
SOCKET=VM/'qmp.sock'
OUT=WORKSPACE/'outputs/native-windows-nt5/pc-evidence'
RUNTIME=ROOT/'toolchains/qemu-pc/root'
class Qmp:
    def __enter__(self):
        self.sock=socket.socket(socket.AF_UNIX);self.sock.settimeout(10);self.sock.connect(str(SOCKET))
        self.f=self.sock.makefile('rwb',buffering=0)
        self.greeting=json.loads(self.f.readline());self.call('qmp_capabilities');return self
    def call(self,execute,arguments=None):
        self.f.write((json.dumps({'execute':execute,'arguments':arguments or {}})+'\n').encode())
        while True:
            msg=json.loads(self.f.readline())
            if 'error' in msg:raise RuntimeError(msg['error'])
            if 'return' in msg:return msg['return']
    def __exit__(self,*args):self.f.close();self.sock.close()
def launch(minutes,install=False,media='EN_WIN2000_PRO_SP4.ISO',disk_only=False):
    VM.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    if SOCKET.exists():raise SystemExit('QMP socket exists; inspect ownership before relaunch')
    disk=VM/'win2000.qcow2'
    if disk_only and (install or not disk.exists()):raise SystemExit('Disk-only mode requires an existing installed disk')
    if not disk.exists():
        subprocess.run(['qemu-img','create','-f','qcow2',str(disk),'2G'],check=True)
        install=True
    env=os.environ.copy();env['LD_LIBRARY_PATH']=str(RUNTIME/'usr/lib/x86_64-linux-gnu')
    cmd=[str(RUNTIME/'usr/bin/qemu-system-i386'),'-name','windows-native-pc-fixture',
         '-L',str(RUNTIME/'usr/share/qemu'),'-bios',str(RUNTIME/'usr/share/seabios/bios.bin'),
         '-machine','pc,acpi=off,hpet=off','-accel','tcg,thread=single','-cpu','pentium3','-smp','1','-m','64',
         '-vga','cirrus','-display','none','-nic','none',
         '-drive',f'file={disk},format=qcow2,if=ide,index=0']
    if not disk_only:
        cmd += ['-drive',f'file={WORKSPACE}/outputs/{media},media=cdrom,readonly=on,if=ide,index=2',
                '-drive',f'file={WORKSPACE}/work/pc-fixture/answer.img,format=raw,if=floppy,readonly=on']
    cmd += ['-boot','once=d' if install else 'order=c','-qmp',f'unix:{SOCKET},server=on,wait=off',
         '-rtc','base=localtime','-no-reboot']
    # Stop at each requested reboot so the next disk boot is explicit.
    stamp=time.strftime('%Y%m%d-%H%M%S');log=OUT/f'launch-{stamp}.log'
    with log.open('wb') as stream:
        proc=subprocess.Popen(cmd,env=env,stdout=stream,stderr=subprocess.STDOUT)
        record={'pid':proc.pid,'command':cmd,'runtime':subprocess.check_output([cmd[0],'--version'],env=env,text=True).splitlines()[0],
                'disk':str(disk),'expires_after_minutes':minutes,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
        (OUT/'instance.json').write_text(json.dumps(record,indent=2)+'\n')
        try:
            deadline=time.monotonic()+minutes*60
            while proc.poll() is None and time.monotonic()<deadline:time.sleep(1)
        finally:
            if proc.poll() is None:
                try:
                    with Qmp() as q:q.call('quit')
                except (OSError,RuntimeError,ValueError):proc.terminate()
                try:proc.wait(timeout=15)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
            record['exit_code']=proc.returncode
            record['end_reason']='deadline' if time.monotonic()>=deadline else 'guest-exit-or-explicit-stop'
            record['ended_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
            (OUT/f'instance-{stamp}.json').write_text(json.dumps(record,indent=2)+'\n')
            if SOCKET.exists():SOCKET.unlink()
        if proc.returncode:raise SystemExit(proc.returncode)
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['launch','capture','key','status','stop']);p.add_argument('--minutes',type=int,default=30);p.add_argument('--name',default='screen');p.add_argument('--keys');p.add_argument('--install',action='store_true');p.add_argument('--media',choices=['EN_WIN2000_PRO_SP4.ISO','Windows 2000 (SP4).iso'],default='EN_WIN2000_PRO_SP4.ISO');p.add_argument('--disk-only',action='store_true');a=p.parse_args()
    if a.action=='launch':return launch(a.minutes,a.install,a.media,a.disk_only)
    with Qmp() as q:
        if a.action=='capture':
            target=OUT/(a.name+'.png');q.call('screendump',{'filename':str(target),'format':'png'});print(target)
        elif a.action=='key':
            assert a.keys
            print(q.call('human-monitor-command',{'command-line':'sendkey '+a.keys}))
        elif a.action=='status':print(json.dumps(q.call('query-status')))
        elif a.action=='stop':q.call('quit')
if __name__=='__main__':main()
