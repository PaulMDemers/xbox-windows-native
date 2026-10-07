"""Independently check both directional transcript hashes and runner isolation."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control001','candidate001']
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(k/case/'network-host.json');a=read(k/case/'audit.json');assert r['complete'] and r['network_restricted'] and len(r['connections'])==2
for phase,row in enumerate(r['connections']):
    raw=bytes((phase*97+round*13+offset*7)&255 for round in range(32) for offset in range(4096));response=bytes(v^0xa5 for v in raw)
    assert row['phase']==phase and row['rounds']==32 and row['received']==row['sent']==len(raw)==131072 and row['peer_send_closed']
    assert row['received_sha256']==hashlib.sha256(raw).hexdigest() and row['sent_sha256']==hashlib.sha256(response).hexdigest()
assert sha(k/case/'network-host.json')==a['network_host_sha256'] and a['network_passed']
runner=(k/case/'source/Invoke-Network.ps1').read_text();assert 'restrict=on,hostfwd=tcp:127.0.0.1:${FtpPort}-:21,hostfwd=tcp:127.0.0.1:4597-:4597' in runner
print(case,'two exact bidirectional TCP exchanges; restricted loopback-only host forward')
