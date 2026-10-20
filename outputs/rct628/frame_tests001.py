"""Reject malformed frame/call captures; do not guess unsupported callers."""
import json,struct
from pathlib import Path
from frame_layout import OFFSETS,frame_return,call_target
K=Path(__file__).resolve().parent;out=K/'frame-tests001.json';assert not out.exists()
base=0x77570000;ret=0x401234
for rva,off in OFFSETS.items():
    stack=bytearray(64)
    if rva>=0x7bfd:struct.pack_into('<I',stack,off-20,base+0x7bf6)
    struct.pack_into('<I',stack,off,ret)
    assert frame_return(base,rva,stack)==ret
code=bytearray(64);code[26:28]=b'\xff\x15';struct.pack_into('<I',code,28,0x403000)
slot=(0x403000,struct.pack('<I',base+0x7bbc))
assert call_target(ret,code,slot)[0]==base+0x7bbc
relative=bytearray(64);relative[27]=0xe8;struct.pack_into('<i',relative,28,base+0x7bbc-ret)
assert call_target(ret,relative,None)[0]==base+0x7bbc
assert call_target(ret,bytes(64),None)[0] is None
negative=[('boundary',lambda:frame_return(base,0x7bbd,bytes(64))),
 ('short-stack',lambda:frame_return(base,0x7bbc,bytes(63))),
 ('bad-internal-return',lambda:frame_return(base,0x7c00,bytes(64))),
 ('null-return',lambda:frame_return(base,0x7bbc,bytes(64))),
 ('short-code',lambda:call_target(ret,bytes(63),None)),
 ('missing-indirection',lambda:call_target(ret,code,None)),
 ('wrong-indirection',lambda:call_target(ret,code,(0x403004,slot[1]))),
 ('short-indirection',lambda:call_target(ret,code,(slot[0],slot[1][:3])))]
rejected=[]
for name,fn in negative:
    try:fn()
    except AssertionError:rejected.append(name)
    else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,frame_boundaries=len(OFFSETS),rejections=rejected,unsupported_encoding_preserved=True),indent=2)+'\n')
print('Fixed-frame boundaries and eight rejection cases passed')
