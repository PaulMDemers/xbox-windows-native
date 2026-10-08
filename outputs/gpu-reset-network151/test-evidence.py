"""Negative checks for packet truncation and DHCP/link evidence identity."""
import copy,importlib.util,json,struct
from pathlib import Path
from packets import decode
k=Path(__file__).resolve().parent;ws=k.parents[1]
s=importlib.util.spec_from_file_location('series',k/'verify-series.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
checks=[]
for case in ['control001','candidate001']:
    data=(ws/'work/runs'/('gpu-reset-network151-'+case)/'nvnet.pcap').read_bytes()
    for name,bad in [('tail_truncated',data[:-1]),('header_truncated',data[:23]),('wrong_magic',b'xxxx'+data[4:])]:
        try:decode(bad)
        except AssertionError:checks.append(case+':'+name)
        else:raise AssertionError('Malformed capture accepted: '+name)
    n=json.loads((k/case/'network.json').read_text())
    for name in ['missing_ack','wrong_xid','wrong_mac','wrong_address','no_rx','link_down']:
        bad=copy.deepcopy(n);p=bad['phases']['reset_return'];pair=p['request_ack_pairs'][0]
        if name=='missing_ack':p['request_ack_pairs']=[]
        elif name=='wrong_xid':pair['ack']['xid']^=1
        elif name=='wrong_mac':pair['ack']['client_mac']='00:00:00:00:00:00'
        elif name=='wrong_address':pair['ack']['offered_address']='10.0.2.16'
        elif name=='no_rx':p['nvnet_event_counts']['nvnet_rx_dma']=0
        else:p['bmsr_values']=[0]
        try:m.network_gate(bad)
        except AssertionError:checks.append(case+':'+name)
        else:raise AssertionError('Invalid network evidence accepted: '+name)
p=k/'evidence-tests.json';assert not p.exists();p.write_text(json.dumps(dict(passed=True,checks=checks),indent=2)+'\n')
print(len(checks),'negative network evidence checks passed')
