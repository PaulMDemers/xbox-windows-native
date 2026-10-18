# SPDX-License-Identifier: MIT
"""A pinned, in-memory extent proposal. No filesystem or runtime operations."""
import hashlib
import struct

BASE=0x10000
END=0x94d60
SIZE=END-BASE
ORIGINAL_SIZE=545088
ORIGINAL_SHA='a272c18d32f96719ddf5ec07dcc551f74165f797b8247b361c1a4e3b3d84da1d'
FIELDS=(0x10c,0x350,0x358)
DIGEST=slice(0x36c,0x380)

def digest(b):
    return hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()

def original(b):
    if len(b)!=ORIGINAL_SIZE or hashlib.sha256(b).hexdigest()!=ORIGINAL_SHA:
        raise ValueError('exact516 parent required')

def propose(b):
    original(b)
    if any(b[SIZE:0x85000]):raise ValueError('removed padding must be zero')
    q=bytearray(b[:SIZE])
    for off,value in zip(FIELDS,(SIZE,SIZE-4096,SIZE-4096)):
        struct.pack_into('<I',q,off,value)
    q[DIGEST]=digest(q)
    return bytes(q)

def validate(q,parent):
    original(parent)
    if len(q)!=SIZE:raise ValueError('exact shortened extent')
    if tuple(struct.unpack_from('<I',q,o)[0] for o in FIELDS)!=(SIZE,SIZE-4096,SIZE-4096):
        raise ValueError('three independent size fields')
    if q[DIGEST]!=digest(q):raise ValueError('section digest')
    inverse=bytearray(q)
    for off in FIELDS:inverse[off:off+4]=parent[off:off+4]
    inverse[DIGEST]=parent[DIGEST]
    if inverse!=parent[:SIZE]:raise ValueError('unapproved live/header/payload change')
    return True
