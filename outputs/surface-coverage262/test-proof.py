"""Independent synthetic streams, explicitly not guest preservation evidence."""
import copy,hashlib,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('proof262',k/'lifecycle-proof.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def nv(p,t,ref,a,b):return f'nv2a_lifecycle244 phase={p} when={t} thread=7 ref={ref} a={a} b={b}\n'
def cpu(p,t,ref):return f'xwn_mem_callback244 phase={p} when={t} thread={7 if p in [1,3] else 8} ref={ref} addr=9000 len=704 stopped=0\n'
def group(seq,t,site,flags,ref=222,surface=444):
    parts=[(site,flags),(surface,ref),(1048576+4096,704),(55,0),(0,0),(0,0),(0,0)]
    return ''.join(nv(100+i,t,seq,*v) for i,v in enumerate(parts))
trace={'checkpoints':[]}
for n,(start,end,ref,surface) in enumerate([(10,20,111,333),(30,40,222,444),(50,60,222,444),(70,80,222,444)],1):
    fields=dict(reason=0,result=0,callback_result=0,unknown_vertex=0,cpu0_done=1,cpu1_done=1,cpu0_reason=0,cpu1_reason=0,started=start,finished=end,surface=surface,callback=ref,worker=7)
    trace['checkpoints'].append(dict(stage=n,attestation=dict(passed=True,physical=1048576),state=5,renderer_report=' '.join(f'slot{n}_{name}={v}' for name,v in fields.items())))
text=''.join(cpu(p,t,111) for p,t in [(1,10),(2,11),(3,17),(4,18),(5,19)])
text+=''.join(nv(p,t,111,1052672,704) for p,t in [(1,12),(2,16),(3,20)])
text+=group(1,14,2,1,111,333)+group(2,15,6,0,111,333)
text+=''.join(cpu(p,t,222) for p,t in [(1,30),(2,31),(3,68),(4,69),(5,70)])
text+=''.join(nv(p,t,222,1052672,704) for p,t in [(1,32),(2,67),(3,71)])
text+=group(3,45,11,1)+group(4,65,12,1)+group(5,66,3,8)+group(6,67,6,8)
assert m.prove(text.encode(),trace,True)['full_callback_lifecycle_passed']
checks=[]
def rejects(name,data,t=trace):
    try:m.prove(data.encode(),t,True)
    except (AssertionError,KeyError,ValueError):checks.append(name)
    else:raise AssertionError('negative accepted: '+name)
for ref,times in [(111,[(1,10),(2,11),(3,17),(4,18),(5,19)]),(222,[(1,30),(2,31),(3,68),(4,69),(5,70)])]:
    for p,t in times:rejects(f'missing-cpu-{ref}-{p}',text.replace(cpu(p,t,ref),''))
for ref,times in [(111,[(1,12),(2,16),(3,20)]),(222,[(1,32),(2,67),(3,71)])]:
    for p,t in times:rejects(f'missing-renderer-{ref}-{p}',text.replace(nv(p,t,ref,1052672,704),''))
for site,seq,t in [(3,5,66),(6,6,67)]:
    for flags in [0,1,2,4,9,10,12,15]:
        rejects(f'bad-state-{site}-{flags}',text.replace(group(seq,t,site,8),group(seq,t,site,flags)))
for seq,t,site in [(3,45,11),(4,65,12)]:rejects(f'no-dirty-{site}',text.replace(group(seq,t,site,1),group(seq,t,site,0)))
rejects('wrong-address',text.replace('a=1052672 b=704','a=1052673 b=704'))
rejects('duplicate-free',text+cpu(5,70,222))
rejects('malformed-line',text+'nv2a_lifecycle244 phase=oops\n')
bad=copy.deepcopy(trace);bad['checkpoints'][3]['renderer_report']=bad['checkpoints'][3]['renderer_report'].replace('slot4_result=0','slot4_result=1');rejects('GL-result-failed',text,bad)
for site in m.sites.SITES:
    cap=4096 if site==11 else 256
    stream=''.join(group(i+1,i+1,site,0) for i in range(cap))
    assert m.sites.parse(stream.encode())['groups']==cap
    parsed=m.sites.parse((stream+nv(99,cap+1,site,cap,0)).encode());assert parsed['truncated_sites']==[site]
    try:m.sites.parse((stream+group(cap+1,cap+1,site,0)).encode())
    except AssertionError:checks.append(f'over-cap-{site}')
    else:raise AssertionError('overcapacity accepted')
    try:m.sites.parse((stream+nv(99,cap+1,site,cap,0)*2).encode())
    except AssertionError:checks.append(f'duplicate-overflow-{site}')
    else:raise AssertionError('duplicate marker accepted')
# Actual261 remains rejected, without editing its original raw data or parser.
raw=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/residency261/runs/nt5-residency261-emu001/cpu-trace.log')
try:m.sites.parse(raw.read_bytes())
except AssertionError:checks.append('historical261-incompatible-truncation-rejected')
else:raise AssertionError('historical truncated stream accepted')
dest=k/'proof-tests.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,synthetic_only=True,positive_full_lifecycle=True,negative_controls=checks,site_limits=m.sites.LIMITS,sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),k/'lifecycle-proof.py',k/'analyze-sites.py']},pixel_preservation_proved=False,physical_access=False),indent=2)+'\n')
print('262 synthetic proof and capacity controls:',len(checks),'negative controls')
