"""Close539 using its one fresh capture and retained536 evidence; no network."""
import collections,datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists()
q=read(K/'package001.json')
for p,h in q['pins'].items():assert sha(Path(p))==h,p
before=read(K/'before1.json');after=read(K/'after1.json');audit=read(K/'audit1.json')
d=read(K/'decoded1.json');obs=read(K/'observer1.json');launch=read(K/'launch1.json')
assert before['completed'] and after['completed'] and audit['closed'] and audit['hives_clean']
assert d['closed'] and not d['errors'] and d['report.bin']['preparation_verified']
assert obs['at_dashboard'] and obs['user_report_received'] and not obs['boot_sequence_observed']
assert launch['requested'] and launch['image_sha256']==q['images']['1']['sha256']
assert not (K/'launch2.json').exists()
assert set(before['files'])==set(after['files'])
for n,row in after['files'].items():
    assert sha(Path(row['path']))==row['sha256']
    assert row['sha256']==before['files'][n]['sha256'],n
for row in after['receipts'].values():
    if row is not None:assert sha(Path(row['path']))==row['sha256']
assert d['present']=={'report.bin':True,'handoff.bin':True,'context.bin':True,'refusal.bin':False}
counts=collections.Counter(f"{e['source']}:{e['event_id']}" for v in audit['events'].values() for e in v['new_records'])
assert not counts and not audit['changed_files']
assert all(v['normal_shutdown_delta']==0 for v in audit['events'].values())
def differences(a,b,path=''):
    if type(a)!=type(b):return [dict(path=path,prior=a,current=b)]
    if isinstance(a,dict):
        return [x for k in sorted(a.keys()|b.keys()) for x in differences(a.get(k),b.get(k),path+'/'+k)]
    if isinstance(a,list):
        if len(a)!=len(b):return [dict(path=path,prior=a,current=b)]
        return [x for i,(v,w) in enumerate(zip(a,b)) for x in differences(v,w,path+'/'+str(i))]
    return [] if a==b else [dict(path=path,prior=a,current=b)]
comparisons=[]
for i in (1,2):
    p=K.parent/f'context-pair536/decoded{i}.json';prior=read(p)
    delta=[]
    for name in ('report.bin','handoff.bin','context.bin'):
        delta+=differences(prior[name],d[name],'/'+name)
    prior_after=read(K.parent/f'context-pair536/after{i}.json')
    comparisons.append(dict(prior_closed_case=f'536-{i}',source_sha256=sha(p),
        primary_raw_equal=prior_after['receipts']['report.bin']['sha256']==after['receipts']['report.bin']['sha256'],
        all_packet_differences=delta,physical_recollection=False))
states={}
for name in ('stage','before1','launch1','after1'):
    row=read(K/f'supervisor-{name}.json');assert row['closed'] and row['completed'] and row['exit_code']==0
    states[name]={key:row[key] for key in ('pid','closed','completed','exit_code','deadline_reached','finished_utc')}
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),launch_count=1,
    repeated_launch_allowed=False,console_state='User-confirmed dashboard, authenticated after1 collection completed',
    observation=obs,baseline_file_count=10,all_baseline_files_identical=True,hives_clean=True,
    new_event_counts=dict(counts),normal_shutdown_delta=0,preparation_verified=True,
    primary_witness_context_present=True,refusal_present=False,comparisons_to_successful536= comparisons,
    physical_post_stack_execution_proved=False,windows_execution_proved=False,normal_restart_proved=False,
    cause_established=False,ordinary_boot_fix_established=False,
    interpretation='Unobserved return; recorder reached pre-handoff checkpoints, but no Windows startup/shutdown or video-trace change. This is not a qualified Windows boot or proof of where it failed.',
    no_temporary_hook=True,console_C_accessed=False,protected720p_ordinary_startup_exact=True,
    all_owned_supervisors_closed=True,supervisors=states,automation='PAUSED',
    evidence_sha256={name:sha(K/name) for name in ('before1.json','after1.json','audit1.json','decoded1.json','observer1.json','launch1.json','package001.json')},
    source_sha256=sha(Path(__file__)))
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(closed=True,new_events=dict(counts),all10_baseline_files_identical=True,
    comparisons=[dict(prior=v['prior_closed_case'],primary_raw_equal=v['primary_raw_equal'],differences=v['all_packet_differences']) for v in comparisons])))
