"""Preserve cycle011 evidence and disable its one-shot startup; never launch."""
import datetime, ftplib, hashlib, io, json, os, pathlib
k=pathlib.Path(__file__).resolve().parent
record=k/'physical-cycle-011.json'; r=json.loads(record.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def get(f,name,optional=False):
    b=io.BytesIO()
    try:f.retrbinary('RETR '+name,b.write)
    except ftplib.error_perm as e:
        if optional and str(e).startswith('550'):return None
        raise
    return b.getvalue()
def preserve(name,data):
    p=k/'artifacts'/name
    if p.exists():assert p.read_bytes()==data, 'Evidence changed: '+name
    else:p.write_bytes(data)
    return {'bytes':len(data),'sha256':sha(data)}
def save():record.write_text(json.dumps(r,indent=2)+'\n')
assert r['launch_attempted'] and not r.get('prior_cycle009_report_restored'), 'Collection already completed; inspect preserved evidence'
with ftplib.FTP() as f:
    f.connect(r['host'],timeout=15); f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
    f.cwd('/F'); marker=json.loads(get(f,'xwn-deploy-v1.json'))
    assert marker==json.loads((k/'physical-cache-preflight.json').read_text())['ownership_marker']
    old_startup=get(f,'xwn-startup-c10.bak')
    assert sha(old_startup)==json.loads((k/'physical-cycle-010.json').read_text())['startup_sha256']
    f.cwd('/F/documents and settings/all users/start menu/programs/startup')
    current=get(f,'xwnsetup.cmd');assert sha(current) in [r['startup_sha256'],sha(old_startup)]
    if current!=old_startup:
        f.storbinary('STOR xwnsetup.cmd',io.BytesIO(old_startup),blocksize=1024)
    assert get(f,'xwnsetup.cmd')==old_startup
    r.update(startup_restart_enabled=False,current_startup_sha256=sha(old_startup));save()
    f.cwd('/F'); report=get(f,'xwn-report-v2.txt')
    r['cache_report']=preserve('physical-cache-011-report.txt',report)
    r['cache_report']['text']=report.rstrip(b' \0').decode('ascii',errors='replace')
    r['cache_probe_started']=report.startswith(b'XWN-CACHE-START')
    r['cache_probe_passed']=b'XWN-CACHE-PASS' in report
    r['test_files']={}
    for name in ['xwn-cache-append.tmp','xwn-cache-map.tmp','xwn-cache-pressure.tmp']:
        data=get(f,name,True)
        r['test_files'][name]=None if data is None else {'bytes':len(data),'sha256':sha(data)}
    save()
    for directory,names in [('/F/winnt/system32',['xwn-video-trace.bin','ntoskrnl.exe']),('/F/winnt/system32/config',['sysevent.evt','appevent.evt']),('/F/winnt',['setupapi.log'])]:
        f.cwd(directory)
        for name in names:
            data=get(f,name);r.setdefault('collected',{})[name]=preserve('physical-011-'+name,data)
    f.cwd('/F/winnt/system32/drivers')
    assert sha(get(f,'xwnfatx.sys'))==r['filesystem_sha256']
    assert sha(get(f,'xboxvnt5.sys'))==r['miniport_sha256']
    r.update(evidence_collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='physical_boot_stop_0a_probe_not_completed')
    save()
    # Preserve the failed test report on the console, then restore the prior
    # passing report with its original identity. This is not cycle011 success.
    f.cwd('/F');assert get(f,'xwn-cache-report-011.txt',True) is None
    prior=get(f,'xwn-report-v2.pass009')
    assert sha(prior)==json.loads((k/'physical-cycle-009.json').read_text())['report_sha256']
    f.rename('xwn-report-v2.txt','xwn-cache-report-011.txt')
    f.rename('xwn-report-v2.pass009','xwn-report-v2.txt')
    assert get(f,'xwn-report-v2.txt')==prior
    r['prior_cycle009_report_restored']=True;save()
print(json.dumps(r,indent=2))
