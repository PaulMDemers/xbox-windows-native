import copy,hashlib,json
from pathlib import Path
from trace_analysis import analyze
K=Path(__file__).resolve().parent;out=K/'candidate001';dest=out/'trace-verification001.json';assert not dest.exists()
p=out/'trace.json';trace=json.loads(p.read_text());result=analyze(trace);checks=0
def reject(t):
    global checks
    try:analyze(t)
    except (AssertionError,KeyError,ValueError,IndexError,TypeError):checks+=1
    else:raise AssertionError('Mutated observation accepted')
for oi,op in enumerate(trace['operations']):
    for ci,c in enumerate(op['calls']):
        for field in ['thread','process','expected_return_sp','return_address','result']:
            t=copy.deepcopy(trace);t['operations'][oi]['calls'][ci][field]^=4;reject(t)
        t=copy.deepcopy(trace);t['operations'][oi]['calls'][ci]['returned']=False;reject(t)
        if c['label']=='primary':
            for coord in range(4):
                t=copy.deepcopy(trace);t['operations'][oi]['calls'][ci]['rect'][coord]+=1;reject(t)
            for index in range(len(c['owner_results'])):
                t=copy.deepcopy(trace);t['operations'][oi]['calls'][ci]['owner_results'][index]['value']^=4;reject(t)
            t=copy.deepcopy(trace);t['operations'][oi]['calls'][ci]['copied_bytes']+=4;reject(t)
            for side in ['destination','source']:
                t=copy.deepcopy(trace);t['operations'][oi]['calls'][ci][side]['type']^=1;reject(t)
for name,value in [('pending_calls',1),('armed_breakpoints_remaining',[1]),('physical_mode_restored',False),('guest_resumed',False),('guest_memory_writes',True),('guest_register_writes',True),('completed_intervals',[12])]:
    t=copy.deepcopy(trace);t[name]=value;reject(t)
result.update(trace_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),actual_mutations_rejected=checks,inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),K/'trace_analysis.py']})
dest.write_text(json.dumps(result,indent=2)+'\n');print('Scoped call/geometry accounting PASS;',checks,'actual mutations rejected')
