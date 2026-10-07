"""Synthetic boundary/coverage tests, not guest evidence."""
import struct
from walk import *
data=bytearray(0x6000)
def put(at,v):struct.pack_into('<I',data,at,v)
put(0x1000+512*4,0x2003);put(0x2000,0x03c0001b);put(0x2004,0xf3c0101b)
r=scan_directory(data,0x1000);assert len(r['matches'])==2 and r['ptes_examined']==1024
assert physical(data,0x1000,0x80000007)==0x03c00007
assert {p['kind'] for p in r['matches']}=={'reserved_ram','gpu_aperture'}
put(0x1000+513*4,0x03c0109b);r=scan_directory(data,0x1000)
assert r['large_pdes']==1 and r['matches'][-1]['length']==0x400000 and r['matches'][-1]['pat']
assert physical(data,0x1000,0x807fffff)==0x03ffffff
put(0x1000+513*4,0x03c02083)
try:scan_directory(data,0x1000);raise RuntimeError('accepted PSE36')
except AssertionError:pass
put(0x1000+513*4,0x6003)
try:scan_directory(data,0x1000);raise RuntimeError('accepted missing page table')
except AssertionError:pass
put(0x1000+513*4,0x6002);r=scan_directory(data,0x1000);assert r['present_pdes']==1
put(0x2004,0x03c0101b);r=scan_directory(data,0x1000);assert len(ranges(r['matches']))==1 and ranges(r['matches'])[0]['length']==8192
put(0x2004,0x03c01003);assert len(ranges(scan_directory(data,0x1000)['matches']))==2
put(0x2000,0x03bff003);put(0x2004,0x04000003);assert not scan_directory(data,0x1000)['matches']
print('Synthetic 4KiB/4MiB, both targets, exact bounds, PAT, missing/absent table, PSE36 and range split checks passed')
