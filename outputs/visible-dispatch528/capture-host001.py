"""Actual socket transport with one modeled HMP server per case."""
import hashlib,json,socket,threading,time
from pathlib import Path
from capture import capture
K=Path(__file__).resolve().parent;O=Path('C:/xwn528/capture-host001');assert not O.exists();O.mkdir()
cases=[]
for name in ['success','no-banner','no-ack','ack-no-file','truncated-file']:
 path=O/(name+'.ppm');record=O/(name+'.json');calls=[];errors=[]
 server=socket.socket();server.bind(('127.0.0.1',0));server.listen(1);server.settimeout(2);port=server.getsockname()[1]
 def worker():
  try:
   with server:
    with server.accept()[0] as c:
     c.settimeout(1)
     if name=='no-banner':time.sleep(.4);return
     c.sendall(b'QEMU modeled monitor\r\n(qemu) ')
     data=b''
     while not data.endswith(b'\n'):data+=c.recv(1024)
     calls.append(data);assert data==('screendump "'+path.as_posix()+'"\n').encode()
     if name=='no-ack':time.sleep(.4);return
     if name!='ack-no-file':path.write_bytes(b'P6\n2 2\n255\n'+b'\x00\x60\xc0'*(3 if name=='truncated-file' else 4))
     c.sendall(b'\r\n(qemu) ')
  except BaseException as e:errors.append(repr(e))
 thread=threading.Thread(target=worker);thread.start()
 try:
  capture(port,path,record,timeout=.15);assert name=='success'
 except (OSError,EOFError,ValueError):assert name!='success'
 thread.join(2);assert not thread.is_alive() and not errors,errors
 r=json.loads(record.read_text());assert r['completed']==(name=='success') and len(calls)==(0 if name=='no-banner' else 1)
 try:capture(port,path,record)
 except AssertionError:pass
 else:raise AssertionError('duplicate capture accepted')
 cases.append(dict(case=name,commands=len(calls),server_closed=True,result=r))
out=dict(passed=True,actual_socket_transport=True,server_and_pixels='MODELED',cases=cases,source_sha256=hashlib.sha256((K/'capture.py').read_bytes()).hexdigest())
(K/'capture-host001.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print('PASS five bounded actual transport cases with modeled HMP')
