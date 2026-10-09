"""Single bounded loopback-only emulator launch, descriptor observation and UI input smoke."""
import datetime,ftplib,json,os,socket,time,sys,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[1]
case=sys.argv[1];assert re.fullmatch(r'emu[0-9]{3}',case);run=repo/('work/runs/usb207-'+case)
monitor=int(os.environ['USB207_MONITOR_PORT']);ftp_port=int(os.environ['USB207_FTP_PORT'])
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
dest=run/'observation.json';assert not dest.exists()
r=dict(physical_access=False,debugger=False,launch_requested=False,actions=[],normal_shutdown_qualified=False)
def save():dest.write_text(json.dumps(r,indent=2)+'\n')
def command(text):
    def receive(s):
        data=b''
        while not data.endswith(b'(qemu) '):
            b=s.recv(65536)
            if not b or len(data)>1024*1024:raise RuntimeError('HMP disconnected/over budget')
            data+=b
        return data.decode('utf-8','replace')
    with socket.create_connection(('127.0.0.1',monitor),timeout=10) as s:
        receive(s);s.sendall((text+'\n').encode());reply=receive(s)
    r['actions'].append(dict(command=text,reply=reply));save();return reply
save();deadline=time.monotonic()+30
while True:
    try:command('set_link nvnet.0 on');break
    except OSError:
        if time.monotonic()>deadline:raise
        time.sleep(1)
deadline=time.monotonic()+60
while True:
    f=ftplib.FTP()
    try:
        f.connect('127.0.0.1',ftp_port,timeout=4)
        f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD'])
        break
    except (OSError,EOFError,ftplib.Error):
        f.close()
        if time.monotonic()>deadline:raise
        time.sleep(1)
command('info usb');command('info qtree')
r.update(launch_requested=True,launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe');save()
try:r['reply']=f.sendcmd(r['command'])
except (OSError,EOFError,ftplib.Error) as exc:r['reply_uncertain']=type(exc).__name__
finally:f.close();save()
# These framebuffer snapshots pause/resume the owned guest; diagnostic only.
def capture(name):
    subprocess.run([sys.executable,'-B',str(repo/'outputs/native-windows-prebuild/monitor_capture.py'),
        '--port',str(monitor),'--output',str(run/(name+'.png')),'--auto-framebuffer'],check=True)
time.sleep(75)
command('info usb');capture('desktop')
command('sendkey ctrl-esc');time.sleep(2)
capture('keyboard')
command('sendkey esc');command('mouse_move 80 60');time.sleep(2)
capture('mouse')
time.sleep(10)
r['observer_complete']=True;r['closure']='bounded diagnostic host stop; not normal shutdown';save()
print('USB207 diagnostic observer complete; owner will stop its exact emulator process')
