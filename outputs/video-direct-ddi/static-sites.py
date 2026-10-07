"""Extract pinned COFF function leads; these are NOT runtime observations."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
path=k/'candidate001/artifacts/xwndir.dll';data=path.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(data)==json.loads((k/'pe-review.json').read_text())['display_sha256']
pe=pefile.PE(data=data);offset=pe.FILE_HEADER.PointerToSymbolTable;count=pe.FILE_HEADER.NumberOfSymbols
strings=offset+count*18;size=struct.unpack_from('<I',data,strings)[0];assert strings+size<=len(data)
wanted=['XwnDirectEscape','DrvEnableDriver','DrvEnablePDEV','DrvCompletePDEV','DrvEnableSurface','DrvDisableSurface','DrvDisablePDEV','DrvAssertMode','GetAvailableModes']
rows=[];index=0
while index<count:
 at=offset+18*index;name=data[at:at+8];value,section,typ,storage,aux=struct.unpack_from('<IhHBB',data,at+8);index+=1+aux
 if name[:4]==bytes(4):
  pos=struct.unpack('<I',name[4:])[0];assert 4<=pos<size;name=data[strings+pos:strings+size].split(b'\0')[0]
 else:name=name.split(b'\0')[0]
 name=name.decode('ascii',errors='strict')
 plain=name.lstrip('_').split('@')[0]
 if plain not in wanted or section<=0:continue
 sec=pe.sections[section-1];rva=sec.VirtualAddress+value
 assert sec.Characteristics&0x20000000
 rows.append(dict(name=name,rva=rva,section=sec.Name.rstrip(b'\0').decode(),entry16=pe.get_data(rva,16).hex()))
assert sorted(r['name'].lstrip('_').split('@')[0] for r in rows)==sorted(wanted)
dest=k/'static-sites.json';assert not dest.exists()
r=dict(binary_sha256=sha(data),source_sha256=sha(Path(__file__).read_bytes()),preferred_base=pe.OPTIONAL_HEADER.ImageBase,sites=rows,limits=__doc__)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
