"""Cold readers, pinned identities and strict video profile log validation."""
import hashlib,importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'))
from coldio import ColdIO
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
STARTUP='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
HIVES=['system','software','default','sam','security']
PROTECTED=[('F','winnt/system32/drivers/'+p) for p in ['xwnfatx.sys','xboxvnt5.sys','nvnetnt5.sys','atapi.sys','ndis.sys','tcpip.sys']]+[('F','winnt/system32/'+p) for p in ['setupapi.dll','ntoskrnl.exe','kernel32.dll','ntdll.dll']]+[('E','Applications/XWNFBoot/'+p) for p in ['default.xbe','freeldr.sys','loader/halxboxnt5.dll']]
PROTECTED += [('F','winnt/system32/'+p) for p in ['msvcrt.dll','advapi32.dll','user32.dll','hid.dll','shell32.dll']]
PROTECTED += [('F','winnt/system32/drivers/videoprt.sys')]
PROTECTED += [('F','winnt/system32/'+p) for p in ['gdi32.dll','win32k.sys','bootvid.dll']]
PROTECTED += [('E','Applications/XWNFBoot/loader/xboxbvid.dll')]
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
def readers(io,disk):return {v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}

def validate_log(data, candidate=False):
    r=dict(passed=False,cases=[])
    if data is None:return r
    try:
        lines=data.decode('ascii').splitlines();at=0
        def take(label,exact=None):
            nonlocal at
            words=lines[at].split();at+=1;assert words[0]==label and len(words)==4,(label,words)
            nums=list(map(int,words[1:]))
            if exact is not None:assert nums==exact,(label,nums,exact)
            return nums
        take('ATTEMPT_ONCE',[117,3,3]);take('INSTALL_IDLE_START',[0,0,0]);take('MODE_WIDTH_HEIGHT_BPP',[1024,576,32])
        take('DRIVER_EXPECT_RESPONSE',[int(candidate),1,0])
        take('DRIVER_ID_VERSION_MODE',[0x44525758,109 if candidate else 108,1])
        take('DRIVER_WIDTH_HEIGHT_STRIDE',[1024,576,4096]);take('DRIVER_BPP_BYTES_RESERVED',[32,2359296,0])
        take('CURSOR_PARKED',[1000,550,0])
        for size,(w,h) in enumerate([(64,64),(256,128),(768,384)]):
            take('GEOMETRY_INDEX_W_H',[size,w,h]);take('DIB_STRIDE_BYTES',[(w+16)*4,(w+16)*(h+16)*4,2])
            for round in range(3):
                for index in range(6):
                    kind=(index+round)%6
                    take('CASE_SIZE_ROUND_KIND',[size,round,kind]);n,ms,pixels=take('TIMING_COUNT_MS_PIXELS')
                    assert 0<n<=4096 and 0<ms<30000 and pixels==w*h
                    take('VERIFIED_PRE_POST',[2,1,0]);take('SHADOW_COHERENCE',[1,0,1]);r['cases'].append(dict(width=w,height=h,round=round,kind=kind,count=n,elapsed_ms=ms,pixels=pixels,ns_per_pixel=ms*1000000/(n*pixels)))
        if True:
            calls=[]
            for i in range(14):
                index,count,reserved=take('SHADOW_CALLBACK');assert index==i and reserved==0;calls.append(count)
            uploads,low,high=take('SHADOW_UPLOADS_BYTES');assert uploads>0 and (low or high) and sum(calls)>0
            r['shadow_callbacks']=calls;r['shadow_uploads']=uploads;r['shadow_bytes']=low+(high<<32)
        take('COMPLETE' ,[0,54,162]);take('INSTALL_IDLE_END',[0,0,0]);take('NORMAL_RESTART_REQUEST',[0,0,0]);assert at==len(lines)
        r.update(passed=True,verified_pixel_stages=162,mode=[1024,576,32])
    except (AssertionError,ValueError,IndexError,UnicodeError) as exc:r['error']=repr(exc)
    return r
