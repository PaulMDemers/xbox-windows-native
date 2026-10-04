"""Small bounded data-connection experiment in the owned staging directory."""
import ftplib,socket,time,io,pathlib,json,os
class FTP(ftplib.FTP):
 def ntransfercmd(self,*a,**kw):
  s,n=super().ntransfercmd(*a,**kw);s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return s,n
k=pathlib.Path(__file__).resolve().parent;r=[]
with FTP() as f:
 f.connect('192.168.50.242',timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD']);f.cwd('/E/Applications/XWNFBoot')
 for size in [32768,32768,32768]:
  name='xwn-nodelay.tmp';data=b'XWN benchmark\n'.ljust(size,b'x');t=time.monotonic();f.storbinary('STOR '+name,io.BytesIO(data),blocksize=1024)
  elapsed=time.monotonic()-t;b=io.BytesIO();f.retrbinary('RETR '+name,b.write);assert b.getvalue()==data;f.delete(name)
  r.append({'bytes':size,'seconds':elapsed,'readback':True});print(r[-1],flush=True)
  (k/'nodelay-benchmark.json').write_text(json.dumps(r,indent=2)+'\n')
(k/'nodelay-benchmark.json').write_text(json.dumps(r,indent=2)+'\n')
