"""Check the opt-in loader changes leave default executable bytes unchanged."""
import pathlib,struct,hashlib,json
k=pathlib.Path(__file__).resolve().parent
old=(k/'package/E/Applications/XWNFBoot/freeldr.sys').read_bytes()
new=(k/'artifacts-normal/freeldr.sys').read_bytes()
def normalized(data):
 b=bytearray(data);pe=b.find(b'PE\0\0');assert pe>=0
 optional=pe+24;assert struct.unpack_from('<H',b,optional)[0]==0x10b
 # freeldr.sys prepends its start sector to the embedded PE image.
 base=next(i for i in range(pe) if b[i:i+2]==b'MZ' and i+struct.unpack_from('<I',b,i+60)[0]==pe)
 count=struct.unpack_from('<H',b,pe+6)[0];optional_size=struct.unpack_from('<H',b,pe+20)[0]
 def raw(rva):
  for i in range(count):
   off=optional+optional_size+i*40;vs,va,rs,rp=struct.unpack_from('<IIII',b,off+8)
   if va<=rva<va+max(vs,rs):return base+rp+rva-va
  raise AssertionError(('RVA outside sections',rva))
 debug,size=struct.unpack_from('<II',b,optional+96+6*8);assert size%28==0
 ignored=[(optional+64,4,'PE checksum')]
 exports,exportsize=struct.unpack_from('<II',b,optional+96)
 if exports and exportsize:ignored.append((raw(exports)+4,4,'export directory timestamp'))
 if debug and size:
  for off in range(raw(debug),raw(debug)+size,28):ignored.append((off+4,4,'debug directory timestamp'))
 for off,n,_ in ignored:b[off:off+n]=bytes(n)
 return bytes(b),ignored
a,fields=normalized(old);b,newfields=normalized(new)
assert fields==newfields and a==b
sha=lambda b:hashlib.sha256(b).hexdigest()
r={'scope':'FATX_F_BOOT disabled build regression','baseline_sha256':sha(old),'rebuilt_sha256':sha(new),'ignored_metadata':fields,'executable_bytes_equal':True}
(k/'default-build-check.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
