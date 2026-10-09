"""One CloseHandle EBP frame, only for its verified standard prologue/call site.

No FPO guesses, return-address scans or recursive EBP walk. The runtime caller
must separately pin the actual wrapper prologue and return site in kernel32.
"""
import struct
def capture_frame(read,cpu,teb,handle):
    u32=lambda address:struct.unpack('<I',read(address,4))[0]
    limit,base=u32(teb+8),u32(teb+4)
    ebp,esp=cpu['EBP'],cpu['ESP']
    assert 0x10000<=limit<base<=0x80000000
    assert limit<=esp<=ebp and ebp+12<=base
    assert ebp==esp+8, 'Exact verified wrapper stack contract required'
    previous,ret,arg=struct.unpack('<3I',read(ebp,12))
    assert arg==handle and 0x10000<=ret<0x80000000
    return dict(ebp=ebp,esp=esp,stack_limit=limit,stack_base=base,
                previous_ebp=previous,return_address=ret,handle=arg,
                previous_frame_walked=False)
