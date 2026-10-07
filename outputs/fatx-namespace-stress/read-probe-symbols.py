"""Pin counter offsets in the exact executed diagnostic, without changing it."""
import hashlib,json,struct,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
p=k/'artifacts/probe.exe';data=p.read_bytes()
review=json.loads((k/'probe-review.json').read_text())
assert hashlib.sha256(data).hexdigest()==review['probe_sha256']
pe=struct.unpack_from('<I',data,60)[0];assert data[pe:pe+4]==b'PE\0\0'
base=struct.unpack_from('<I',data,pe+52)[0]
text=subprocess.check_output(['/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-nm','-n',str(p)],text=True)
symbols={s[2]:int(s[0],16)-base for line in text.splitlines() if len(s:=line.split())==3 and s[2] in ['_Errors','_Completed','_Start','_Log']}
assert len(symbols)==4
sections=[];count=struct.unpack_from('<H',data,pe+6)[0];optional=struct.unpack_from('<H',data,pe+20)[0]
for i in range(count):
    at=pe+24+optional+40*i
    name=data[at:at+8].split(b'\0')[0].decode('ascii')
    virtual,size,offset=struct.unpack_from('<III',data,at+12)
    if name=='.text':sections.append(dict(rva=virtual,raw_size=size,raw_offset=offset,sha256=hashlib.sha256(data[offset:offset+size]).hexdigest()))
assert len(sections)==1
r=dict(scope=__doc__,probe_sha256=review['probe_sha256'],preferred_base=base,counter_count=5,symbols=symbols,text=sections[0])
(k/'probe-symbols.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
