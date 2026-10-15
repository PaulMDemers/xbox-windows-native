"""Read-only collection after the user returns from the manual media demo."""
import subprocess,sys
from physical import K,W,PRIVATE,connect,get,sha,utc,ticket,read,write_json,installed,START,PLAYER

ticket()
assert read(K/'launch.json')['launch_requested']
assert read(K/'stage002.json')['completed']
dest=K/'collection.json';assert not dest.exists()
out=PRIVATE/'after';assert not out.exists()
r=dict(completed=False,started_utc=utc(),console_writes=False,console_C_accessed=False,
       files={},events={},physical_playback_requires_user_report=True,full_allocation_audit=False)
with connect() as f:
    out.mkdir();write_json(dest,r)
    expected=installed()
    expected[PLAYER]=read(K/'before.json')['files'][PLAYER]['sha256']
    expected.update({p:v['sha256'] for p,v in read(K/'stage002.json')['verified'].items()})
    for p,h in expected.items():
        data=get(f,p);r['files'][p]=dict(bytes=len(data),sha256=sha(data),matches=sha(data)==h)
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        remote='/E/winnt/system32/config/'+name
        data=get(f,remote);target=out/remote.lstrip('/');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        phases={}
        for phase in ['before','after']:
            raw=PRIVATE/phase/remote.lstrip('/');result=PRIVATE/phase/(label+'-events.json')
            assert not result.exists()
            subprocess.run([sys.executable,'-B',str(W/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(raw),'--output',str(result)],check=True,stdout=subprocess.DEVNULL)
            phases[phase]=read(result)['records']
        old,new=phases['before'],phases['after'];by={v['record']:v for v in new}
        boundary=max((v['record'] for v in old),default=0)
        r['events'][label]=dict(history_preserved=all(by.get(v['record'])==v for v in old),new=[v for v in new if v['record']>boundary])
r['protected_and_demo_files_exact']=all(v['matches'] for v in r['files'].values())
delta=[v for phase in r['events'].values() for v in phase['new']]
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in delta)
r['warning_error_events']=[v for v in delta if v['type'] in [1,2]]
r.update(completed=True,completed_utc=utc(),strict_clean_install_qualified=False)
write_json(dest,r)
print('407 read-only collection complete; protected/demo exact:',r['protected_and_demo_files_exact'])
