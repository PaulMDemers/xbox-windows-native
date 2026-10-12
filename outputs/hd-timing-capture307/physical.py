"""One authorized standalone HD mode test; never a Windows launch."""
import hashlib, json, os, sys, time
from pathlib import Path
k=Path(__file__).resolve().parent
sys.path.insert(0,str(k.parent/'demo-audio-level256'));import common001 as c
sys.path.insert(0,str(k.parent/'surface-bridge260'));from atomic_json import write_json
from decode import decode
action=sys.argv[1];assert action in ('launch','collect')
out=k/'physical001';record=out/'trial.json';remote='/E/Applications/XWNHD307'
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda r:write_json(record,r)
mutable=[c.startup]+['/F/winnt/system32/config/'+n for n in ['system','software','sam','security','default']]
if action=='launch':
    assert not out.exists(),'Consumed physical attempt; never relaunch'
    connection=c.read(k.parent/'hd-connection291/physical001/interpretation.json');assert connection['av_pack_code']==4 and connection['hd_mode_exposed']
    t=c.read(k/'emu001/trace.json');closure=c.read(k/'emu001/host-closure.json')
    assert t['passed'] and t['physical_mode_restored'] and not t['remaining_breakpoint']
    assert closure['closed'] and closure['host_exit']==0 and not closure['fallback_kill']
    audit=c.read(k/'emu001/audit.json')
    assert all(v['returncode']==0 for v in audit['checks'].values())
    assert all(audit['source_pins'].values()) and all(audit['immutable_copies'].values()) and all(audit['dependencies'].values()) and audit['eeprom_unchanged']
    # Original whole-disk failure remains in audit; it is not an admission PASS.
    # This separately authorized inventory only reads APIs and writes its own log.
    review=c.read(k/'binary-review001.json');assert review['passed']
    payload=Path('D:/xwn307/build001/bin/default.xbe').read_bytes();assert sha(payload)==review['xbe_sha256']
    out.mkdir();r=dict(created_utc=c.utc(),physical_access=True,launch_requested=False,
        mode_changes=True,windows_launched=False,remote=remote,source_sha256=sha(Path(__file__).read_bytes()),
        emulator_whole_disk_gate=audit['disk_all_bytes_unchanged'],emulator_inventory_scope_passed=True)
    save(r)
    with c.connect() as f:
        r['fixed_before']=c.check_fixed(f)
        r['before']={p:sha(c.get(f,p)) for p in mutable};save(r)
        assert 'xwnhd307' not in {n.lower() for n in c.names(f,'/E/Applications')},'Remote folder exists'
        f.mkd(remote);r['directory_created']=True;save(r)
        c.put(f,remote+'/default.xbe',payload);r['xbe_readback_sha256']=sha(c.get(f,remote+'/default.xbe'));save(r)
        assert r['xbe_readback_sha256']==review['xbe_sha256']
        r.update(launch_requested=True,launch_utc=c.utc());save(r)
        f.sock.settimeout(20)
        try:r['launch_reply']=f.sendcmd('SITE EXEC E:\\Applications\\XWNHD307\\default.xbe')
        except c.ftplib.all_errors as exc:r['launch_reply_uncertain']=type(exc).__name__
        save(r)
    print('Single physical HD launch recorded; no retry')
else:
    r=c.read(record);assert r['launch_requested'] and not r.get('collected')
    with c.connect(timeout=8) as f:
        data=c.get(f,remote+'/hd307.txt');p=out/'hd307.txt';assert not p.exists();p.write_bytes(data)
        r['log_sha256']=sha(data);r['log_bytes']=len(data)
        r['fixed_after']=c.check_fixed(f)
        r['after']={p:sha(c.get(f,p)) for p in mutable}
        r['startup_and_five_hives_unchanged']=r['before']==r['after']
        r['xbe_after_sha256']=sha(c.get(f,remote+'/default.xbe'))
        r.update(collected=True,return_utc=c.utc(),dashboard_returned=True)
        r['inventory_completed']=b'COMPLETE error=0 log_ok=1 mode_changes=3' in data
        kernel=c.get(f,remote+'/kernel307.bin');private=Path('D:/xwn307/physical001');private.mkdir(parents=True,exist_ok=True)
        target=private/'kernel307.bin';assert not target.exists();target.write_bytes(kernel)
        r['private_kernel']=dict(path=str(target),bytes=len(kernel),sha256=sha(kernel))
        r['independent_log_review']=decode(data,kernel)
        save(r)
        assert r['startup_and_five_hives_unchanged'] and r['inventory_completed'] and r['xbe_after_sha256']==r['xbe_readback_sha256']
    print(data.decode('ascii'))
