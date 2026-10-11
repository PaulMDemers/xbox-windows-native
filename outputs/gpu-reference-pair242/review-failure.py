"""Verify CLOSED242 raw observations while preserving original qualification failure."""
import hashlib,json
from pathlib import Path
from schema import parse,qualify
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in read(k/'emulator-frozen.json').items():assert sha(ws/p)==h,p
m=read(k/'matrix001.json');state=read(k/'preserve001/host-state.json');t=read(k/'preserve001/trace.json');a=read(k/'preserve001/audit.json');al=read(k/'preserve001/allocation.json')
assert m['closed'] and not m['completed'] and state['closed'] and state['audit_exit_code']==0
assert not t['passed'] and t['closed'] and t['guest_resumed'] and not t['remaining_breakpoints'] and t['physical_mode_restored']
assert 'not any(s[\'stats\'][1:7])' in t['host_traceback']
p=t['preservation'];result=p['result'];assert result['state']==3 and result['downloaded']==3 and result['bytes']==3072000 and not result['reason'] and not result['error']
v=parse(p['paired_inventory_reply']);assert v==p['paired_inventory'] and p['paired_inventory_immutable']
try:qualify(v,t['phase_snapshot']['tuple'])
except AssertionError:pass
else:raise AssertionError('Original frozen qualifier must remain failed')
first,last=v['slots'];pre=t['phase_snapshot']['tuple'];assert all(s['valid'] for s in [first,last])
assert first['fifo_when']<=first['when']<=last['when']<=last['fifo_when']
assert first['surfaces']==pre['surfaces'] and first['context']==last['context']==pre['context']
assert first['fifo']==last['fifo']==[1]+pre['current_fifo'][1:]
assert first['stats']==last['stats'] and first['textures']==last['textures'] and first['bindings']==last['bindings']
assert first['stats'][3]==last['stats'][3]==pre['current_pg_only'][5]==0xffffffff
assert not any(first['stats'][i] for i in [1,2,4,5,6])
for old,new in zip(first['surfaces'],last['surfaces']):assert old[:5]==new[:5] and old[6:]==new[6:] and old[5]&3 and not new[5]&3 and old[5]&~3==new[5]&~3
assert a['cpu_scope_passed'] and a['observation_scope_passed'] and a['integrity_passed'] and not a['guest_trace_scope_passed']
assert a['normal_shutdown_count']==1 and a['dashboard_return'] and a['orderly_host_exit_passed']
assert [(r['source'],r['event_id'],r['type']) for r in a['warnings_errors']]==[('Ftdisk',49,1)] and not a['new_events']['application']
assert not a['strict_qualification_passed'] and not al['errors'] and not al['orphan_cluster_count'] and al['allocation_consistent']
assert len(t['events'])==1 and t['events'][0]['resident_bytes_match'] and t['events'][0]['registers'][8]==0x11100
assert sha(ws/t['events'][0]['pin']['path'])==t['events'][0]['pin']['sha256']
assert not p['ram'] and not any(c['command'].startswith('pmemsave ') for c in t['monitor'])
dest.write_text(json.dumps(dict(passed=True,review_kind='negative evidence retention, not requalification',original_trace_passed=False,paired_inventory_scope_passed=False,raw_inventory_consistency_checked=True,reason='Frozen host qualifier incorrectly classified enabled-interrupt mask as pending work; original failure unchanged',trace_sha256=sha(k/'preserve001/trace.json'),audit_sha256=sha(k/'preserve001/audit.json'),matrix=m,allocation={key:al[key] for key in ['directories','files','directory_clusters','orphan_cluster_count']},observed=dict(callbacks=3,texture_units=4,texture_cache=24,shaders=53,shader_save_handles=53,modules=53,elements=93),strict_qualified=False,physical_access=False,native_gpu_ownership=False),indent=2)+'\n',encoding='utf-8')
print('242 CLOSED failed verifier and actual raw/cold evidence reviewed, no retroqualification')
