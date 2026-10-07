"""Independent expected bytes and identities for ordinary mapped-append regression."""
import hashlib,importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'))
from coldio import ColdIO
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
PREFIXES=[0,3985,65290,65300,65315,65316,130826,130836,130851,130852,270225]
CHUNKS=[220,53,27,49,75,23,45,86,220,185,74,103,141,42,22,51,115,104]
WARNING=b'An unsigned or incorrectly signed driver (c:\\xwninf99\\xwnvideo.inf) was installed for Xbox NV2A firmware framebuffer (experimental). Error 0xe000022f: The third-party INF does not contain digital signature information.\r\n'
assert len(WARNING)==220 and sum(CHUNKS)==1635
STARTUP='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
HIVES=['system','software','default','sam','security']
PROTECTED=[('F','winnt/system32/drivers/'+p) for p in ['xwnfatx.sys','xboxvnt5.sys']]+[('F','winnt/system32/'+p) for p in ['setupapi.dll','ntoskrnl.exe','kernel32.dll','ntdll.dll']]+[('E','Applications/XWNFBoot/'+p) for p in ['default.xbe','freeldr.sys','loader/halxboxnt5.dll']]
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
def readers(io,disk):return {v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}
def expected(index,round=3):
    start=PREFIXES[index];data=bytearray((offset*13+index*17+round*29)&255 for offset in range(start+sum(CHUNKS)))
    data[start:start+220]=WARNING
    return bytes(data)
def shrinks(index):
    old=PREFIXES[index];count=0
    for size in CHUNKS:
        end=old+size;count+=((end+35+65535)//65536>(end+65535)//65536);old=end
    return count
def validate_log(mode,data):
    r=dict(passed=False,expected_shrinks=sum(shrinks(i) for i in range(11))*4,expected_checks=132)
    if data is None:return r
    try:
        lines=data.decode('ascii').splitlines();at=0;overlaps=[];dirty=[]
        def take(label,exact=None):
            nonlocal at
            words=lines[at].split();at+=1;assert words[0]==label and len(words)==4
            nums=[int(n) for n in words[1:]]
            if exact is not None:assert nums==exact,(label,nums,exact)
            return nums
        take('ATTEMPT_ONCE',[mode,11,4]);take('INSTALL_IDLE_START',[0,0,0])
        for round in range(4):
            for i,p in enumerate(PREFIXES):
                take('CASE_COMPLETE',[round,i,p+sum(CHUNKS)])
                take('CASE_SHRINKS',[round,i,shrinks(i)])
                a,b,n=take('CASE_OVERLAP');assert [a,b]==[round,i] and (n>0 if mode else n==0);overlaps.append(n)
                a,b,n=take('CASE_DIRTY_OVERLAP');assert [a,b]==[round,i] and (n>0 if mode else n==0);dirty.append(n)
        wait,flushes,error=take('FLUSH_JOIN');assert wait==0 and error==0 and (flushes>0 if mode else flushes==0)
        take('DIRTY_COVERAGE',[44*mode,sum(dirty),0])
        take('COVERAGE',[r['expected_shrinks'],132,sum(overlaps)])
        take('COMPLETE',[mode,792,44]);take('INSTALL_IDLE_END',[0,0,0]);take('NORMAL_RESTART_REQUEST',[0,0,0])
        assert at==len(lines)
        r.update(passed=True,completed_flushes=flushes,overlaps=overlaps,completed_flushes_within_append=sum(overlaps),dirty_overlaps=dirty,completed_flushes_within_dirty_mapping=sum(dirty),rendezvous=44*mode)
    except (ValueError,AssertionError,IndexError,UnicodeError) as exc:r['error']=repr(exc)
    return r
