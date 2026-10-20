"""MIT. Preserve failed staging and draft bounded continuation without replaying writes."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
r=json.loads((K/'stage001.json').read_text());s=json.loads((K/'supervisor001-stage.json').read_text())
assert not r['completed'] and not r['temporary_hook_installed'] and s['closed'] and s['exit_code']==1
assert not (K/'launch001.json').exists()
assert len(r['asset_before'])==503 and len(r['staged'])==189
assert [x['action'] for x in r['writes']]==['mkdir','put','move-verified-retail-assets-only','restore-pristine-asset','restore-pristine-asset']
text=(K/'controller001.py').read_text().replace('package001.json','package002.json').replace('stage001.json','stage002.json')
start=text.index('def stage():');end=text.index('\n\ndef launch():',start)
text=text[:start]+text[end:]
start=text.index('def launch():');end=text.index('\ndef result_names',start)
text=text[:start]+'''def launch():
    q=verify();boot_work_closed();out=K/'launch001.json';assert not out.exists()
    st=read(K/'stage002.json');assert st['completed'] and st['temporary_hook_installed']
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');startup(f,True)
        assert 'xwn593' not in {n.lower() for n in m.names(f,'/E')}
        assert set(m.names(f,KIT))=={'owner.json','run593.exe','game'}
    check=K/'launch-preflight002.json';assert not check.exists()
    rec=dict(completed=False,verified={},remote_writes=[],launch_requested=False);m.write_json(check,rec)
    deadline=time.monotonic()+600
    for n,row in {**st['before'],**st['staged']}.items():
        assert time.monotonic()<deadline
        b=m.cold_pair(n,rec,check);assert b is not None and len(b)==row['bytes'] and m.sha(b)==row['sha256'],n
        rec['verified'][n]=row['sha256'];m.write_json(check,rec)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');startup(f,True)
        assert 'xwn593' not in {n.lower() for n in m.names(f,'/E')}
        assert set(inventory(f,KIT+'/game'))==set(q['reuse_expected'])
        for n in [KIT+'/run593.exe',KIT+'/owner.json']:
            assert m.sha(m.get(f,n))==st['staged'][n]['sha256']
        for name,h in q['runtime_module_pins'].items():assert m.sha(m.get(f,'/E/winnt/system32/'+name))==h
        rec['completed']=True;m.write_json(check,rec)
        pair.request_once(f,out,dict(stage_sha256=m.sha((K/'stage002.json').read_bytes()),preflight_sha256=m.sha(check.read_bytes()),ordinary_launcher=True,automatic_restart_requested_by_runner=True,native_pc_control=593,unattended=False,console_C_accessed=False,one_launch_only=True))

'''+text[end:]
text=text.replace("('stage','launch','collect')","('launch','collect')")
(K/'controller002.py').write_bytes(text.encode())
for n in ['observe001.py','supervise001.py']:
    text=(K/n).read_text().replace('controller001.py','controller002.py')
    if n.startswith('supervise'):
        text=text.replace("'supervisor001-'+action", "'supervisor002-'+action").replace('C:/xwn594/supervisor001','C:/xwn594/supervisor002')
    (K/n.replace('001','002')).write_bytes(text.encode())
failure=dict(failed_stage='stage001.json',supervisor='supervisor001-stage.json',error='FTP PASV received502 Command not implemented during payload readback',verified_old_files=503,verified_new_entries=189,launch_sent=False,hook_installed=False,source_folder='/E/xwn586-kit/game',destination_folder='/E/xwn593-kit/game',recorded_writes=r['writes'],next='Independent readback of exact partial state; never rerun stage001 or replay its move/restore operations. New stage002 uses fresh connections per cold read.',source_sha256=hashlib.sha256((K/'stage001.json').read_bytes()).hexdigest())
(K/'stage-failure001.json').write_text(json.dumps(failure,indent=2)+'\n')
print('Drafted recovery controller; no physical action')
