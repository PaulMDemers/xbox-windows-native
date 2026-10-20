"""Fixed-version WINMM frame interpretation; unsupported instruction sites fail."""
import struct

OFFSETS={r:0 for r in (0x7bbc,0x7bc3,0x7bc9,0x7bce,0x7bd4,0x7bda,0x7bdc,0x7be2,0x7bf6,0x7bfc)}
OFFSETS.update({0x7be4:4,0x7be9:8,0x7bef:8,0x7bf0:12,0x7bf1:16,0x7bfd:20,0x7bfe:24,0x7bff:28,0x7c40:28,0x7c41:24,0x7c42:20})
OFFSETS.update({r:32 for r in (0x7c00,0x7c02,0x7c06,0x7c08,0x7c0e,0x7c12,0x7c14,0x7c1a,0x7c1c,0x7c22,0x7c26,0x7c2a,0x7c2c,0x7c2e,0x7c30,0x7c34,0x7c36,0x7c38,0x7c39,0x7c3f)})

def frame_return(base,rva,stack):
    assert 0<base<2**32-0x7c45 and rva in OFFSETS and len(stack)==64
    offset=OFFSETS[rva]
    if rva>=0x7bfd:assert struct.unpack_from('<I',stack,offset-20)[0]==base+0x7bf6
    ret=struct.unpack_from('<I',stack,offset)[0]
    assert 32<=ret<2**32-32
    return ret

def call_target(ret,code,slot):
    assert 32<=ret<2**32-32 and len(code)==64
    if code[26:28]==b'\xff\x15':
        address=struct.unpack_from('<I',code,28)[0]
        assert slot is not None and slot[0]==address and len(slot[1])==4
        return struct.unpack('<I',slot[1])[0], 'indirect absolute memory call'
    if code[27]==0xe8:
        return (ret+struct.unpack_from('<i',code,28)[0])&0xffffffff, 'direct relative call'
    return None, 'unsupported call encoding; return address only'
