"""Bounded host-side timestamp recorder for owned virtual COM1."""
import datetime,json,socket,threading,time
from pathlib import Path
class Lines:
 def __init__(self):self.pending=b'';self.rows=[]
 def feed(self,data,stamp):
  self.pending+=data
  assert len(self.pending)<4096 and len(self.rows)<32
  while b'\n' in self.pending:
   line,self.pending=self.pending.split(b'\n',1)
   text=line.rstrip(b'\r').decode('ascii');parts=text.split()
   assert len(parts)==4 and parts[0]=='MARK' and parts[1] in ['START','END']
   case,tick=int(parts[2]),int(parts[3]);assert 0<=case<6 and 0<=tick<2**32
   assert not self.rows or stamp>=self.rows[-1]['monotonic_ns']
   self.rows.append(dict(line=text,kind=parts[1],case=case,tick=tick,monotonic_ns=stamp))
 def finish(self):assert not self.pending,'partial serial line'

class SerialRecorder:
 def __init__(self,path,out):
  self.path=path;self.out=Path(out);assert not self.out.exists()
  self.event=threading.Event();self.lines=Lines()
  self.state=dict(connected=False,closed=False,rows=[],clock='time.monotonic_ns',physical_access=False)
  self.thread=threading.Thread(target=self.run,name='xwn615-serial',daemon=True)
 def save(self):
  self.state['rows']=self.lines.rows
  self.out.write_text(json.dumps(self.state,indent=2)+'\n')
 def start(self):self.save();self.thread.start()
 def run(self):
  s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);s.settimeout(.1)
  try:
   deadline=time.monotonic()+10
   while True:
    try:s.connect(self.path);break
    except (FileNotFoundError,ConnectionRefusedError):
     if time.monotonic()>deadline:raise TimeoutError('serial connection deadline')
     time.sleep(.05)
   self.state.update(connected=True,connected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());self.save()
   while not self.event.is_set():
    try:data=s.recv(1024)
    except socket.timeout:continue
    if not data:break
    self.lines.feed(data,time.monotonic_ns());self.save()
   self.lines.finish()
  except BaseException as e:self.state['error']=repr(e)
  finally:s.close();self.state['closed']=True;self.save()
 def stop(self):
  self.event.set();self.thread.join(3)
  assert not self.thread.is_alive(),'serial reader did not stop'
