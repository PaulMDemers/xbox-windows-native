"""Owned 180-second physical receiver; no launch, ACK, or retry capability."""
import importlib.util,json,os,socket
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn661')
cfg=json.loads((P/'config.json').read_text());build=json.loads((K/'build001.json').read_text())
cfg['candidate_sha256']=build['artifacts']['default.xbe']['sha256']
spec=importlib.util.spec_from_file_location('rx655',K.parent/'udp655/receiver.py');rx=importlib.util.module_from_spec(spec);spec.loader.exec_module(rx)
assert not (P/'capture001').exists() and not (P/'receiver-ready001.json').exists()
with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
 s.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1);s.bind(('',cfg['port']))
 with (P/'receiver-ready001.json').open('x') as f:json.dump(dict(pid=os.getpid(),bound=True,port=cfg['port'],seconds=180),f)
 result=rx.capture(s,P/'capture001',cfg,seconds=180)
print(result['status'])
raise SystemExit(0 if result['status']=='one-distinct-valid-record' else 2)
