"""One-shot physical cache test; preserve cycle009 report and cycle010 driver."""
import pathlib,ftplib,io,json,os,hashlib,datetime
k=pathlib.Path(__file__).resolve().parent;record=k/'physical-cycle-011.json'
assert not record.exists(),'Inspect the existing cycle record; never relaunch blindly'
sha=lambda b:hashlib.sha256(b).hexdigest()
old=json.loads((k/'physical-cycle-010.json').read_text());good=json.loads((k/'physical-cycle-009.json').read_text())
audit=json.loads((k.parent/'native-windows-extended-storage/nt5-physical-f-cache-stress-candidate-001-cold-audit.json').read_text());assert audit['passed']
driver=(k/'artifacts/xwnfatx-deferred.sys').read_bytes();probe=(k/'artifacts/xwncache-stress.exe').read_bytes()
assert sha(driver)==audit['expected_filesystem_driver_sha256']=='f8c1f66a4460034d6c78cdd186ac2c3471383362aaa2b69d2865ba803d1d7154'
assert sha(probe)=='833a5756b19db7771b9d96a3e3534781bc848bc440546e8e1acf0197be2a46e3'
seed=b'XWN-VID-TRACE01\n'+bytes(4080);startup=b'@echo off\r\nC:\\xwncache.exe\r\n'
r={'scope':__doc__,'host':old['host'],'launch_attempted':False,'filesystem_sha256':sha(driver),'previous_filesystem_sha256':'a10cfaac19a526f48e0a85ebab961140130ba4e7e4a3660dad2f56fa2841d183','probe_sha256':sha(probe),'miniport_sha256':old['miniport_sha256'],'hal_sha256':old['hal_sha256'],'trace_seed_sha256':sha(seed),'startup_sha256':sha(startup),'startup_restart_enabled':True,'prior_report_backup':'/F/xwn-report-v2.pass009','driver_backup':'/F/winnt/system32/drivers/xwnfatx.xwn-c10'}
def save():record.write_text(json.dumps(r,indent=2)+'\n')
def get(f,name,optional=False):
    b=io.BytesIO()
    try:f.retrbinary('RETR '+name,b.write)
    except ftplib.error_perm as e:
        if optional and str(e).startswith('550'):return None
        raise
    return b.getvalue()
def put(f,name,data):
    f.storbinary('STOR '+name,io.BytesIO(data),blocksize=1024);assert get(f,name)==data
with ftplib.FTP() as f:
    f.connect(r['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
    f.cwd('/F');marker=json.loads(get(f,'xwn-deploy-v1.json'));assert marker==json.loads((k/'physical-cache-preflight.json').read_text())['ownership_marker']
    assert sha(get(f,'xwn-report-v2.txt'))==good['report_sha256']
    for name in ['xwncache.exe','xwn-report-v2.pass009','xwn-startup-c10.bak','xwn-cache-map.tmp','xwn-cache-append.tmp','xwn-cache-pressure.tmp']:assert get(f,name,True) is None,name
    f.cwd('/E/Applications/XWNFBoot/loader');assert sha(get(f,'halxboxnt5.dll'))==r['hal_sha256']
    f.cwd('/F/winnt/system32');assert get(f,'xwn-video-trace.bin')==(k/'artifacts/physical-video-trace-010.bin').read_bytes()
    f.cwd('/F/winnt/system32/drivers');assert sha(get(f,'xwnfatx.sys'))==r['previous_filesystem_sha256'];assert sha(get(f,'xboxvnt5.sys'))==r['miniport_sha256']
    for name in ['xwnfatx.xwn-c10','xwnfatx.xwn-new11']:assert get(f,name,True) is None
    f.cwd('/F/documents and settings/all users/start menu/programs/startup');previous_startup=get(f,'xwnsetup.cmd');assert sha(previous_startup)==old['startup_sha256']
    r.update(status='preconditions_verified',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
    try:
        f.cwd('/F');put(f,'xwncache.exe',probe);put(f,'xwn-startup-c10.bak',previous_startup)
        f.rename('xwn-report-v2.txt','xwn-report-v2.pass009');put(f,'xwn-report-v2.txt',b'XWN-CACHE-PENDING\r\n'.ljust(4096,b' '))
        f.cwd('/F/winnt/system32/drivers');put(f,'xwnfatx.xwn-new11',driver)
        f.rename('xwnfatx.sys','xwnfatx.xwn-c10');f.rename('xwnfatx.xwn-new11','xwnfatx.sys');assert get(f,'xwnfatx.sys')==driver
        f.cwd('/F/winnt/system32');put(f,'xwn-video-trace.bin',seed)
        f.cwd('/F/documents and settings/all users/start menu/programs/startup');put(f,'xwnsetup.cmd',startup)
        f.cwd('/E/Applications/XWNFBoot');initial=json.loads((k/'physical-cycle-001.json').read_text())
        for name,key in [('default.xbe','launcher_sha256'),('freeldr.sys','loader_sha256')]:assert sha(get(f,name))==initial[key]
        r.update(status='awaiting_automatic_cache_test',launch_attempted=True,launch_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=good['command']);save()
        try:r['reply']=f.sendcmd(r['command'])
        except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
        save();print(r)
    except Exception as e:r['error']=repr(e);save();raise
