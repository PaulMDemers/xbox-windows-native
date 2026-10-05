"""One cycle014 Paint trial after cycle013; change only video driver and startup."""
import datetime, ftplib, hashlib, io, json, os, pathlib
k=pathlib.Path(__file__).resolve().parent
record=k/'physical-cycle-014.json'
assert not record.exists(), 'Never repeat a recorded launch blindly'
old=json.loads((k/'physical-cycle-013.json').read_text())
assert old['physical_cache_trial_passed'] and not old['startup_restart_enabled']
sha=lambda b:hashlib.sha256(b).hexdigest()
driver=(k/'artifacts/xboxvnt5-dimensions.sys').read_bytes()
assert sha(driver)=='f8af1d8477d61ad8933962fd6347f43620f5ef1d21efe54110b94fec106986eb'
assert sha(driver)==json.loads((k/'video-dimensions-tests.json').read_text())['miniport_sha256']
assert sha(driver)==json.loads((k/'video-dimensions-emulator.json').read_text())['miniport_sha256']
startup=b'@echo off\r\nstart C:\\WINNT\\system32\\mspaint.exe\r\nexit\r\n'
seed=b'XWN-VID-TRACE01\n'+bytes(4080)
r={key:old[key] for key in ['host','filesystem_sha256','hal_sha256','command']}
r.update(scope=__doc__,launch_attempted=False,miniport_sha256=sha(driver),
         previous_miniport_sha256=old['miniport_sha256'],
         miniport_backup='/F/winnt/system32/drivers/xboxvnt5.xwn-c13',
         startup_backup='/F/xwn-startup-c13.bak',startup_sha256=sha(startup),
         startup_restart_enabled=False,startup_paint_enabled=True,
         trace_seed_sha256=sha(seed),prior_cache_report_sha256=old['cache_report']['sha256'],
         physical_paint_result='awaiting_user_observation')
def save():record.write_text(json.dumps(r,indent=2)+'\n')
def get(f,name,optional=False):
    b=io.BytesIO()
    try:f.retrbinary('RETR '+name,b.write)
    except ftplib.error_perm as e:
        if optional and str(e).startswith('550'):return None
        raise
    return b.getvalue()
def put(f,name,b):
    f.storbinary('STOR '+name,io.BytesIO(b),blocksize=1024);assert get(f,name)==b
with ftplib.FTP() as f:
    f.connect(r['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
    f.cwd('/F')
    assert json.loads(get(f,'xwn-deploy-v1.json'))==json.loads((k/'physical-cache-preflight.json').read_text())['ownership_marker']
    assert sha(get(f,'xwn-report-v2.txt'))==r['prior_cache_report_sha256']
    assert get(f,'xwn-startup-c13.bak',True) is None
    assert get(f,'xwn-paint-test.bmp',True) is None
    f.cwd('/F/winnt/system32/drivers')
    assert sha(get(f,'xwnfatx.sys'))==r['filesystem_sha256']
    assert sha(get(f,'xboxvnt5.sys'))==r['previous_miniport_sha256']
    for name in ['xboxvnt5.xwn-c13','xboxvnt5.xwn-new14']:assert get(f,name,True) is None
    f.cwd('/E/Applications/XWNFBoot/loader');assert sha(get(f,'halxboxnt5.dll'))==r['hal_sha256']
    f.cwd('/E/Applications/XWNFBoot')
    initial=json.loads((k/'physical-cycle-001.json').read_text())
    for name,key in [('default.xbe','launcher_sha256'),('freeldr.sys','loader_sha256')]:assert sha(get(f,name))==initial[key]
    f.cwd('/F/winnt/system32')
    assert get(f,'xwn-video-trace.bin')==(k/'artifacts/physical-013-xwn-video-trace.bin').read_bytes()
    f.cwd('/F/documents and settings/all users/start menu/programs/startup')
    previous=get(f,'xwnsetup.cmd');assert sha(previous)==old['current_startup_sha256']
    r.update(status='preconditions_verified',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
    try:
        f.cwd('/F');put(f,'xwn-startup-c13.bak',previous)
        f.cwd('/F/winnt/system32/drivers');put(f,'xboxvnt5.xwn-new14',driver)
        f.rename('xboxvnt5.sys','xboxvnt5.xwn-c13');f.rename('xboxvnt5.xwn-new14','xboxvnt5.sys')
        assert sha(get(f,'xboxvnt5.sys'))==r['miniport_sha256']
        f.cwd('/F/winnt/system32');put(f,'xwn-video-trace.bin',seed)
        f.cwd('/F/documents and settings/all users/start menu/programs/startup');put(f,'xwnsetup.cmd',startup)
        r.update(status='awaiting_physical_paint',launch_attempted=True,launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
        try:r['reply']=f.sendcmd(r['command'])
        except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
        save();print(json.dumps(r,indent=2))
    except Exception as e:r['error']=repr(e);save();raise
