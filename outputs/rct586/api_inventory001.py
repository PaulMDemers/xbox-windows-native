"""Read-only PE metadata for choosing future observation points, not a call trace."""
import hashlib,json,re,sys
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
expected=json.loads((K.parent/'rct565/package001.json').read_text())['files']['game/RCT.EXE']
p=Path('C:/xwn566/transfer002/game/RCT.EXE');data=p.read_bytes()
digest=hashlib.sha256(data).hexdigest();assert digest==expected['sha256'] and len(data)==expected['bytes']
pe=pefile.PE(data=data)
imports=[]
for dll in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[]):
    imports.append(dict(module=dll.dll.decode('ascii'),symbols=[dict(name=x.name.decode('ascii') if x.name else None,ordinal=x.ordinal,iat_va=hex(x.address)) for x in dll.imports]))
patterns=[b'ddraw.dll',b'DirectDrawCreate',b'DirectDrawCreateEx',b'DirectDrawEnumerateA',b'd3dim.dll',b'd3d8.dll',b'BitBlt',b'StretchDIBits',b'SetDIBitsToDevice',b'GetProcAddress',b'LoadLibraryA']
strings=[]
for term in patterns:
    for m in re.finditer(re.escape(term)+b'\0',data,re.I):
        try:rva=pe.get_rva_from_offset(m.start())
        except pefile.PEFormatError:rva=None
        strings.append(dict(symbol=term.decode(),file_offset=hex(m.start()),rva=hex(rva) if rva is not None else None))
out=K/'api-inventory001.json';assert not out.exists()
out.write_text(json.dumps(dict(executable_sha256=digest,bytes=len(data),machine=hex(pe.FILE_HEADER.Machine),image_base=hex(pe.OPTIONAL_HEADER.ImageBase),imports=imports,selected_literal_locations=strings,read_only=True,physical_access=False,limits='Static imports and literal locations only. No execution, call counts, COM interface identity, surface capability, timing, FPS or acceleration evidence.'),indent=2)+'\n')
print(json.dumps(dict(imports=imports,selected_literal_locations=strings)))
