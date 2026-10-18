"""Real local sockets and stdlib FTP; fixture servers are models, no Xbox access."""
import contextlib,ftplib,hashlib,json,socket,threading,time
from pathlib import Path
from probe import probe,ProbeFailure
K=Path(__file__).resolve().parent;out=K/'host002.json';assert not out.exists()
credentials=('fixture-user','fixture-token');path='/E/Applications/XWNBoot504a/entry.bin'
class Server:
 def __init__(self,change=None):
  self.s=socket.socket();self.s.bind(('127.0.0.1',0));self.s.listen(1);self.s.settimeout(3)
  self.port=self.s.getsockname()[1];self.change=change;self.verbs=[];self.errors=[]
  self.refused=socket.socket();self.refused.bind(('127.0.0.1',0));self.deadport=self.refused.getsockname()[1]
  self.thread=threading.Thread(target=self.run);self.thread.start()
 def run(self):
  try:
   with self.s.accept()[0] as c:
    c.settimeout(3)
    def send(stage,value):
     if self.change and self.change[0]==stage:
      if self.change[1]=='eof':return False
      if self.change[1]=='delay':time.sleep(.3);return False
      value=self.change[1]
     c.sendall((value+'\r\n').encode());return True
    if not send('connect','220 fixture'):return
    with c.makefile('rb') as f:
     while True:
      line=f.readline(8193)
      if not line:return
      assert len(line)<=8192
      verb=line.decode().split()[0];self.verbs.append(verb)
      stage={'USER':'user','PASS':'login','TYPE':'binary','PWD':'pwd','SIZE':'size','NOOP':'noop','QUIT':'quit','PASV':'pasv','RETR':'retr'}[verb]
      replies={'USER':'331 continue','PASS':'230 fixture','TYPE':'200 binary','PWD':'257 "/"','SIZE':'213 112','NOOP':'200 okay','QUIT':'221 goodbye','PASV':f'227 entering (127,0,0,1,{self.deadport//256},{self.deadport%256})','RETR':'425 fixture data failure'}
      if not send(stage,replies[verb]) or verb=='QUIT':return
  except (ConnectionResetError,BrokenPipeError):pass
  except BaseException as e:self.errors.append(repr(e))
 def close(self):
  self.thread.join(4);self.s.close();self.refused.close();assert not self.thread.is_alive() and not self.errors,self.errors
# Reproduce default passive transfer after successful auth, with no data listener.
s=Server();f=ftplib.FTP();reproduction={}
try:
 f.connect('127.0.0.1',s.port,timeout=3);f.login(*credentials)
 try:f.retrbinary('RETR '+path,lambda data:None)
 except (ConnectionRefusedError,TimeoutError) as error:reproduction=dict(login_succeeded=True,data_channel_unreachable=True,error_type=type(error).__name__,default_passive=True)
 else:raise AssertionError('Expected unreachable passive data port')
finally:f.close();s.close()
assert s.verbs==['USER','PASS','TYPE','PASV'];reproduction['verbs']=s.verbs
s=Server()
try:r=probe(s.port,credentials,path,112,time.monotonic()+2)
finally:s.close()
assert r['passed'] and not r['live_receipt_bytes_verified']
assert s.verbs==['USER','PASS','TYPE','PWD','SIZE','NOOP','QUIT']
failures=[]
changes=[(stage,reply) for stage,reply in [('connect','421 unavailable'),('login','530 denied'),('binary','500 unsupported'),('pwd','200 wrong'),('size','213 111'),('size','213 nope'),('size','550 absent'),('noop','421 closing'),('quit','500 refused')]]
changes += [(stage,'eof') for stage in ['connect','login','binary','pwd','size','noop','quit']]
changes += [('size','delay')]
for change in changes:
 s=Server(change);started=time.monotonic()
 try:
  try:probe(s.port,credentials,path,112,time.monotonic()+(.1 if change[1]=='delay' else 2))
  except ProbeFailure as e:failures.append(dict(change=change,stage=e.stage,error=e.error_type,events=e.events,verbs=s.verbs.copy()))
  else:raise AssertionError(change)
 finally:s.close()
 assert time.monotonic()-started<4
 assert not any(v in s.verbs for v in ['PASV','PORT','EPRT','RETR'])
# Input validation is before connection; no accepting service required.
invalid=0
for kw in [dict(host='192.0.2.1'),dict(path='/C/forbidden'),dict(path=path+'\r\nNOOP'),dict(expected_size=113)]:
 args=dict(port=65000,credentials=credentials,path=path,expected_size=112,deadline=time.monotonic()+1);args.update(kw)
 try:probe(**args)
 except AssertionError:invalid+=1
 else:raise AssertionError(kw)
r=dict(passed=True,actual_local_socket_successes=2,default_passive_reproduction=reproduction,control_only_failure_cases=len(failures),input_refusals=invalid,failures=failures,all_server_threads_closed=True,physical_access=False,guest_access=False,server_effects_modeled=True,actual_stdlib_transport_executed=True,live_receipt_bytes_qualified=False,sources={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['probe.py','host002.py']})
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print({k:v for k,v in r.items() if k not in ['sources','failures']})
