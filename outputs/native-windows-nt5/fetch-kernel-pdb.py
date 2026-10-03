import pathlib,struct,urllib.request,json,hashlib
r=pathlib.Path(__file__).resolve().parents[2]
p=r/'work/symbols/Windows_2000_(SP4)-ntoskrnl.dbg';data=p.read_bytes()
assert data[:2]==b'DI'
head=struct.unpack_from('<HHHH10I',data)
assert head[4]==0x4b7a1bd5 and head[7]==0x19d000
i=data.index(b'NB10');_,_,stamp,age=struct.unpack_from('<4sIII',data,i)
name=data[i+16:].split(b'\0',1)[0].decode().replace('\\','/').split('/')[-1]
assert name=='ntoskrnl.pdb'
key=f'{stamp:08X}{age:x}';url=f'https://msdl.microsoft.com/download/symbols/{name}/{key}/{name}'
with urllib.request.urlopen(url,timeout=20) as response:pdb=response.read(100*1024*1024)
target=r/'work/symbols/ntoskrnl-2195-7376.pdb';target.write_bytes(pdb)
report={'url':url,'dbg_matches_image_timestamp_and_size':True,'pdb_id':key,'bytes':len(pdb),'sha256':hashlib.sha256(pdb).hexdigest(),'pdb_file':str(target)}
(r/'outputs/native-windows-nt5/kernel-symbols.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
