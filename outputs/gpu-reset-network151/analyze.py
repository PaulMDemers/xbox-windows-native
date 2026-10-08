"""Decode closed captures and pair FTP greetings with SYN/host closure evidence."""
import collections,hashlib,json,re,sys
from pathlib import Path
from packets import decode
k=Path(__file__).resolve().parent;ws=k.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def analyze(root,case):
    out=root/case;run=ws/'work/runs'/(root.name+'-'+case);assert (run/'cleanup.json').exists()
    reset=json.loads((out/'reset.json').read_text());raw=(run/'nvnet.pcap').read_bytes();packet=decode(raw)
    trace=(run/'cpu-trace.log').read_bytes();assert len(trace)<=16*1024*1024
    boundaries=[('startup',24,reset['reset_pcap_offset'],0,reset['reset_trace_offset']),
                ('reset_return',reset['reset_pcap_offset'],reset.get('after_reset_pcap_offset',len(raw)),reset['reset_trace_offset'],reset.get('after_reset',{}).get('trace_offset',len(trace))),
                ('probe_return',reset.get('after_reset_pcap_offset',len(raw)),len(raw),reset.get('after_reset',{}).get('trace_offset',len(trace)),len(trace))]
    phases={}
    for name,start,end,ts,te in boundaries:
        dhcp=[d for d in packet['dhcp'] if start<=d['offset']<end]
        rows=[f for f in packet['frames'] if start<=f['offset']<end]
        flows={}
        for f in rows:
            if f.get('protocol')!=6 or 21 not in [f['source_port'],f['destination_port']]:continue
            port=f['source_port'] if f['destination_port']==21 else f['destination_port'];flow=flows.setdefault(port,dict(port=port))
            t=f['seconds']+f['microseconds']/1e6
            if f['destination_port']==21 and f['tcp_flags']==2:flow.setdefault('syn',t)
            if f['destination_port']==21 and f['tcp_flags']&1:flow.setdefault('fin',t)
            if f.get('ftp_greeting_part'):flow.setdefault('greeting',t)
            if f.get('ftp_greeting_ready'):flow.setdefault('ready',t)
        completed=[]
        for f in flows.values():
            if 'syn' in f and 'greeting' in f:
                f['greeting_delay_seconds']=round(f['greeting']-f['syn'],6)
                f['host_closed_before_greeting']=f.get('fin',float('inf'))<f['greeting'];completed.append(f)
        text=trace[ts:te].decode('ascii',errors='replace');nvnet=[l for l in text.splitlines() if l.startswith('nvnet_')]
        counts=collections.Counter(l.split()[0] for l in nvnet)
        bmsr=[int(v,16) for v in re.findall(r'nvnet_phy_reg_read phy 1 addr 0x1 MII_BMSR val 0x([0-9a-f]+)',text)]
        pairs=[]
        for request in [d for d in dhcp if d['type']==3]:
            acks=[d for d in dhcp if d['type']==5 and d['xid']==request['xid'] and d['client_mac']==request['client_mac'] and d['offset']>request['offset']]
            if acks:pairs.append(dict(request=request,ack=acks[0]))
        phases[name]=dict(frame_count=len(rows),dhcp=dhcp,request_ack_pairs=pairs,nvnet_event_counts=dict(counts),
                          bmsr_values=bmsr,receive_unavailable=[l for l in nvnet if l.startswith('nvnet_cant_rx')],
                          ftp_greeting_flows=completed)
    report=dict(case=case,pcap_sha256=sha(run/'nvnet.pcap'),trace_sha256=sha(run/'cpu-trace.log'),
                reset_sha256=sha(out/'reset.json'),pcap_bytes=len(raw),trace_bytes=len(trace),complete_records=True,
                phases=phases,limits='ACK capture and receive counts alone do not pair an exact packet to guest DMA. Fresh FTP success and subsequent guest traffic are separate evidence.',
                decoder_sha256=sha(Path(__file__).with_name('packets.py')),analyzer_sha256=sha(Path(__file__)))
    p=out/'network.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    root=k if len(sys.argv)==1 else Path(sys.argv[1]).resolve()
    for case in ['control001','candidate001']:
        r=analyze(root,case);print(case,{p:(v['frame_count'],len(v['request_ack_pairs']),len(v['ftp_greeting_flows'])) for p,v in r['phases'].items()})
