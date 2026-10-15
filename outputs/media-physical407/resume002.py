"""Resume only a readback-proven prefix after the failed bulk STOR."""
import io
from physical import *

ticket();dest=K/'stage002.json';assert not dest.exists()
old=read(K/'stage.json');assert not old['completed'] and not (K/'launch.json').exists()
media=MEDIA.read_bytes();assert sha(media)==MEDIA_SHA
r=dict(completed=False,utc=utc(),parent_stage_sha256=sha((K/'stage.json').read_bytes()),
       directory=NS,writes=[],verified={},startup_changed=False,drivers_changed=False,console_C_accessed=False)
write_json(dest,r)
with connect() as f:
    for p,h in installed().items():assert sha(get(f,p))==h,p
    current=names(f,NS);assert set(current)=={'ces2001.mpg'}
    prefix=get(f,NS+'/ces2001.mpg');assert 0<len(prefix)<len(media) and prefix==media[:len(prefix)]
    private=PRIVATE/'partial001.mpg';assert not private.exists();private.write_bytes(prefix)
    r['prefix']=dict(bytes=len(prefix),sha256=sha(prefix),exact_source_prefix=True)
    r['writes'].append(NS+'/ces2001.mpg');write_json(dest,r)
    for at in range(len(prefix),len(media),32768):
        ticket();f.storbinary('APPE '+NS+'/ces2001.mpg',io.BytesIO(media[at:at+32768]),1024)
        r['acknowledged_bytes']=min(at+32768,len(media))
        if (at-len(prefix))%(1024*1024)==0:
            write_json(dest,r);print('Acknowledged bytes',r['acknowledged_bytes'],flush=True)
    assert get(f,NS+'/ces2001.mpg')==media
    r['verified'][NS+'/ces2001.mpg']=dict(bytes=len(media),sha256=sha(media));write_json(dest,r)
    script=b'@echo off\r\n"C:\\Program Files\\Windows Media Player\\mplayer2.exe" /play "C:\\xwndemo407\\ces2001.mpg"\r\n'
    assert 'play.cmd' not in {n.lower() for n in names(f,NS)}
    r['writes'].append(NS+'/play.cmd');write_json(dest,r)
    f.storbinary('STOR '+NS+'/play.cmd',io.BytesIO(script),1024)
    assert get(f,NS+'/play.cmd')==script
    r['verified'][NS+'/play.cmd']=dict(bytes=len(script),sha256=sha(script))
    assert sha(get(f,START))==read(K/'before.json')['files'][START]['sha256']
r.update(completed=True,completed_utc=utc());write_json(dest,r)
print('Complete private media readback verified; no launch yet',flush=True)
