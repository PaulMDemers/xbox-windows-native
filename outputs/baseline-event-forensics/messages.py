"""Decode observed IDs from the exact closed emulator's owned message resources."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
out=k/'messages.json';assert not out.exists()
state=json.loads((k/'cold-state.json').read_text())
targets=[('winnt/system32/netevent.dll',0xc0001b58),('winnt/system32/kernel32.dll',2),
         ('winnt/system32/iologmsg.dll',0xc0040031),('winnt/system32/drivers/ftdisk.sys',0xc0040031)]
result=[]
for path,target in targets:
    row=next(r for r in state['files'] if r['path']==path);p=k/'artifacts'/row['private_copy'];data=p.read_bytes()
    assert hashlib.sha256(data).hexdigest()==row['sha256'];pe=pefile.PE(data=data);matches=[]
    for kind in getattr(pe,'DIRECTORY_ENTRY_RESOURCE',[]).entries if hasattr(pe,'DIRECTORY_ENTRY_RESOURCE') else []:
        if kind.id!=11:continue
        for name in kind.directory.entries:
            for language in name.directory.entries:
                d=language.data.struct;b=pe.get_data(d.OffsetToData,d.Size)
                blocks=struct.unpack_from('<I',b)[0];assert 4+blocks*12<=len(b)
                for i in range(blocks):
                    low,high,offset=struct.unpack_from('<III',b,4+i*12)
                    if not low<=target<=high:continue
                    for ident in range(low,target+1):
                        length,flags=struct.unpack_from('<HH',b,offset);assert length>=4 and offset+length<=len(b)
                        if ident==target:
                            text=b[offset+4:offset+length].decode('utf-16le' if flags&1 else 'cp1252').rstrip('\0')
                            matches.append(dict(language=language.id,flags=flags,message=text))
                        offset+=length
    result.append(dict(path=path,file_sha256=row['sha256'],event_id_hex=f'{target:08x}',messages=matches))
assert result[0]['messages'] and result[1]['messages'] and (result[2]['messages'] or result[3]['messages'])
r=dict(scope=__doc__,physical_access=False,resources=result,limits='Exact message meaning, not proof that configured dump/pagefile requirements were met or an attribution of filesystem corruption.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
