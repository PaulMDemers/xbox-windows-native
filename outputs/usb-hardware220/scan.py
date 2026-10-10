"""Owned E-only launches of the validated read-only F allocation snapshot application."""
import argparse,ftplib,json,subprocess,sys,time
import physical as m

p=argparse.ArgumentParser();p.add_argument('phase',choices=['before','after','restored'])
p.add_argument('action',choices=['launch','observe','collect','analyze']);args=p.parse_args()
phase=args.phase
remote='/E/Applications/XWNU220Scan'+dict(before='B',after='A',restored='R')[phase]
record=m.K/(phase+'-scan.json');folder=m.ART/(phase+'-allocation')
source=m.CANON/'outputs/native-windows-fatx-preflight'
payload=(source/'artifacts/default.xbe').read_bytes()
assert m.sha(payload)=='c6c878447d2a5ace95fced0e6d7c819fd5271e665cd0fc8efe886c5232cbdf05'

def save(r):
    t=record.with_suffix('.tmp');t.write_text(json.dumps(r,indent=2)+'\n')
    for i in range(100):
        try:t.replace(record);return
        except PermissionError:
            if i==99:raise
            time.sleep(.05)

def verify(f):
    r=m.read(m.RECORD)
    assert m.get(f,m.STARTUP)==m.local(r['before'][m.STARTUP])
    for path in m.expected():assert m.get(f,path)==m.local(r['before'][path]),'Protected drift during scan'
    group='after' if phase=='after' else 'before'
    for n in m.HIVES:assert m.get(f,m.auxiliary()[n])==m.local(r[group][n]),'Hive drift during scan'

def launch():
    m.pins();assert not record.exists(),'Never repeat allocation scan launch'
    state=m.read(m.RECORD)
    assert state['capture_complete'] and not state['startup_enabled']
    if phase=='before':assert not state['launch_requested'] and m.read(m.K/'before-hive-audit.json')['passed']
    elif phase=='after':assert state.get('collected_utc') and not state['baseline_restored']
    else:assert state['baseline_restored']
    with m.connect() as f:
        verify(f);assert remote.rsplit('/',1)[1].lower() not in m.names(f,'/E/Applications')
        r=dict(phase=phase,scope=__doc__,remote=remote,payload_sha256=m.sha(payload),launch_requested=False,
               created_utc=m.utc(),physical_result=True,source_partition_read_only=True,output_partition='E')
        save(r);f.mkd(remote);m.put(f,remote+'/default.xbe',payload)
        r.update(launch_requested=True,launch_utc=m.utc(),command='SITE EXEC E:\\Applications\\'+remote.rsplit('/',1)[1]+'\\default.xbe');save(r)
        try:r['launch_reply']=f.sendcmd(r['command'])
        except ftplib.all_errors as e:r['launch_reply_uncertain']=type(e).__name__
        save(r)
    print('One read-only allocation launch recorded: '+phase,flush=True)

def observe():
    r=m.read(record);assert r['launch_requested'] and not r.get('collected')
    until=time.monotonic()+45
    while time.monotonic()<until:
        sample=dict(utc=m.utc(),dashboard=False,snapshot_complete=False)
        try:
            with m.connect(timeout=5) as f:
                sample['dashboard']=True;b=m.get(f,remote+'/snapshot.txt',optional=True)
                sample['snapshot_complete']=bool(b and b'SNAPSHOT_COMPLETE success=1 ' in b)
        except (OSError,EOFError,ftplib.Error) as e:sample['error_type']=type(e).__name__
        r.setdefault('observations',[]).append(sample)
        r['dashboard_return']=sample['dashboard'] and sample['snapshot_complete'];save(r)
        if r['dashboard_return']:print('Snapshot complete at owned dashboard: '+phase,flush=True);return
        time.sleep(5)
    print('Allocation observation bound reached; no repeat launch',flush=True)

def collect():
    m.pins();r=m.read(record);assert r['launch_requested'] and r.get('dashboard_return') and not r.get('collected')
    folder.mkdir(parents=True,exist_ok=True)
    with m.connect() as f:
        verify(f);assert m.get(f,remote+'/default.xbe')==payload;r['files']={}
        for n in ['snapshot.txt','fat-metadata.bin','directories.bin']:
            r['files'][n]=m.keep(phase+'-allocation/'+n,m.get(f,remote+'/'+n));save(r)
    r.update(collected=True,collected_utc=m.utc(),protected_and_hives_unchanged=True);save(r)
    print('Full physical F allocation metadata preserved: '+phase,flush=True)

def analyze():
    m.pins();r=m.read(record);assert r['collected'];dest=m.K/(phase+'-allocation.json');assert not dest.exists()
    for row in r['files'].values():m.local(row)
    subprocess.run([sys.executable,'-B',str(source/'analyze.py'),'--capture',str(folder),'--output',str(dest)],check=True)
    a=m.read(dest)
    assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count'],'Retain failed physical allocation audit'

globals()[args.action]()
