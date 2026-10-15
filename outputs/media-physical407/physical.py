"""Private demo-only copy and one normal launch; no startup/driver changes."""
import io,json,os,sys
from pathlib import Path

K=Path(__file__).resolve().parent
W=K.parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(W/'outputs/demo-audio-level256'))
from common001 import connect,get,names,sha,ticket,utc
sys.path.insert(0,str(W/'outputs/surface-bridge260'))
from atomic_json import write_json

NS='/E/xwndemo407'
MEDIA=Path('E:/xwn406/media001/ces2001-nt5.mpg')
MEDIA_SHA='e39bf2aee01eecf993723988b274518f3f75076c6b62d1f263051daadd069619'
PRIVATE=Path('E:/xwn407')
PLAYER='/E/Program Files/Windows Media Player/mplayer2.exe'
TARGET='/E/Applications/XWNEBoot/default.xbe'
START='/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))

def installed():
    r=read(W/'outputs/demo-integration399/accepted-state.json')
    assert r['accepted'] and r['normal_startup_retained']
    return {p:h for p,h in r['verified_files'].items() if '/config/' not in p.lower()}

def capture():
    ticket()
    assert all(os.environ.get(k) for k in ('XWN_FTP_HOST','XWN_FTP_USER','XWN_FTP_PASSWORD'))
    assert not (K/'before.json').exists() and not PRIVATE.exists()
    b=MEDIA.read_bytes();assert sha(b)==MEDIA_SHA
    PRIVATE.mkdir()
    r=dict(completed=False,utc=utc(),physical_writes=False,console_C_accessed=False,files={})
    write_json(K/'before.json',r)
    with connect() as f:
        assert 'xwndemo407' not in {n.lower() for n in names(f,'/E')}
        for p,h in installed().items():
            data=get(f,p);assert sha(data)==h,p
            r['files'][p]=dict(bytes=len(data),sha256=sha(data))
        player=get(f,PLAYER);assert player[:2]==b'MZ'
        r['files'][PLAYER]=dict(bytes=len(player),sha256=sha(player))
        for p in [START,'/E/winnt/system32/config/sysevent.evt','/E/winnt/system32/config/appevent.evt']:
            data=get(f,p);q=PRIVATE/'before'/p.lstrip('/');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
            r['files'][p]=dict(bytes=len(data),sha256=sha(data))
        r['startup_listing']=names(f,START.rsplit('/',1)[0])
    r.update(completed=True,completed_utc=utc());write_json(K/'before.json',r)
    print('Current installation and normal startup verified; no console writes',flush=True)

def stage():
    ticket();before=read(K/'before.json');assert before['completed']
    dest=K/'stage.json';assert not dest.exists()
    media=MEDIA.read_bytes();assert sha(media)==MEDIA_SHA
    script=b'@echo off\r\n"C:\\Program Files\\Windows Media Player\\mplayer2.exe" /play "C:\\xwndemo407\\ces2001.mpg"\r\n'
    r=dict(completed=False,utc=utc(),directory=NS,writes=[],verified={},startup_changed=False,drivers_changed=False,console_C_accessed=False)
    write_json(dest,r)
    with connect() as f:
        for p,h in installed().items():assert sha(get(f,p))==h,p
        assert sha(get(f,PLAYER))==before['files'][PLAYER]['sha256']
        assert 'xwndemo407' not in {n.lower() for n in names(f,'/E')}
        r['directory_create_requested']=True;write_json(dest,r);f.mkd(NS)
        for name,data in [('ces2001.mpg',media),('play.cmd',script)]:
            p=NS+'/'+name;r['writes'].append(p);write_json(dest,r)
            ticket();f.storbinary('STOR '+p,io.BytesIO(data),65536)
            assert get(f,p)==data,p
            r['verified'][p]=dict(bytes=len(data),sha256=sha(data));write_json(dest,r)
        assert sha(get(f,START))==before['files'][START]['sha256']
    r.update(completed=True,completed_utc=utc());write_json(dest,r)
    print('Two demo files uploaded/readback-verified; startup and drivers unchanged',flush=True)

def launch():
    ticket();stage=read(K/'stage002.json');assert stage['completed']
    dest=K/'launch.json';assert not dest.exists(),'Never repeat an uncertain launch'
    with connect() as f:
        for p,h in installed().items():assert sha(get(f,p))==h,p
        for p,v in stage['verified'].items():assert sha(get(f,p))==v['sha256'],p
        r=dict(utc=utc(),launch_requested=True,command=r'SITE EXEC E:\Applications\XWNEBoot\default.xbe',automatic_playback=False,normal_startup_unchanged=True,drivers_unchanged=True,console_C_accessed=False)
        write_json(dest,r);f.sock.settimeout(20)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as exc:r['reply_uncertain']=type(exc).__name__
        write_json(dest,r)
    print('One normal Windows launch recorded; manual C:\\xwndemo407\\play.cmd',flush=True)

if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ('capture','stage','launch')
    globals()[sys.argv[1]]()
