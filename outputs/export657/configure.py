"""Resolve the owned console connection and assign private diagnostic identity."""
import importlib.util,ipaddress,json,secrets,shutil,socket
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn657')
s=importlib.util.spec_from_file_location('session642',K.parent/'windows480p642/physical.py')
b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
assert not P.exists() and not (K/'configuration001.json').exists()
assert shutil.disk_usage('C:/').free-128*1024**2>20.05*1024**3
b.session();b.m.ticket()
with b.m.connect(timeout=10) as f:
 b.m.baseline(f,'720p');b.startup(f)
 peer=f.sock.getpeername()[0];host=f.sock.getsockname()[0]
 assert ipaddress.ip_address(peer).is_private and ipaddress.ip_address(host).is_private
with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
 sock.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1);sock.bind(('',50657))
P.mkdir()
cfg=dict(attempt=secrets.token_hex(16),build_id=secrets.token_hex(32),expected_peer=peer,host=host,port=50657,fixture='physical-candidate')
(P/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
def array(x):return ','.join(str(v) for v in x)
(P/'identity657.h').write_text('static const struct xwn655_identity Identity657={{'+array(bytes.fromhex(cfg['attempt']))+'},{'+array(bytes.fromhex(cfg['build_id']))+'}};\nstatic const uint8_t SourceIP657[4]={'+array(ipaddress.ip_address(peer).packed)+'};\nstatic const uint16_t Port657=50657;\n')
b.m.write_json(K/'configuration001.json',dict(utc=b.m.utc(),dashboard_reachable=True,ordinary720p_checked=True,hook=False,port_available=True,private_config=str(P/'config.json'),identity_header_sha256=b.m.sha((P/'identity657.h').read_bytes()),physical_launch=False))
print('Private identity assigned; dashboard and protected720p checked; UDP port available.')
