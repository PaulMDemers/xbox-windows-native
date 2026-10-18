"""One read-only HMP command; require prompt acknowledgment and complete PPM."""
import datetime,hashlib,json,re,socket,time
from pathlib import Path
def ppm(data):
 m=re.match(rb'P6\n([0-9]+) ([0-9]+)\n255\n',data)
 if not m:raise ValueError('PPM header')
 w,h=map(int,m.groups())
 if not (0<w<=4096 and 0<h<=4096 and len(data)==m.end()+w*h*3):raise ValueError('PPM body')
 return w,h,m.end()
def capture(port,path,record,timeout=3):
 path=Path(path);record=Path(record);assert not path.exists() and not record.exists()
 r=dict(completed=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),path=str(path),port=port,command_sent=False,retry=False)
 def save():record.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 def prompt(s):
  end=time.monotonic()+timeout;data=b''
  while b'(qemu)' not in data:
   left=end-time.monotonic()
   if left<=0:raise TimeoutError('HMP prompt deadline')
   s.settimeout(left);b=s.recv(4096)
   if not b:raise EOFError('HMP closed before prompt')
   data+=b
   if len(data)>65536:raise ValueError('HMP reply bound')
  return data.decode('ascii',errors='replace')
 save()
 try:
  with socket.create_connection(('127.0.0.1',port),timeout=timeout) as s:
   r['banner']=prompt(s)
   name=path.as_posix();assert not any(c in name for c in ['"','\n','\r'])
   command='screendump "'+name+'"\n';r['command_sent']=True;save();s.sendall(command.encode('ascii'))
   r['reply']=prompt(s)
  data=path.read_bytes();w,h,_=ppm(data)
  r.update(completed=True,width=w,height=h,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 except BaseException as e:r['failure']=repr(e);raise
 finally:save()
 return r
if __name__=='__main__':
 import sys
 r=capture(int(sys.argv[1]),sys.argv[2],sys.argv[3]);print('Captured',r['width'],r['height'])
