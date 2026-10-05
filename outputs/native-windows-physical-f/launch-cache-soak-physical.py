"""One cycle013 launch: extend tests while keeping cycle012 drivers unchanged."""
import datetime, ftplib, hashlib, io, json, os, pathlib
k = pathlib.Path(__file__).resolve().parent
record = k / 'physical-cycle-013.json'
assert not record.exists(), 'Inspect existing cycle; never relaunch blindly'
old = json.loads((k / 'physical-cycle-012.json').read_text())
assert old['physical_cache_trial_passed'] and not old['startup_restart_enabled']
sha = lambda b: hashlib.sha256(b).hexdigest()
probe = (k / 'artifacts/xwncache-soak.exe').read_bytes()
build = json.loads((k / 'cache-soak-build.json').read_text())
assert sha(probe) == build['sha256']
assert sha((k / 'cache-probe.c').read_bytes()) == build['source_sha256']
startup = b'@echo off\r\nC:\\xwnsoak.exe\r\n'
seed = b'XWN-VID-TRACE01\n' + bytes(4080)
r = {key: old[key] for key in ['host','filesystem_sha256','previous_filesystem_sha256','driver_backup','hal_sha256','miniport_sha256','command']}
r.update(scope=__doc__, launch_attempted=False, probe_sha256=sha(probe),
         prior_report_backup='/F/xwn-report-v2.pass012', prior_cycle=12,
         startup_sha256=sha(startup), startup_restart_enabled=True,
         startup_backup='/F/xwn-startup-c12.bak', trace_seed_sha256=sha(seed),
         mapped_cases=300, soak_ms=300000)
def save(): record.write_text(json.dumps(r, indent=2)+'\n')
def get(f, name, optional=False):
    b=io.BytesIO()
    try: f.retrbinary('RETR '+name,b.write)
    except ftplib.error_perm as e:
        if optional and str(e).startswith('550'): return None
        raise
    return b.getvalue()
def put(f, name, b):
    f.storbinary('STOR '+name,io.BytesIO(b),blocksize=1024)
    assert get(f,name)==b
with ftplib.FTP() as f:
    f.connect(r['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
    f.cwd('/F')
    assert json.loads(get(f,'xwn-deploy-v1.json'))==json.loads((k/'physical-cache-preflight.json').read_text())['ownership_marker']
    assert sha(get(f,'xwn-report-v2.txt'))==old['cache_report']['sha256']
    for name in ['xwn-report-v2.pass012','xwn-startup-c12.bak','xwnsoak.exe']:
        assert get(f,name,True) is None,name
    for name,info in old['test_files'].items():
        assert sha(get(f,name))==info['sha256']
        assert get(f,name+'.c12',True) is None
    f.cwd('/F/winnt/system32/drivers')
    assert sha(get(f,'xwnfatx.sys'))==r['filesystem_sha256']
    assert sha(get(f,'xboxvnt5.sys'))==r['miniport_sha256']
    f.cwd('/E/Applications/XWNFBoot/loader')
    assert sha(get(f,'halxboxnt5.dll'))==r['hal_sha256']
    f.cwd('/F/winnt/system32')
    assert get(f,'xwn-video-trace.bin')==(k/'artifacts/physical-012-xwn-video-trace.bin').read_bytes()
    f.cwd('/F/documents and settings/all users/start menu/programs/startup')
    previous=get(f,'xwnsetup.cmd');assert sha(previous)==old['current_startup_sha256']
    f.cwd('/E/Applications/XWNFBoot')
    initial=json.loads((k/'physical-cycle-001.json').read_text())
    for name,key in [('default.xbe','launcher_sha256'),('freeldr.sys','loader_sha256')]:
        assert sha(get(f,name))==initial[key]
    r.update(status='preconditions_verified',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
    try:
        f.cwd('/F');put(f,'xwn-startup-c12.bak',previous)
        f.rename('xwn-report-v2.txt','xwn-report-v2.pass012')
        for name in old['test_files']:f.rename(name,name+'.c12')
        put(f,'xwn-report-v2.txt',b'XWN-CACHE-PENDING\r\n'.ljust(4096,b' '))
        put(f,'xwnsoak.exe',probe)
        f.cwd('/F/winnt/system32');put(f,'xwn-video-trace.bin',seed)
        f.cwd('/F/documents and settings/all users/start menu/programs/startup');put(f,'xwnsetup.cmd',startup)
        r.update(status='awaiting_cache_soak',launch_attempted=True,launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
        try:r['reply']=f.sendcmd(r['command'])
        except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
        save();print(json.dumps(r,indent=2))
    except Exception as e:r['error']=repr(e);save();raise
