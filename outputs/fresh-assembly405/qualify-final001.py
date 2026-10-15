import copy,hashlib,json
from pathlib import Path
from qualification001 import qualify
K=Path(__file__).resolve().parent
paths=['emu006/audit.json','emu006/launch.json','emu006/network-host.json','assembly006.json','assembly001.json']
args=[json.loads((K/p).read_text()) for p in paths]
original=qualify(*args);assert original['fresh_xbox_functional_scoped_pass'] and not original['strict_qualification']
assert original['unrepresentable_paths']==8
cases=[]
def reject(name,alter):
    values=copy.deepcopy(args);alter(values)
    assert not qualify(*values)['fresh_xbox_functional_scoped_pass'],name;cases.append(name)
reject('audio missing',lambda a:a[0]['witness'].update(WAVE_DEVICES=0))
reject('wrong mode',lambda a:a[0]['witness'].update(WIDTH=640))
reject('drawing failed',lambda a:a[0]['witness'].update(MEMORY_GDI=0))
reject('short network',lambda a:a[2].update(rounds=31))
reject('duplicate launch',lambda a:a[1]['cycles'].append(copy.deepcopy(a[1]['cycles'][0])))
reject('host kill',lambda a:a[0]['host_exit'].update(fallback_kill=True))
reject('orphan',lambda a:a[0]['allocation'].update(orphan_cluster_count=1))
reject('missing hive',lambda a:a[0]['hives'].pop())
reject('wrong protected bytes',lambda a:a[0]['protected'][0].update(after='00'*32))
reject('old Windows payload',lambda a:a[4].update(old_windows_payload_used=True))
reject('startup still active',lambda a:a[3].update(diagnostic_startup_absent=False))
reject('lost event history',lambda a:a[0]['checks'].update(event_history_preserved=False))
reject('cold persistence mismatch',lambda a:a[0]['checks'].update(cold_exact_data=False))
reject('missing normal shutdown',lambda a:[v.update(new=[r for r in v['new'] if r['event_id']!=6006]) for v in a[0]['events'].values()])
result=dict(**original,actual_mutations_rejected=cases,inputs={p:hashlib.sha256((K/p).read_bytes()).hexdigest() for p in paths})
with (K/'qualification001.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
