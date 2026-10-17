"""Independent, little-endian BGRX comparison; ignores only the unused X byte."""
import struct
W,H=1024,512
def expected(phase):
    if phase not in range(4):raise ValueError('phase')
    out=bytearray()
    for y in range(H):
        n=y+int(phase==1)
        one=b'\xff\xff\xff\0' if n%2 else b'\0'*4
        two=b'\xff\xff\xff\0' if (n//2)%2 else b'\0'*4
        out+=one*320+two*320
        for bit in range(10):out+=(b'\xff\xff\xff\0' if n&(1<<bit) else b'\0'*4)*32
        out+=(b'\0\xff\0\0' if n%2 else b'\xff\0\xff\0')*64
    return bytes(out)
def verify_pixels(data,phase):
    if len(data)!=W*H*4:raise ValueError('capture length')
    want=expected(phase)
    # Compare all color bytes; this is not a hash-based partial sample.
    if data[0::4]!=want[0::4] or data[1::4]!=want[1::4] or data[2::4]!=want[2::4]:
        raise ValueError('pixel mismatch')
    return W*H
def verify_log(text):
    rows=[line.split() for line in text.splitlines()]
    if any(len(r)!=4 for r in rows):raise ValueError('record shape')
    parsed=[(r[0],*(int(v) for v in r[1:])) for r in rows]
    if parsed[-1]!=('COMPLETE',4,8,0):raise ValueError('not complete')
    def select(tag):return [r[1:] for r in parsed if r[0]==tag]
    if select('SCANOUT')!=[(n,1,0) for n in range(8)]:raise ValueError('scanout comparisons')
    if select('PIXELS')!=[(n,W*H,0) for n in range(8)]:raise ValueError('pixel comparisons')
    if [r[0] for r in select('PHASE_DONE')]!=list(range(4)):raise ValueError('phases')
    if any(tag in ('FAILED','FAIL') for tag,*_ in parsed):raise ValueError('failure')
    return True
