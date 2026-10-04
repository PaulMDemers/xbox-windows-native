"""Collect the exact native probe after its normal return to emulator FTP."""
import ftplib,io,json,pathlib,hashlib,datetime,sys
k=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
from monitor_capture import command
class FTP(ftplib.FTP):
 def makepasv(self):
  host,port=super().makepasv()
  command(4594,'hostfwd_remove xemu-netdev tcp:127.0.0.1:4597')
  reply=command(4594,'hostfwd_add xemu-netdev tcp:127.0.0.1:4597-10.0.2.15:'+str(port))
  assert 'Could not' not in reply,reply
  return '127.0.0.1',4597
def get(f,path):
 b=io.BytesIO();f.retrbinary('RETR '+path,b.write);return b.getvalue()
with FTP() as f:
 f.connect('127.0.0.1',4596,timeout=8);f.login('xbox','xbox');f.cwd('/F')
 log=get(f,'xwn-physical.log');data=get(f,'xwn-physical-write.bin')
 assert b'XWN-PHYSICAL-PASS\r\n' in log and b'Failures: 0\r\n' in log
 assert data==bytes(((i*37+(i>>8)+0x5a)&255)^0xa5 for i in range(65537))
 r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run':'nt5-physical-f-package-003','scope':'Emulator only; FTP report after native Windows normal restart','log':log.decode('ascii'),'log_sha256':hashlib.sha256(log).hexdigest(),'payload_sha256':hashlib.sha256(data).hexdigest(),'payload_bytes':len(data),'passed':True}
 (k/'emulator-cycle.json').write_text(json.dumps(r,indent=2)+'\n');print(r['log'])
