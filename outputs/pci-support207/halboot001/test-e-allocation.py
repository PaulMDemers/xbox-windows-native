"""Corruption checks for the new E: read-only audit; no disk image modifications."""
import json,struct
from e_allocation import audit_tree
end=0xffffffff
def entry(name,first,size=0,flags=0):
    b=bytearray(64);b[0]=len(name);b[1]=flags;b[2:2+len(name)]=name;struct.pack_into('<II',b,44,first,size);return b
def check(fat,root,valid):
    try:audit_tree(fat,len(fat),512,4,lambda _:bytes(root).ljust(512,b'\xff'))
    except AssertionError:assert not valid
    else:assert valid
cases=[([0,end,0,0],b'',True),([0,end,end,0],entry(b'a',2,512),True),([0,end,end,0],b'',False),([0,end,2,0],entry(b'a',2,1),False),([0,end,0,0],entry(b'a',7,1),False),([0,end,end,0],entry(b'a',2,513),False),([0,end,end,0],entry(b'a',2,1)+entry(b'b',2,1),False),([0,end,end,0],entry(b'a',2,1)+entry(b'A',0),False),([0,end,0,0],entry(b'a',0,1),False),([0,end,0xfffffff7,0],b'',True),([0,end,0,0],entry(b'a/b',0),False)]
for f,r,v in cases:check(f,r,v)
print(json.dumps(dict(passed=True,cases=len(cases),scope=__doc__)))
