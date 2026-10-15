import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent
base=Path('/mnt/c/xwn403/installed-reference001/payload/E/winnt/system32/drivers/halxboxnt5.dll')
if not base.exists():
 matches=list(Path('/mnt/c/xwn403/installed-reference001').rglob('halxboxnt5.dll'));assert len(matches)==1;base=matches[0]
new=Path('/home/paul/xbox-windows-native/hal403002xxxxxxxx/artifacts/halxboxnt5.dll')
a=base.read_bytes();b=new.read_bytes();assert len(a)==len(b)
def fields(data):
 pe=struct.unpack_from('<I',data,60)[0];opt=pe+24;count=struct.unpack_from('<H',data,pe+6)[0];n=struct.unpack_from('<H',data,pe+20)[0];sections={}
 for i in range(count):
  p=opt+n+40*i;name=data[p:p+8].rstrip(b'\0').decode();size,raw=struct.unpack_from('<II',data,p+16);sections[name]=(raw,size)
 return {'coff_timestamp':(pe+8,4),'pe_checksum':(opt+64,4),'export_timestamp':(sections['.edata'][0]+4,4)},sections
fa,sa=fields(a);fb,sb=fields(b);assert fa==fb and sa==sb
changed=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y];allowed={i for o,n in fa.values() for i in range(o,o+n)}
r={'installed_sha256':hashlib.sha256(a).hexdigest(),'rebuilt_sha256':hashlib.sha256(b).hexdigest(),'different_bytes':len(changed),'all_differences_in_timestamp_or_checksum':set(changed)<=allowed,'fields':{n:{'offset':o,'installed':a[o:o+sz].hex(),'rebuilt':b[o:o+sz].hex()} for n,(o,sz) in fa.items()},'sections':{n: a[o:o+sz]==b[o:o+sz] for n,(o,sz) in sa.items()},'scope':'New canonical source-path build compared to installed HAL, no deployment'}
(k/'hal-correspondence003.json').write_text(json.dumps(r,indent=2)+'\n');assert r['all_differences_in_timestamp_or_checksum'];print(json.dumps(r,indent=2))
