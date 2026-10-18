"""Bounded emulator-only FTP control proof. No data channel or console mutation."""
import ftplib,time
class ProbeFailure(Exception):
 def __init__(self,stage,error,events):
  super().__init__(stage+':'+type(error).__name__);self.stage=stage;self.events=events;self.error_type=type(error).__name__

def probe(port,credentials,path,expected_size,deadline,host='127.0.0.1'):
 assert host=='127.0.0.1' and 1024<=port<=65535
 assert path.startswith('/E/Applications/XWNBoot') and path.endswith('/entry.bin') and not any(c in path for c in '\r\n')
 assert expected_size==112
 events=[];stage='connect';f=ftplib.FTP()
 def bound():
  remaining=deadline-time.monotonic();assert remaining>0,'probe deadline expired'
  if f.sock:f.sock.settimeout(min(2,remaining))
  return min(2,remaining)
 def record(reply):
  assert isinstance(reply,str) and len(reply)<=8192
  events.append(dict(stage=stage,reply=reply,monotonic=time.monotonic()))
 try:
  reply=f.connect(host,port,timeout=bound());record(reply);assert reply.startswith('220')
  stage='login';bound();reply=f.login(*credentials);record(reply);assert reply.startswith('230')
  stage='binary';bound();reply=f.voidcmd('TYPE I');record(reply);assert reply.startswith('200')
  stage='pwd';bound();reply=f.sendcmd('PWD');record(reply);assert reply.startswith('257 ')
  stage='size';bound();reply=f.sendcmd('SIZE '+path);record(reply)
  assert reply=='213 '+str(expected_size),'unexpected receipt length'
  stage='noop';bound();reply=f.voidcmd('NOOP');record(reply);assert reply.startswith('200')
  stage='quit';bound();reply=f.quit();record(reply);assert reply.startswith('221')
  assert time.monotonic()<=deadline
  return dict(passed=True,authenticated_control=True,receipt_size=expected_size,live_receipt_bytes_verified=False,events=events)
 except BaseException as e:
  # FTP replies never include USER/PASS commands or caller-supplied credentials.
  if isinstance(e,ftplib.Error):
   value=str(e)
   for secret in credentials:
    if secret:value=value.replace(secret,'[redacted]')
   events.append(dict(stage=stage,error=type(e).__name__,reply=value[:8192],monotonic=time.monotonic()))
  raise ProbeFailure(stage,e,events) from e
 finally:f.close()
