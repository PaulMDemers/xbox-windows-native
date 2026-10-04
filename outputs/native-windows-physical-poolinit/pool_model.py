"""Independent audit of the pinned kernel's initial pool structures and writes."""
import hashlib, json, struct

POOL = 0xfe4af000
FREE = POOL + 0x4000
SIZE = 0x1f8000

def verify_pool_initialized(read, kernel):
    u32 = lambda va: struct.unpack('<I', read(va,4))[0]
    expected = {0x727f4:0x4000,0x73dec:0,0x811c0:POOL,0x82390:SIZE,
        0x82320:0x1731000,0x81384:POOL+SIZE,0x824a4:POOL,0x82268:4,
        0x81b80:500,0x81ac0:504,0x81388:0x373,0x81378:0x9ff,
        0x8125c:0xc03f9aa0,0x81264:0xc03fef7c,0x8239c:0x7e6a8000,
        0x8121c:5432,0x82334:0xc0200000}
    for off,value in expected.items():
        assert u32(kernel+off)==value,(hex(off),hex(u32(kernel+off)),hex(value))
    for i in range(4):
        head=kernel+0x81320+i*8
        assert struct.unpack('<2I',read(head,8))==((FREE,FREE) if i==3 else (head,head))
    assert struct.unpack('<3I',read(FREE,12))==(kernel+0x81338,kernel+0x81338,500)
    for i in range(4):assert u32(POOL+i*4096)==(POOL+(i+1)*4096 if i<3 else 0)
    for i in range(500):assert u32(FREE+i*4096+16)==FREE
    ptes=b''.join(read(0xc03f9aa0+off,min(4096,5432*4-off)) for off in range(0,5432*4,4096))
    assert ptes==struct.pack('<2I',0xfffff000,5432<<12)+bytes((5432-2)*4)
    assert u32(0xc03f9a9c)==0 and u32(0xc03fef80)==0
    return {'must_succeed_pages':4,'free_pool_pages':500,'page_owner_links_verified':500,
        'expansion_ptes':5432,'list_heads_verified':4,'pool_initialized':True,
        'expansion_guard_ptes_unchanged':True}

def snapshot_pool(port, output):
    from monitor_capture import command
    path=output.with_suffix('.pool.bin')
    command(port,'pmemsave '+str(0x17c000)+' '+str(SIZE)+' '+json.dumps(path.resolve().as_posix()))
    try:
        data=path.read_bytes();assert len(data)==SIZE;return data
    finally:path.unlink(missing_ok=True)

def verify_pool_delta(before, after, kernel):
    expected=bytearray(before)
    for i in range(4):struct.pack_into('<I',expected,i*4096,POOL+(i+1)*4096 if i<3 else 0)
    struct.pack_into('<3I',expected,0x4000,kernel+0x81338,kernel+0x81338,500)
    for i in range(500):struct.pack_into('<I',expected,0x4000+i*4096+16,FREE)
    assert after==expected,'Unexpected writes to nonpaged-pool backing'
    return {'only_expected_507_dword_writes':True,'pool_bytes_checked':len(after),
        'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(after).hexdigest()}
