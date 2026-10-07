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
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
def readers(io,disk):return {v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}

def validate_log(data):
    r=dict(passed=False,cases=[])
    if data is None:return r
    try:
        lines=data.decode('ascii').splitlines();at=0
        def take(label,exact=None):
            nonlocal at
            words=lines[at].split();at+=1;assert words[0]==label and len(words)==4,(label,words)
            nums=list(map(int,words[1:]));assert all(0<=v<=0xffffffff for v in nums)
            if exact is not None:assert nums==exact,(label,nums,exact)
            return nums
        take('ATTEMPT_ONCE',[111,3,3]);cursor=take('CURSOR_CONFIGURATION');assert cursor==[820,460,1];r['cursor_configuration']=cursor;detail=take('QPC_MODE');assert detail in [[0,0,0],[1,0,0]];r['qpc_mode']=detail[0];freqhi,freqlo,zero=take('QPC_FREQUENCY');freq=(freqhi<<32)|freqlo;assert 0<freq<=0x7fffffff and zero==0;r['qpc_frequency']=freq;take('INSTALL_IDLE_START',[0,0,0]);take('MODE_WIDTH_HEIGHT_BPP',[1024,576,32])
        for size,(w,h) in enumerate([(64,64),(256,128),(768,384)]):
            take('GEOMETRY_INDEX_W_H',[size,w,h]);take('DIB_STRIDE_BYTES',[(w+16)*4,(w+16)*(h+16)*4,2])
            for round in range(3):
                for index in range(6):
                    kind=(index+round)%6
                    attempts,settle_ms,z=take('CURSOR_READY');assert 1<=attempts<=50 and 0<settle_ms<=12000 and z==0
                    take('CASE_SIZE_ROUND_KIND',[size,round,kind]);n,ms,pixels=take('TIMING_COUNT_MS_PIXELS')
                    assert 0<n<=4096 and 0<ms<30000 and pixels==w*h and (ms>=300 or n==4096)
                    take('VERIFIED_PRE_POST',[2,1,0])
                    def ticks(label,count):
                        hi,lo,c=take(label);assert 0<=hi<=0xffffffff and 0<=lo<=0xffffffff and c==count;return (hi<<32)|lo
                    outer=ticks('QPC_OUTER',n);op=ticks('QPC_OPERATION',n);flush=ticks('QPC_FLUSH',n);checks=ticks('QPC_CHECKS',n)
                    calibration=[]
                    for phase in ['PRE','POST']:
                        total=ticks('QPC_CAL_'+phase,128);lo,hi,c=take('QPC_CAL_'+phase+'_RANGE');assert 0<=lo<=hi and c==128 and lo*128<=total<=hi*128
                        calibration.append(dict(sum_ticks=total,min_ticks=lo,max_ticks=hi,count=128))
                    assert outer>0 and op+flush+checks<=outer
                    assert (detail[0]==1 and op>0) or (detail[0]==0 and op==flush==checks==0)
                    qpc_ms=outer*1000/freq;assert abs(qpc_ms-ms)<=max(50,ms*.1),('QPC/coarse disagreement',qpc_ms,ms)
                    r['cases'].append(dict(width=w,height=h,round=round,kind=kind,count=n,elapsed_ms=ms,pixels=pixels,ns_per_pixel=ms*1000000/(n*pixels),qpc_outer=outer,qpc_operation=op,qpc_flush=flush,qpc_checks=checks,qpc_unbracketed=outer-op-flush-checks,calibration=calibration,cursor_ready_attempts=attempts,cursor_ready_ms=settle_ms))
        take('COMPLETE',[0,54,162]);take('INSTALL_IDLE_END',[0,0,0]);take('NORMAL_RESTART_REQUEST',[0,0,0]);assert at==len(lines)
        r.update(passed=True,verified_pixel_stages=162,mode=[1024,576,32])
    except (AssertionError,ValueError,IndexError,UnicodeError) as exc:r['error']=repr(exc)
    return r
