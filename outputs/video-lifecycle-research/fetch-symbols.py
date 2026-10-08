"""Fetch exact owned win32k image symbols from Microsoft's symbol server only."""
import hashlib,json,struct,sys,urllib.request,urllib.error
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];art=k/'artifacts';art.mkdir(exist_ok=True)
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
path=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/win32k.sys');data=path.read_bytes()
assert hashlib.sha256(data).hexdigest()=='414cc2568ba7f11fa58490060c947477f44d6218e6c52e01deea1bbe8a364a92'
p=pefile.PE(data=data);dest=k/'symbol-fetch.json';assert not dest.exists()
r=dict(physical_access=False,guest_launched=False,image_path=str(path),image_sha256=hashlib.sha256(data).hexdigest(),timestamp=p.FILE_HEADER.TimeDateStamp,image_size=p.OPTIONAL_HEADER.SizeOfImage,requests=[])
def save():dest.write_text(json.dumps(r,indent=2)+'\n')
def fetch(name,key):
 url=f'https://msdl.microsoft.com/download/symbols/{name}/{key}/{name}';row=dict(url=url);r['requests'].append(row)
 try:
  with urllib.request.urlopen(url,timeout=25) as response:
   payload=response.read(32*1024*1024+1);assert len(payload)<=32*1024*1024
   row.update(status=response.status,bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest())
  out=art/name;assert not out.exists();out.write_bytes(payload);save();return payload
 except urllib.error.HTTPError as exc:row['status']=exc.code;save();return None
 except Exception as exc:row['error']=repr(exc);save();raise
key=f'{p.FILE_HEADER.TimeDateStamp:08X}{p.OPTIONAL_HEADER.SizeOfImage:x}';dbg=fetch('win32k.dbg',key)
if dbg is not None:
 assert dbg[:2]==b'DI';head=struct.unpack_from('<HHHH10I',dbg)
 assert head[4]==p.FILE_HEADER.TimeDateStamp and head[7]==p.OPTIONAL_HEADER.SizeOfImage
 at=dbg.index(b'NB10');_,_,stamp,age=struct.unpack_from('<4sIII',dbg,at);name=dbg[at+16:].split(b'\0')[0].decode().replace('\\','/').split('/')[-1]
 assert name.lower()=='win32k.pdb';r['pdb_id']=f'{stamp:08X}{age:x}';r['dbg_matches_owned_image']=True
 pdb=fetch(name,r['pdb_id']);r['pdb_available']=pdb is not None
save();print(json.dumps(r,indent=2))
