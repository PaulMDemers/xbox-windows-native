"""Useful failure gates: wrong retained data, rearm, truncation, missing epoch."""
import struct
from oracle import *
checks=[]
def u(b,x,y):return struct.unpack_from('<I',b,(y*W+x)*4)[0]
for epoch in range(2):
    for depth in range(2):
        a,b,c,d=[expected(epoch,depth,s) for s in range(4)]
        assert u(a,0,0)==([0xa5317ca4,0x345678a5][depth]^(epoch*0x01010100))
        assert u(b,3,5)==0x52100000^(epoch<<20)^(depth<<19)^(16<<12)^(5<<6)^3
        assert u(c,3,5)==u(b,3,5) and u(c,18,13)==u(b,18,13)
        assert u(c,19,13)!=u(b,19,13) and u(c,116,66)==u(a,116,66)
        assert len(d)==W*H*4 and u(d,3,5)==u(d,500,300)
        for wrong in [None,c[:-4],a,b,d]:assert not compare(wrong,c)['matched']
        assert compare(c,c)['matched']
        checks.append(dict(epoch=epoch,depth=depth,gates=6))
lines=['BEGIN 143 2 2 4 640 480 17']
for e in range(2):
    lines += [f'INIT_BEGIN {e}',f'INIT_RETURN {e} 0']
    for z in range(2):
        base=0x1000000+z*0x200000
        lines += [f'SURFACE {e} {z} {base:08x} 2560']+[f'CAPTURE {e} {z} {s} {base:08x} 2560 1228800' for s in range(4)]
    lines += [f'KILL_BEGIN {e}',f'KILL_RETURN {e}']
lines += ['COMPLETE 16 120292 0','NORMAL_REBOOT_REQUEST']
good=('\r\n'.join(lines)+'\r\n').encode();assert len(validate_log(good))==4
bad=[good.replace(b'COMPLETE 16 120292 0',b'COMPLETE 16 120292 1'),good.replace(b'KILL_RETURN 0\r\n',b''),good[:-25],good+b'EXTRA\r\n']
for data in bad:
    try:validate_log(data)
    except AssertionError:pass
    else:raise AssertionError('Malformed protocol accepted')
if __name__=='__main__':
    import json
    print(json.dumps(dict(passed=True,byte_oracle_cases=checks,protocol_failure_gates=len(bad)),indent=2))
