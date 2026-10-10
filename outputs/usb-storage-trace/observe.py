"""Exactly one loopback NT5 launch; bounded observation and no UI input."""
import datetime,ftplib,json,os,re,socket,subprocess,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[1];case=sys.argv[1]
assert re.fullmatch('emu[0-9]{3}',case)
run=repo/('work/runs/nt5stortrace-'+case);instance=json.loads((run/'instance.json').read_text())
assert not (run/'observe.json').exists() and not (run/'cleanup.json').exists()
monitor=instance['monitor_port'];port=instance['ftp_port']
r=dict(physical_access=False,case=case,actions=[],launch_requested=False,dashboard_returned=False)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():(run/'observe.json').write_text(json.dumps(r,indent=2)+'\n')
def command(line):
    def receive(s):
        b=b''
        while not b.endswith(b'(qemu) '):
            part=s.recv(65536)
            if not part or len(b)>1024*1024:raise RuntimeError('monitor budget/disconnection')
            b+=part
        return b.decode('utf-8','replace')
    with socket.create_connection(('127.0.0.1',monitor),timeout=5) as s:
        receive(s);s.sendall((line+'\n').encode());reply=receive(s)
    r['actions'].append(dict(utc=now(),command=line,reply=reply));save()
def connect():
    f=ftplib.FTP()
    try:
        f.connect('127.0.0.1',port,timeout=3)
        f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD'])
        assert 'unleash' in f.getwelcome().lower();return f
    except Exception:f.close();raise
save();deadline=time.monotonic()+90
while True:
    try:command('set_link nvnet.0 on');break
    except OSError:
        if time.monotonic()>deadline:raise
        time.sleep(2)
while True:
    try:f=connect();break
    except (OSError,EOFError,ftplib.Error):
        if time.monotonic()>deadline:raise
        time.sleep(2)
command('info usb')
r.update(launch_requested=True,launch_utc=now());save()
with f:
    try:r['launch_reply']=f.sendcmd(r'SITE EXEC E:\Applications\XWNFBoot\default.xbe')
    except (OSError,EOFError,ftplib.Error) as e:r['launch_uncertain']=type(e).__name__
save();start=time.monotonic();captured=False;seen_offline=False
while time.monotonic()-start<300:
    time.sleep(5)
    trace=run/'host-io.trace'
    if trace.exists() and trace.stat().st_size>128*1024*1024:
        r['trace_limit_exceeded']=True;save();break
    try:
        with connect():
            if seen_offline:r.update(dashboard_returned=True,returned_utc=now());save();break
    except (OSError,EOFError,ftplib.Error):seen_offline=True
r['seen_offline']=seen_offline;r['observation_end_utc']=now();r['elapsed_seconds']=time.monotonic()-start
r['closure']='dashboard return then host stop' if r['dashboard_returned'] else 'watchdog host stop; no relaunch'
save();print(r['closure'])
