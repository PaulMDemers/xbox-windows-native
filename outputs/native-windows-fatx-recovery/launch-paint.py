"""One manual Paint/persistence boot; retain qualified0088 storage and physical HAL."""
import datetime, ftplib, hashlib, io, json, os, pathlib, socket

k=pathlib.Path(__file__).resolve().parent
p=k.parent/'native-windows-physical-f'
record=k/'physical-paint.json'
assert not record.exists(), 'Existing launch record: inspect, never relaunch blindly'
prior=json.loads((k/'physical-long.json').read_text())
assert json.loads((k/'physical-long-qualification.json').read_text())['passed']
assert not prior['startup_restart_enabled']
sha=lambda data:hashlib.sha256(data).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
driver=(p/'artifacts/xboxvnt5-dimensions.sys').read_bytes()
candidate=sha(driver)
assert candidate=='f8af1d8477d61ad8933962fd6347f43620f5ef1d21efe54110b94fec106986eb'
for filename,key in [('video-dimensions-tests.json','miniport_sha256'),('video-dimensions-emulator.json','miniport_sha256'),('video-dimensions-trace-tests.json','sha256')]:
    assert json.loads((p/filename).read_text())[key]==candidate
assert json.loads((p/'video-dimensions-trace-tests.json').read_text())['passed']
replay=json.loads((p/'patch-check-0075.json').read_text())
assert replay['clean_index_replay_verified'] and replay['reverse_check']
folder=k/'artifacts/paint';folder.mkdir(exist_ok=True)
startup='/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
miniport='/F/winnt/system32/drivers/xboxvnt5.sys'
backup='/F/winnt/system32/drivers/xboxvnt5.pre-dim'
staged='/F/winnt/system32/drivers/xboxvnt5.new-dim'
trace='/F/winnt/system32/xwn-video-trace.bin'

class FTP(ftplib.FTP):
    def ntransfercmd(self,*args,**kwargs):
        sock,n=super().ntransfercmd(*args,**kwargs)
        sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
        return sock,n

def get(f,path,optional=False):
    b=io.BytesIO()
    try:f.retrbinary('RETR '+path,b.write)
    except ftplib.error_perm as e:
        if optional and str(e).startswith('550'):return None
        raise
    return b.getvalue()

def put(f,path,data):
    for at in range(0,len(data),32768):
        f.storbinary(('STOR ' if at==0 else 'APPE ')+path,io.BytesIO(data[at:at+32768]),blocksize=1024)
    assert get(f,path)==data

def preserve(name,data):
    path=folder/name
    if path.exists():assert path.read_bytes()==data
    else:path.write_bytes(data)
    return dict(bytes=len(data),sha256=sha(data))

def save():record.write_text(json.dumps(r,indent=2)+'\n')

with FTP() as f:
    f.connect('192.168.50.242',timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
    assert json.loads(get(f,'/F/xwn-deploy-v1.json'))==json.loads((p/'physical-cache-preflight.json').read_text())['ownership_marker']
    for path,expected in prior['expected_drivers'].items():assert sha(get(f,path))==expected,path
    initial=json.loads((p/'physical-cycle-001.json').read_text())
    for name,key in [('default.xbe','launcher_sha256'),('freeldr.sys','loader_sha256')]:
        assert sha(get(f,'/E/Applications/XWNFBoot/'+name))==initial[key]
    previous=get(f,startup);assert sha(previous)==prior['current_startup_sha256']
    assert sha(get(f,'/F/xwn-report-v2.txt'))==prior['report']['sha256']
    assert get(f,backup,True) is None and get(f,staged,True) is None
    r=dict(scope=__doc__,created_utc=utc(),launch_attempted=False,
           filesystem_sha256=prior['expected_drivers']['/F/winnt/system32/drivers/xwnfatx.sys'],
           hal_sha256=prior['expected_drivers']['/E/Applications/XWNFBoot/loader/halxboxnt5.dll'],
           previous_miniport_sha256=prior['expected_drivers'][miniport],miniport_sha256=candidate,
           miniport_backup=backup,startup_restart_enabled=False,startup_paint_enabled=False,
           startup_sha256=sha(previous),manual_saved_files_result='awaiting_user_reopen',
           physical_paint_result='awaiting_user_observation',preserved={})
    for name,path in [('previous-video.sys',miniport),('startup.cmd',startup),('trace.bin',trace),
                      ('system.evt','/F/winnt/system32/config/sysevent.evt'),
                      ('application.evt','/F/winnt/system32/config/appevent.evt')]:
        r['preserved'][name]=preserve(name,get(f,path))
    save()
    try:
        put(f,staged,driver)
        f.rename(miniport,backup);f.rename(staged,miniport)
        assert sha(get(f,backup))==r['previous_miniport_sha256']
        assert sha(get(f,miniport))==candidate
        r['video_installed_utc']=utc();save()
        put(f,trace,b'XWN-VID-TRACE01\n'+bytes(4080))
        assert get(f,startup)==previous
        # Recheck storage/HAL immediately before handoff; no other driver changes.
        for path,expected in prior['expected_drivers'].items():
            assert sha(get(f,path))==(candidate if path==miniport else expected)
        r.update(launch_attempted=True,launch_utc=utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe')
        save()
        try:r['reply']=f.sendcmd(r['command'])
        except (EOFError,OSError) as e:r['uncertain_reply']=repr(e)
        save();print('Manual desktop launch:',r.get('reply',r.get('uncertain_reply')))
    except Exception as e:
        r['error']=repr(e);save();raise
