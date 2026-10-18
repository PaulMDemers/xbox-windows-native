# SPDX-License-Identifier: MIT
"""Exact516 extent child with new namespace; bytes only, no I/O."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'image-extent519'))
import extent
OLD=b'XWNBoot516a';NEW=b'XWNBoot520a'

def offsets(parent):
    extent.original(parent)
    rows=[];start=0
    while True:
        at=parent.find(OLD,start)
        if at<0:break
        if at+len(OLD)>extent.SIZE:raise ValueError('namespace outside live extent')
        rows.append(at);start=at+len(OLD)
    if len(rows)!=5 or sum(0x84c20<=a<extent.SIZE for a in rows)!=1:
        raise ValueError('exact five active namespaces')
    return rows

def prepare(parent):
    b=bytearray(extent.propose(parent))
    for at in offsets(parent):b[at:at+len(OLD)]=NEW
    b[extent.DIGEST]=extent.digest(b)
    return bytes(b)

def validate(b,parent):
    if len(b)!=extent.SIZE:raise ValueError('candidate extent')
    if b[extent.DIGEST]!=extent.digest(b):raise ValueError('candidate digest')
    inverse=bytearray(b)
    for at in offsets(parent):
        if b[at:at+len(NEW)]!=NEW:raise ValueError('candidate namespace')
        inverse[at:at+len(OLD)]=OLD
    inverse[extent.DIGEST]=extent.digest(inverse)
    return extent.validate(bytes(inverse),parent)
