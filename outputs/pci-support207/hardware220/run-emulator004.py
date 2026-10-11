"""Bounded read-only inventory rehearsal; host stop never qualifies normal shutdown."""
import datetime,ftplib,hashlib,json,os,shutil,socket,subprocess,time
from pathlib import Path
k=Path(__file__).resolve().parent
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
canonical=Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
case=k/'emulator004';fixture=json.loads((case/'fixture.json').read_text())
out=case/'artifacts/runtime';assert not out.exists()
source=case/'artifacts/source.qcow2';assert sha(source)==fixture['source_sha256']
exe=canonical/'outputs/xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe'
assert sha(exe)=='685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890'
bios=Path('C:/Emulators/xemu/system/bios/Complex_4627.bin');mcpx=Path('C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin')
iso=canonical/'outputs/native-windows-extended-storage/artifacts/f-boot-length-004.iso'
eeprom=canonical/'work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin'
for port in (4714,4716):
    with socket.socket() as sock:sock.bind(('127.0.0.1',port))
out.mkdir();shutil.copyfile(source,out/'hdd.qcow2');shutil.copyfile(eeprom,out/'eeprom.bin')
config=out/'config.toml'
config.write_text("[general]\nshow_welcome = false\n[general.updates]\ncheck = false\n[sys.files]\n" +
 '\n'.join(f"{name} = '{p.as_posix()}'" for name,p in [('bootrom_path',mcpx),('flashrom_path',bios),('eeprom_path',out/'eeprom.bin'),('hdd_path',out/'hdd.qcow2')])+'\n[net]\nenable = false\n')
dest=case/'run.json';assert not dest.exists()
r={'scope':__doc__,'physical_access':False,'debugger':False,'ordinary_boot_qualified':False,'normal_shutdown':False,
   'host_bound_seconds_after_launch':180,'started_utc':now(),'closed':False,'launch_requested':False,
   'inputs':{str(p):sha(p) for p in (exe,bios,mcpx,iso,eeprom,source,config,Path(__file__))}}
def save():dest.write_text(json.dumps(r,indent=2)+'\n')
def connect():
    f=ftplib.FTP()
    try:f.connect('127.0.0.1',4716,timeout=3);f.login('xbox','xbox');return f
    except BaseException:f.close();raise
def monitor(command):
    with socket.create_connection(('127.0.0.1',4714),timeout=3) as s:
        def reply():
            data=b''
            while not data.endswith(b'(qemu) '):
                part=s.recv(65536)
                if not part:raise EOFError('monitor closed')
                data+=part
            return data.decode('utf-8','replace')
        reply();s.sendall((command+'\n').encode());return reply()
vm=None;stdout=(out/'stdout.log').open('xb');stderr=(out/'stderr.log').open('xb')
try:
    argv=[str(exe),'-config_path',str(config),'-m','64','-no-shutdown','-no-reboot',
          '-dvd_path',str(iso),'-machine','xbox,kernel-irqchip=off,avpack=composite',
          '-device','usb-kbd','-device','usb-mouse','-monitor','tcp:127.0.0.1:4714,server,nowait',
          '-nic','user,id=xemu-netdev,model=nvnet,restrict=on,hostfwd=tcp:127.0.0.1:4716-:21']
    si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=subprocess.SW_HIDE
    vm=subprocess.Popen(argv,cwd=out,stdout=stdout,stderr=stderr,startupinfo=si,
                        env=dict(os.environ,TEMP=str(out),TMP=str(out),TMPDIR=str(out)))
    r.update(pid=vm.pid,argv=argv);save()
    deadline=time.monotonic()+60
    while True:
        assert vm.poll() is None,'xemu exited before launch'
        try:r['link_reply']=monitor('set_link nvnet.0 on');break
        except OSError:
            if time.monotonic()>deadline:raise
            time.sleep(.5)
    while True:
        try:f=connect();break
        except ftplib.all_errors:
            if time.monotonic()>deadline:raise
            time.sleep(1)
    r.update(launch_requested=True,launch_requested_utc=now(),launch_command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe');save()
    try:
        try:r['launch_reply']=f.sendcmd(r['launch_command'])
        except ftplib.all_errors as e:r['launch_reply_uncertain']=type(e).__name__
    finally:f.close();save()
    deadline=time.monotonic()+180
    while time.monotonic()<deadline:
        if vm.poll() is not None:r['unexpected_exit']=vm.returncode;break
        time.sleep(1)
    r['closure_reason']='bounded_host_stop_for_cold_diagnostic_not_normal_shutdown'
except BaseException as e:
    r['failure']=type(e).__name__+': '+str(e);raise
finally:
    if vm:
        if vm.poll() is None:vm.terminate()
        vm.wait(timeout=10);r['exit_code']=vm.returncode
    stdout.close();stderr.close()
    r.update(closed=True,closed_utc=now(),source_unchanged=sha(source)==fixture['source_sha256']);save()
print(json.dumps(r))
