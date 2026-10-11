"""Independent byte oracles. No observed render output is used to define them."""
import struct
WIDTH,HEIGHT=16,8
def textures():
    # Explicit planes: red alternates columns, green rows, blue checkerboard,
    # fourth texture contributes a low-amplitude 2x2 checker to all RGB channels.
    x_red=([0,32]*8)*8
    y_green=[v for row in ([0]*16,[64]*16)*4 for v in row]
    blue=[128 if (column+row)%2 else 0 for row in range(8) for column in range(16)]
    low=[16 if ((column//2)+(row//2))%2 else 0 for row in range(8) for column in range(16)]
    return [b''.join(bytes(pixel) for pixel in plane) for plane in (
        [(0,0,r,255) for r in x_red],[(0,g,0,255) for g in y_green],
        [(b,0,0,255) for b in blue],[(v,v,v,255) for v in low])]
def blocks():
    result=[]
    for unit,payload in enumerate(textures()):
        guard=bytearray((0xa5^unit^(offset*13))&255 for offset in range(4096))
        guard[256:768]=payload;result.append(bytes(guard))
    return result
def framebuffer():
    ts=textures();pixels=[]
    for y in range(-1,9):
        for x in range(-1,17):
            if x<0 or x>=16 or y<0 or y>=8: pixel=bytes([12,12,12,255])
            else:
                i=(16*y+x)*4
                pixel=bytes([sum(t[i+c] for t in ts) for c in range(3)]+[255])
            pixels.append(pixel)
    return b''.join(pixels)
def validate_record(data):
    assert len(data)==1612
    h=struct.unpack_from('<43I',data)
    assert h[0:3]==(0x58323731,271,1612)
    assert h[4]==0 and h[22:27]==(16,8,64,4096,256)
    assert 2560<=h[29]<=4096 and h[29]%64==0 and h[30]==480 and h[32]==384
    assert h[34]==3 and all(x<=10000 for x in h[35:38])
    assert h[39:43]==(0,0,0,0)
    for u in range(4):
        assert h[14+u]==h[6+u]+256 and h[18+u]==h[10+u]+256
    ranges=[(h[10+u],4096) for u in range(4)]+[(h[28],h[29]*h[30]),(h[33],384)]
    for i,(start,size) in enumerate(ranges):
        assert start>0 and start+size<=0x03ffb000
        for other,other_size in ranges[:i]:assert start+size<=other or other+other_size<=start
    expected=framebuffer()
    assert data[172:892]==expected and data[892:1612]==expected
    # This validates bytes only; phase/cookie/callsite/ownership need live attestation.
    return True
