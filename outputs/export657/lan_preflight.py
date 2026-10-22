"""Qualify Windows LAN-addressed broadcast reception; not console link proof."""
import hashlib,importlib.util,json,secrets,socket,struct,threading,zlib,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn657');cfg=json.loads((P/'config.json').read_text())
out=K/'lan001.json';assert not out.exists()
spec=importlib.util.spec_from_file_location('rx655',K.parent/'udp655/receiver.py');rx=importlib.util.module_from_spec(spec);spec.loader.exec_module(rx)
r=dict(passed=False,physical_access=False,scope='Windows host sends from its resolved LAN address to limited broadcast; verifies socket routing and receiver. Does not establish external firewall, switch or console delivery.')
try:
 raw=bytearray(Path('C:/xwn655/host002/encoder.stdout').read_bytes()[:772]);a=secrets.token_bytes(16);b=secrets.token_bytes(32)
 raw[16:32]=a;raw[32:64]=b;struct.pack_into('<I',raw,768,zlib.crc32(raw[:768]))
 manifest=dict(attempt=a.hex(),build_id=b.hex(),expected_peer=cfg['host'],fixture='physical-candidate',candidate_sha256='01'*32)
 result={}
 with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as listener:
  listener.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1);listener.bind(('',cfg['port']))
  def capture():
   try:result['capture']=rx.capture(listener,P/'lan001',manifest,seconds=3)
   except BaseException as e:result['error']=repr(e)
  t=threading.Thread(target=capture);t.start()
  with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as tx:
   tx.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1);tx.bind((cfg['host'],0))
   for i in range(3):assert tx.sendto(raw,('255.255.255.255',cfg['port']))==772
  t.join(8);assert not t.is_alive() and 'error' not in result,result
  got=result['capture'];assert got['status']=='one-distinct-valid-record' and got['duplicates']==2,got
  r.update(passed=True,duplicates=2,packet_sha256=hashlib.sha256(raw).hexdigest(),receiver_sha256=hashlib.sha256((K.parent/'udp655/receiver.py').read_bytes()).hexdigest(),all_sockets_closed=True)
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS LAN-addressed local broadcast, three packets; external path remains untested.')
