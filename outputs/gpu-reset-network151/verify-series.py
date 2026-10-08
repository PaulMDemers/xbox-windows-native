"""Qualify fresh reset evidence while preserving the recorded151 FTP failure."""
import hashlib,importlib.util,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-surface-history'));from lifecycle import parse
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
reset=load('reset_verify',ws/'outputs/gpu-reset150/verify.py');overlap=reset.overlap
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def network_gate(n):
    assert n['complete_records'] and n['pcap_bytes']<=16*1024*1024 and n['trace_bytes']<=16*1024*1024
    for phase in n['phases'].values():
        assert len(phase['request_ack_pairs'])==1
        pair=phase['request_ack_pairs'][0];req,ack=pair['request'],pair['ack']
        assert req['type']==3 and ack['type']==5 and req['xid']==ack['xid'] and req['client_mac']==ack['client_mac']
        assert req['offset']<ack['offset'] and req['requested_address']==ack['offered_address']=='10.0.2.15'
        assert phase['nvnet_event_counts'].get('nvnet_rx_dma',0)>0 and phase['nvnet_event_counts'].get('nvnet_packet_tx',0)>0
        assert phase['bmsr_values'] and all(v&4 for v in phase['bmsr_values'])
def main(root):
    target=root/'verification.json';assert not target.exists();results={}
    build=read(ws/'outputs/xemu-cpu-surface-evict/build003/build.json')
    for case in ['control001','candidate001']:
        out=root/case;run=ws/'work/runs'/(root.name+'-'+case);assert (run/'cleanup.json').exists()
        a=read(out/'audit.json');r=read(out/'reset.json');data=(run/'cpu-trace.log').read_bytes();n=read(out/'network.json')
        digest=next(b['sha256'] for b in build['builds'] if b['case']==case[:-3]);assert read(run/'instance.json')['sourceSha256'].lower()==digest
        before=(out/'before-reset-trace.log').read_bytes();assert data[:len(before)]==before and sha(out/'before-reset-trace.log')==r['before_reset_trace_sha256']
        assert a['protocol_passed'] and a['exact_pixels_passed'] and a['allocation_passed'] and a['entire_f_unchanged'] and not a['changed_existing_e_files'] and a['new_files_exact']
        transitions=reset.reset_evidence(r,data)
        events=[e for e in parse(data) if e['offset']>=r['after_reset']['trace_offset']]
        lifecycle=overlap.verify(events,a['phases']['149']['surfaces'],case.startswith('candidate'))
        network_gate(n)
        expected=not (root.name=='gpu-reset-network151' and case=='candidate001');assert a['cold_passed']==expected
        if expected:
            assert r['dashboard_return'] and r['offline_after_second_launch'] and not r.get('failed')
            assert r['reset_command_completed_utc']<r['reset_dashboard_utc']<=r['after_reset']['requested_utc']<r['returned_utc']
        else:
            assert r['failed'] and r['error']=="RuntimeError('Post-reset run did not return')"
            flows=n['phases']['probe_return']['ftp_greeting_flows'];assert len(flows)==40
            assert all(f['host_closed_before_greeting'] and f['greeting_delay_seconds']>2 for f in flows)
        results[case]=dict(cold_passed=expected,reset_lifecycle=transitions,post_reset_lifecycle=lifecycle,
            network_sha256=sha(out/'network.json'),pcap_sha256=sha(run/'nvnet.pcap'),trace_sha256=sha(run/'cpu-trace.log'),
            emulator_sha256=digest,audit_sha256=sha(out/'audit.json'))
    assert read(root/'control001/audit.json')['files']==read(root/'candidate001/audit.json')['files']
    for name,digest in read(root/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
    target.write_text(json.dumps(dict(evidence_verified=True,matched_pair_passed=root.name=='gpu-reset-banner152',
        results=results,verifier_sha256=sha(Path(__file__)),physical_qualified=False,windows_qualified=False,
        performance_qualified=False,old150_network_failure_cause_proven=False),indent=2)+'\n')
    print(root.name,'evidence verified; strict matched pair',root.name=='gpu-reset-banner152')
if __name__=='__main__':main(k if len(sys.argv)==1 else Path(sys.argv[1]).resolve())
