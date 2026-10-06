"""Extract the observed two-thread FATX lock cycle without claiming old failures proven."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;p=k/'001/timeout-analysis.json';a=json.loads(p.read_text())
waits={w['thread']:w for w in a['resource_waits'] if w['process']=='concurrent.exe'}
cycle=a['exclusive_cycles'][0];assert len(cycle)==2
rows=[]
for edge in cycle:
    w=waits[edge['waiter']];r=w['resource'];assert r['address']==edge['resource'] and r['owners'][0]['thread']==edge['owner']
    t=next(t for proc in a['processes'] for t in proc['threads'] if t['thread']==edge['waiter'])
    rows.append(dict(thread=edge['waiter'],tid=t['tid'],waiting_for=r['address'],resource=r['fatx'],owner=edge['owner'],fatx_code_candidates=[x for x in t['stack_code_candidates'] if x['candidate'].startswith('xwnfatx.sys+')]))
proc=next(p for p in a['processes'] if p['image']=='concurrent.exe')
r=dict(scope=__doc__,snapshot_report_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),observed_exclusive_cycle=True,cycle=rows,
       counters=proc['diagnostic_counters'],helper_sha256=proc['diagnostic_binary_sha256'],normal_shutdown=False,
       interpretation='Cleanup owns DirResource and waits for worker0.bin MainResource; volume flush owns that same MainResource and waits for DirResource. This snapshot proves the cycle in concurrency001.',
       limits='Does not retrospectively prove the lost-snapshot shutdown stall or all physical freezes had this cause. Driver fix and regression qualification remain pending.')
target=k/'001/deadlock-summary.json';assert not target.exists();target.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
