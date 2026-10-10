"""Bounded owned loopback capture; native app only, no Windows launch."""
import datetime,ftplib,hashlib,io,json,os,socket,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[1];case=sys.argv[1];run=repo/('work/runs/xid-'+case)
port=int(os.environ['XID_FTP_PORT']);monitor=int(os.environ['XID_MONITOR_PORT'])
r=dict(physical_access=False,case=case,actions=[],launch_requested=False)
def save():(run/'observe.json').write_text(json.dumps(r,indent=2)+'\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def command(line):
 def recv(s):
  b=b''
  while not b.endswith(b'(qemu) '):
   x=s.recv(65536)
   if not x or len(b)>1024*1024:raise RuntimeError('monitor read')
   b+=x
  return b.decode('utf-8','replace')
 with socket.create_connection(('127.0.0.1',monitor),timeout=5) as s:
  recv(s);s.sendall((line+'\n').encode());reply=recv(s)
 r['actions'].append(dict(utc=now(),command=line,reply=reply));save();return reply
def connect():
 f=ftplib.FTP();f.connect('127.0.0.1',port,timeout=5)
 f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD'])
 assert 'unleash' in f.getwelcome().lower();return f
def get(f,path):
 b=io.BytesIO();f.retrbinary('RETR '+path,b.write);return b.getvalue()
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
remote='/E/Applications/XWNXid'+case
with f:
 stage=json.loads((run/'stage.json').read_text());assert stage['only_E_writes']
 data=(k/'artifacts/build003/bin/default.xbe').read_bytes();assert hashlib.sha256(data).hexdigest()==stage['binary_sha256']
 r.update(binary_sha256=hashlib.sha256(data).hexdigest(),remote=remote,launch_requested=True,launch_utc=now());save()
 try:r['launch_reply']=f.sendcmd('SITE EXEC '+('E:'+remote[2:].replace('/','\\'))+'\\default.xbe')
 except (OSError,EOFError,ftplib.Error) as e:r['launch_uncertain']=type(e).__name__
 save()
command('info usb')
launched=time.monotonic();deadline=launched+150
while time.monotonic()-launched<70:time.sleep(5)
while time.monotonic()<deadline:
 try:
  with connect() as f:
   r.update(dashboard_returned=True,returned_utc=now(),cold_collection_required=True);save();break
 except (OSError,EOFError,ftplib.Error):time.sleep(3)
else:raise RuntimeError('No completed return within bound; do not relaunch')
print('Native emulator capture returned and collected')
