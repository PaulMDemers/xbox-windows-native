# SPDX-License-Identifier: MIT
"""516 byte contract, reusing frozen515 static relocation definitions."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'data-layout515'))
import elf32
import layout

OLD_NAME=b'XWNBoot510a'
NEW_NAME=b'XWNBoot516a'

def prepare(original,obj):
    e=elf32.parse(obj);t=e['named']['.text'];d=e['named']['.data']
    old,ledger=elf32.relocated(e,{t:layout.BASE,d:layout.OLD})
    new,_=elf32.relocated(e,{t:layout.BASE,d:layout.NEW})
    expected=bytearray(layout.proposal(original,old,new,t,d))
    offsets=[];start=0
    while True:
        off=expected.find(OLD_NAME,start)
        if off<0:break
        if off<layout.OLD-layout.BASE:offsets.append(off)
        start=off+len(OLD_NAME)
    if len(offsets)!=5 or sum(layout.NEW-layout.BASE<=off<layout.NEW+layout.SIZE-layout.BASE for off in offsets)!=1:
        raise ValueError('active namespace inventory')
    for off in offsets:expected[off:off+len(NEW_NAME)]=NEW_NAME
    expected[0x36c:0x380]=layout.digest(expected)
    return bytes(expected),ledger,t,d,offsets

def validate(b,original,ledger,t,d,offsets):
    if len(offsets)!=5 or len(set(offsets))!=5:raise ValueError('namespace manifest')
    if len(b)!=len(original):raise ValueError('image length')
    if b[0x36c:0x380]!=layout.digest(b):raise ValueError('candidate digest')
    restored=bytearray(b)
    for off in offsets:
        if b[off:off+len(NEW_NAME)]!=NEW_NAME:raise ValueError('candidate namespace')
        restored[off:off+len(OLD_NAME)]=OLD_NAME
    restored[0x36c:0x380]=layout.digest(restored)
    return layout.validate(bytes(restored),original,ledger,t,d)
