"""Independently reject nonmetadata changes; use already completed HAL comparison."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent
old=next(Path('/mnt/c/xwn403/installed-reference001').rglob('halxboxnt5.dll')).read_bytes()
new=Path('/home/paul/xbox-windows-native/hal403002xxxxxxxx/artifacts/halxboxnt5.dll').read_bytes()
record=json.loads((K/'hal-correspondence003.json').read_text())
assert hashlib.sha256(old).hexdigest()==record['installed_sha256']
assert hashlib.sha256(new).hexdigest()==record['rebuilt_sha256']
allowed=set()
for row in record['fields'].values():allowed.update(range(row['offset'],row['offset']+4))
def equal(a,b):
 if len(a)!=len(b):return False
 aa=bytearray(a);bb=bytearray(b)
 for n in allowed:aa[n]=bb[n]=0
 return aa==bb
assert equal(old,new)
pe=struct.unpack_from('<I',old,60)[0];opt=pe+24
count=struct.unpack_from('<H',old,pe+6)[0];optional=struct.unpack_from('<H',old,pe+20)[0]
tested=[]
for i in range(count):
 at=opt+optional+i*40;size,raw=struct.unpack_from('<II',old,at+16)
 for offset in [at,raw,raw+size//2,raw+size-1] if size else [at]:
  if offset in allowed:continue
  changed=bytearray(new);changed[offset]^=1
  assert not equal(old,changed)
  tested.append(offset)
assert not equal(old,new[:-1]) and not equal(old,new+b'\0')
(K/'correspondence-controls001.json').write_text(json.dumps({'nonmetadata_mutations_rejected':len(tested),'length_mutations_rejected':2,'hal_source_comparison_passed':True,'scope':'Timestamp/checksum exclusion only; no runtime deployment'},indent=2)+'\n')
print(len(tested)+2)
