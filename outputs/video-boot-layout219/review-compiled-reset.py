"""Check actual compiled reset operands against named globals; no guest launch."""
import hashlib,json,re,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'compiled-reset-review.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(source_sha256=sha(Path(__file__)),passed=True,physical_access=False,guest_launch=False,cases={})
for case,entry in read(k/'build-review.json')['binaries'].items():
 path=k/'artifacts/build001'/case/'xboxbvid.dll';assert sha(path)==entry['sha256'];pe=pefile.PE(str(path));rva=entry['symbols']['_ResetDisplay']['rva'];raw=pe.get_data(rva,64);base=entry['image_base'];symbols=entry['symbols'];dis=k/'artifacts/reset-disassembly'/(case+'.txt');text=dis.read_text()
 if case=='control001':
  assert raw[0x19:0x21]==bytes.fromhex('c744240800004000');amount=0x400000;calloff=0x2c
 else:
  assert raw[0x14:0x19]==b'\xa1'+struct.pack('<I',base+symbols['_BootWritableBytes']['rva'])
  assert raw[0x21:0x25]==bytes.fromhex('89442408');amount='loaded from BootWritableBytes';calloff=0x2d
 assert raw[calloff]==0xe8
 target=base+rva+calloff+5+struct.unpack_from('<i',raw,calloff+1)[0]
 assert re.search(r'call\s+'+format(target,'x')+r'\s+<_memset>',text)
 r['cases'][case]=dict(binary_sha256=sha(path),reset_rva=rva,first64_hex=raw.hex(),clear_amount=amount,memset_target=target,disassembly_sha256=sha(dis),exact_operands_verified=True)
r['limits']='Compiled clear operand and actual resident64-byte candidate pin support the bounded reset implementation. No runtime tail sentinel or crash rendering is implied.'
dest.write_text(json.dumps(r,indent=2)+'\n');print('Compiled control/candidate reset operand review PASS')
