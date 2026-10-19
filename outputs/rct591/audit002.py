"""Independent cold hive/event review per ordinal, run under WSL; no network."""
import hashlib,json,sys,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(s):return Path('/mnt/'+s[0].lower()+s[2:].replace(chr(92),'/')) if len(s)>2 and s[1]==':' else Path(s)
assert len(sys.argv)==2 and sys.argv[1] in ('1',);ordinal=int(sys.argv[1])
out=K/f'audit{ordinal}.json';assert not out.exists()
before=read(K/'stage001.json');after=read(K/'collection001.json')
before['files']=before['before']
assert before['completed'] and after['completed'] and after['protected_code_exact']
assert after['hook_removed']
assert after['remote_writes']==[dict(action='rename-owned-hook',source='/E/documents and settings/all users/start menu/programs/startup/xwn591.cmd',destination='/E/xwn586-kit/startup-used591.cmd')]
for group in [before,after]:
    for n,row in group['files'].items():
        p=host(row['path']);assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],n
for n in ['/E/Applications/XWNEBoot/default.xbe','/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd']:
    assert before['files'][n]['sha256']==after['files'][n]['sha256']
hives={};events={}
for name in ['system','software','sam','security','default']:
    n='/E/winnt/system32/config/'+name
    hives[name]={phase:audit(host(group['files'][n]['path'])) for phase,group in [('before',before),('after',after)]}
clean=all(v['clean'] and v['header_valid'] and v['independent_raw_values_agree'] for h in hives.values() for v in h.values())
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
    parsed={}
    for phase,group in [('before',before),('after',after)]:
        p=host(group['files']['/E/winnt/system32/config/'+name]['path'])
        dest=p.with_name(f'{label}-audit591-{ordinal}-{phase}.json');assert not dest.exists()
        subprocess.run([sys.executable,'-B',str(K.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL,timeout=60)
        parsed[phase]=read(dest)['records']
    boundary=max((r['record'] for r in parsed['before']),default=0)
    new=[r for r in parsed['after'] if r['record']>boundary]
    events[label]=dict(new_records=new,normal_shutdown_delta=sum(r['source']=='EventLog' and r['event_id']==6006 for r in parsed['after'])-sum(r['source']=='EventLog' and r['event_id']==6006 for r in parsed['before']),scope='Validated record scan may include stale records outside active ring; sequence-boundary delta, not active-ring completeness')
r=dict(closed=True,ordinal=ordinal,hives_clean=clean,hives=hives,events=events,ordinary_code_exact=True,
       before_sha256=sha(K/'stage001.json'),after_sha256=sha(K/'collection001.json'),
       changed_files=[n for n,row in before['files'].items() if row['sha256']!=after['files'][n]['sha256']],
       console_C_accessed=False,temporary_hook_installed=False,whole_allocation_audit=False,source_sha256=sha(Path(__file__)))
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({n:r[n] for n in ['closed','ordinal','hives_clean','changed_files']}));assert clean
