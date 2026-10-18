# SPDX-License-Identifier: MIT
"""Static layout proposal only. No file writes, loading, or execution."""
import hashlib
import struct
from elf32 import u32

BASE=0x10000
CODE=0x94877
END=0x94c18
OLD=0x95000
SIZE=0x140
NEW=0x94c20

def check_base(base):
    if type(base) is not int or base%16 or base<END or base+SIZE>OLD:
        raise ValueError('aligned zero-gap extent')
    if base>>12!=(base+SIZE-1)>>12 or base>>12!=CODE>>12:
        raise ValueError('same code/data page')

def digest(b):
    return hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()

def proposal(original,old_sections,new_sections,text_index,data_index,base=NEW):
    """Compose an in-memory proposal from independently relocated sections.

    The original 510 namespace is intentional here; this is NOT a launchable
    candidate. A later build must use a fresh namespace and its own review.
    """
    check_base(base)
    if len(original)!=OLD+SIZE-BASE or any(original[END-BASE:OLD-BASE]):
        raise ValueError('original extent/gap')
    if old_sections[data_index]!=original[OLD-BASE:] or len(new_sections[data_index])!=SIZE:
        raise ValueError('original data/size')
    if old_sections[text_index][CODE-BASE:END-BASE]!=original[CODE-BASE:END-BASE]:
        raise ValueError('original diagnostic')
    if old_sections[text_index][:CODE-BASE]!=new_sections[text_index][:CODE-BASE]:
        raise ValueError('unrelated text changed')
    b=bytearray(original)
    b[CODE-BASE:END-BASE]=new_sections[text_index][CODE-BASE:END-BASE]
    b[base-BASE:base+SIZE-BASE]=new_sections[data_index]
    b[0x348+36:0x348+56]=digest(b)
    return bytes(b)

def validate(b,original,ledger,text_index,data_index,base=NEW):
    """Independent inverse-normalization contract, not another ELF linker.

    Every active old-data pointer must move by the same delta; other bytes must
    reconstruct the pinned original. Caller must pin/review the original ledger.
    """
    check_base(base)
    if len(b)!=len(original) or len(b)!=OLD+SIZE-BASE:
        raise ValueError('image extent')
    if b[0x348+36:0x348+56]!=digest(b):raise ValueError('section digest')
    if b[OLD-BASE:]!=original[OLD-BASE:]:raise ValueError('retained old tail')
    if any(b[END-BASE:base-BASE]) or any(b[base+SIZE-BASE:OLD-BASE]):
        raise ValueError('unused gap')
    fixed=bytearray(b)
    data=bytearray(b[base-BASE:base+SIZE-BASE])
    for row in ledger:
        if row['symbol_section']!=data_index:continue
        if row['kind']!=1 or not OLD<=row['value']<OLD+SIZE:
            raise ValueError('pointer contract')
        if row['section']==text_index:
            at=row['address']-BASE;dest=fixed
            if not CODE<=row['address']<END-3:raise ValueError('outside diagnostic')
        elif row['section']==data_index:at=row['offset'];dest=data
        else:raise ValueError('unknown destination')
        if u32(dest,at)!=row['value']+base-OLD:raise ValueError('relocated pointer')
        struct.pack_into('<I',dest,at,row['value'])
    if bytes(data)!=original[OLD-BASE:]:raise ValueError('data values')
    fixed[base-BASE:base+SIZE-BASE]=bytes(SIZE)
    fixed[0x348+36:0x348+56]=original[0x348+36:0x348+56]
    if bytes(fixed)!=original:raise ValueError('unapproved change')
    return True
