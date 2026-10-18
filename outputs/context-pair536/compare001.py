"""Read-only comparison of the two completed physical536 captures."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def differences(a,b,path=''):
    if type(a)!=type(b):return [dict(path=path,warm=a,cold=b)]
    if isinstance(a,dict):
        result=[]
        for key in sorted(a.keys()|b.keys()):result+=differences(a.get(key),b.get(key),path+'/'+key)
        return result
    if isinstance(a,list):
        result=[]
        if len(a)!=len(b):result.append(dict(path=path+'/length',warm=len(a),cold=len(b)))
        for i,(x,y) in enumerate(zip(a,b)):result+=differences(x,y,path+'/'+str(i))
        return result
    return [] if a==b else [dict(path=path,warm=a,cold=b)]

out=K/'comparison001.json';assert not out.exists()
pins={};cases=[];decoded=[]
for i in (1,2):
    docs={n:read(K/f'{n}{i}.json') for n in ['before','after','audit','decoded','observer','ready','launch']}
    for n in docs:pins[str(K/f'{n}{i}.json')]=sha(K/f'{n}{i}.json')
    before,after,a,d,o=[docs[n] for n in ['before','after','audit','decoded','observer']]
    assert before['completed'] and after['completed'] and a['closed'] and a['hives_clean']
    assert after['ordinary_code_exact'] and not after['remote_writes'] and not after['temporary_hook_installed']
    assert o['windows_desktop_observed'] and o['at_dashboard'] and not o['forced_reset_reported']
    assert d['closed'] and not d['errors'] and all(d['present'][n] for n in ['report.bin','handoff.bin','context.bin'])
    assert not d['present']['refusal.bin']
    for phase in (before,after):
        for row in phase['files'].values():
            p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'];pins[str(p)]=row['sha256']
    for row in after['receipts'].values():
        if row:
            p=Path(row['path']);assert sha(p)==row['sha256'];pins[str(p)]=row['sha256']
    ev=a['events']['system'];new=ev['new_records']
    cases.append(dict(ordinal=i,predecessor='warm after534 Windows Restart' if i==1 else 'user-reported poweroff10seconds/on',
        desktop_user_observed=True,dashboard_user_observed=True,hives_clean=a['hives_clean'],ordinary_code_exact=a['ordinary_code_exact'],
        normal_shutdown_delta=ev['normal_shutdown_delta'],new_event_counts={f'{source}:{event}':sum(r['source']==source and r['event_id']==event for r in new) for source,event in [('EventLog',6005),('EventLog',6006),('Ftdisk',49),('Application Popup',26)]},
        receipt_hashes={n:None if row is None else row['sha256'] for n,row in after['receipts'].items()}))
    decoded.append(d)
    if i==1:first_after=after
    else:assert all(row['sha256']==first_after['files'][n]['sha256'] for n,row in before['files'].items())
all_diff=differences(*decoded)
expected={'/ordinal','/handoff.bin/preceding_marker/polls','/handoff.bin/preceding_marker/tsc_start','/handoff.bin/preceding_marker/tsc_end'}
expected|={f'/context.bin/records/{i}/tsc_{edge}' for i in (0,1) for edge in ('start','end')}
assert {r['path'] for r in all_diff}==expected
fields=['eflags','cr0','cr2','cr3','cr4','selectors','gdtr','idtr','entry_esp','return_eip']
epochs=[]
for index in (0,1):
    a,b=[d['context.bin']['records'][index] for d in decoded]
    assert all(a[n]==b[n] for n in fields)
    epochs.append(dict(epoch=index+1,meaning='before witness write' if index==0 else 'after witness close, before context packet IO',equal_fields={n:a[n] for n in fields},direction_flag=bool(a['eflags']&0x400),interrupt_flag=bool(a['eflags']&0x200)))
assert decoded[0]['report.bin']==decoded[1]['report.bin']
assert cases[0]['receipt_hashes']['report.bin']==cases[1]['receipt_hashes']['report.bin']
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cases=cases,all_decoded_differences=all_diff,
    primary_preparation_raw_and_decoded_identical=True,matched_epochs=epochs,predecessor_memory_contents_not_measured=True,
    ordinary_failure_reproduced=False,boot_fix_established=False,device_or_final_handoff_state_proved=False,
    conclusion='Both instrumented boots succeeded; equal observed CPU/preparation fields do not identify the ordinary-launch failure. Instrumentation changes layout, memory use, IO and timing.',
    limitations=['Recorded contexts precede their own packet IO and final handoff','No page-table walk or descriptor-content validation','No device/cache/interrupt-controller state comparison','Event scan may include stale records outside active ring','Ftdisk49 and shutdown Popup26 remain in both cases','No GPU/game/release promotion'],pins=pins,source_sha256=sha(Path(__file__)))
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(cases=cases,difference_paths=[r['path'] for r in all_diff],primary_identical=True)))
