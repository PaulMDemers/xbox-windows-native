"""Independently decode appended XBE section and preserve original payload/font."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'binary-review001.json';assert not out.exists()
B=Path('C:/xwn483/build001');P=Path('C:/xwn482/build001')
new=(B/'default.xbe').read_bytes();old=(P/'default.xbe').read_bytes()
u=lambda b,o:struct.unpack_from('<I',b,o)[0]
sha=lambda b:hashlib.sha256(b).hexdigest()
build=json.loads((K/'build001.json').read_text());sym=build['wrapper_symbols']
prior=json.loads((K.parent/'d3d-depth482/build001.json').read_text())['wrapper_symbols']
assert sha(new)==build['sha256'] and new[:4]==b'XBEH'
base=u(new,0x104);sections=u(new,0x120)-base
assert base==0x10000 and u(new,0x11c)==1 and u(new,0x10c)==len(new)
flags,va,vsize,raw,size=struct.unpack_from('<5I',new,sections)
assert flags==7 and va==base+raw and raw==4096 and vsize==size==len(new)-raw
assert new[sections+36:sections+56]==hashlib.sha1(struct.pack('<I',size)+new[raw:raw+size]).digest()
assert new[0x3000:len(old)]==old[0x3000:]
assert sym['kernel']==prior['kernel']==base+0x3000
assert new[sym['font']-base:sym['font']-base+4096]==old[prior['font']-base:prior['font']-base+4096]
assert new[sym['blentry']-base:sym['newloc']-base+40]==old[prior['blentry']-base:prior['newloc']-base+40]
assert not any(new[len(old):sym['witness_entry']-base])
assert sym['witness_entry']>=base+len(old) and sym['witness_path_end']<va+size
assert (u(new,0x128)^0xa8fc57ab)==sym['_start'] and (u(new,0x158)^0x5b6d40b6)==sym['section_1_start']
assert u(new,0x1080)==0x3000 and u(new,0x1084)==524862
out.write_text(json.dumps(dict(passed=True,sha256=sha(new),bytes=len(new),parent_bytes=len(old),section=dict(flags=flags,virtual_address=va,virtual_bytes=vsize,raw_offset=raw,raw_bytes=size),payload_byte_exact=True,font_byte_exact=True,privileged_prefix_byte_exact=True,original_entry_and_thunks=True,added_tail_bytes=len(new)-build['tail_offset'],header_changes=build['header_changes'],physical_loader_validation=False),indent=2)+'\n')
