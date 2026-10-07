"""Independent expected bytes and identities for ordinary mapped-append regression."""
import hashlib,importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'))
from coldio import ColdIO
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
PREFIXES=[401,511,512,513,3985,4095,4096,4097,65425,65535,65536,65537,270225]
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
def protocol(mode):
    lines=[f'ATTEMPT_ONCE {mode} 13 4','INSTALL_IDLE_START 0 0 0']
    lines += [f'CASE_COMPLETE {r} {i} {p+sum(CHUNKS)}' for r in range(4) for i,p in enumerate(PREFIXES)]
    lines += [f'COMPLETE {mode} 936 52','INSTALL_IDLE_END 0 0 0','NORMAL_RESTART_REQUEST 0 0 0']
    return ('\r\n'.join(lines)+'\r\n').encode('ascii')
