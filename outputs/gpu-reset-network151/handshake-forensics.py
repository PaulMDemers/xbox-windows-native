"""Measure the failed greeting after SYN and SYN/ACK without changing old records."""
import hashlib,json
from pathlib import Path
from packets import decode
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001'
data=(ws/'work/runs/gpu-reset-network151-candidate001/nvnet.pcap').read_bytes()
reset=json.loads((out/'reset.json').read_text());frames=decode(data)['frames'];flows={}
for f in frames:
    if f['offset']<reset['after_reset_pcap_offset'] or f.get('protocol')!=6 or 21 not in [f['source_port'],f['destination_port']]:continue
    port=f['source_port'] if f['destination_port']==21 else f['destination_port'];r=flows.setdefault(port,dict(port=port))
    t=f['seconds']+f['microseconds']/1e6
    if f['destination_port']==21 and f['tcp_flags']==2:r.setdefault('syn',t)
    if f['source_port']==21 and f['tcp_flags']==18:r.setdefault('synack',t)
    if f['destination_port']==21 and f['tcp_flags']&1:r.setdefault('fin',t)
    if f.get('ftp_greeting_part'):r.setdefault('greeting',t)
    if f.get('ftp_greeting_ready'):r.setdefault('ready',t)
rows=[]
for r in flows.values():
    if all(p in r for p in ['syn','synack','fin','greeting','ready']):
        r.update(syn_to_greeting=round(r['greeting']-r['syn'],6),synack_to_greeting=round(r['greeting']-r['synack'],6),
                 host_closed_before_greeting=r['fin']<r['greeting']);rows.append(r)
assert len(rows)==40 and all(r['host_closed_before_greeting'] for r in rows)
p=out/'handshake.json';assert not p.exists()
p.write_text(json.dumps(dict(flows=rows,pcap_sha256=hashlib.sha256(data).hexdigest(),
                            forensic_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
print('SYN range',min(r['syn_to_greeting'] for r in rows),max(r['syn_to_greeting'] for r in rows))
print('SYNACK range',min(r['synack_to_greeting'] for r in rows),max(r['synack_to_greeting'] for r in rows))
