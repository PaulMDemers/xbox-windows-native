"""Resolve the shutdown popup wording using the owned NT5 message resource."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
path=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntdll.dll')
pe=pefile.PE(str(path));target=0xc000026b;matches=[]
for kind in pe.DIRECTORY_ENTRY_RESOURCE.entries:
    if kind.id!=11:continue
    for name in kind.directory.entries:
        for language in name.directory.entries:
            d=language.data.struct;b=pe.get_data(d.OffsetToData,d.Size)
            blocks=struct.unpack_from('<I',b)[0]
            for i in range(blocks):
                low,high,offset=struct.unpack_from('<III',b,4+i*12)
                if not low<=target<=high:continue
                for ident in range(low,target+1):
                    length,flags=struct.unpack_from('<HH',b,offset);assert length>=4 and offset+length<=len(b)
                    if ident==target:
                        text=b[offset+4:offset+length].decode('utf-16le' if flags&1 else 'cp1252').rstrip('\0')
                        matches.append(dict(language=language.id,flags=flags,message=text))
                    offset+=length
assert matches
out=dict(scope=__doc__,file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),event_id_hex=f'{target:08x}',messages=matches,limits='Message meaning only; does not identify the runtime raising process or call path.')
(k/'popup-message.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
