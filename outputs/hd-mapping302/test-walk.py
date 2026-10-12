"""Independent2304-page translation oracle and malformed-table negative cases."""
import hashlib,importlib.util,json,struct
from pathlib import Path
from walk import physical,scan_directory,ranges
k=Path(__file__).resolve().parent;dest=k/'host-tests.json';assert not dest.exists()
data=bytearray(0x10000);checks=0
def put(a,v):struct.pack_into('<I',data,a,v)
for i in range(3):put(0x1000+(896+i)*4,0x2000+i*4096|3)
for page in range(2304):put(0x2000+page*4,0x03700000+page*4096|0x1b)
for page in range(2304):
    for offset in [0,4095]:
        assert physical(data,0x1000,0xe0000000+page*4096+offset)==0x03700000+page*4096+offset;checks+=1
r=scan_directory(data,0x1000);g=ranges(r['matches']);assert len(g)==1 and g[0]['length']==0x900000;checks+=1
put(0x2000+100*4,0x03764003);g=ranges(scan_directory(data,0x1000)['matches']);assert len(g)==3;checks+=1
put(0x2000+100*4,0x0376401b)
put(0x1000+899*4,0x0400009b);assert len(scan_directory(data,0x1000)['matches'])==2304;checks+=1
put(0x1000+899*4,0x0340009b);r=scan_directory(data,0x1000);assert r['matches'][-1]['length']==0x100000 and r['matches'][-1]['physical']==0x03700000;checks+=1
for entry in [0x03402083,0x10003]:
    put(0x1000+899*4,entry)
    try:scan_directory(data,0x1000)
    except AssertionError:checks+=1
    else:raise AssertionError('Accepted unsupported/out-of-capture table')
spec=importlib.util.spec_from_file_location('discovery',k/'kernel-discovery.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
idt=0x82800000;base=0x82400000;rvas={0:0x65048,14:0x67028}
gates={idt+v*8:struct.pack('<HHBBH',(base+rva)&65535,8,0,0x8e,(base+rva)>>16) for v,rva in rvas.items()}
assert d.discover(lambda a,n:gates[a],idt,2047,rvas)[0]==base;checks+=1
gates[idt+14*8]=gates[idt]
try:d.discover(lambda a,n:gates[a],idt,2047,rvas)
except AssertionError:checks+=1
else:raise AssertionError('Accepted inconsistent trap bases')
dest.write_text(json.dumps(dict(passed=True,checks=checks,walker_sha256=hashlib.sha256((k/'walk.py').read_bytes()).hexdigest(),
                               scope='Synthetic translation and discovery only; no runtime observation'),indent=2)+'\n')
print('Host checks',checks)
