"""Fetch exact timestamp/size matched PCI symbols from Microsoft's server."""
import pathlib,struct,sys,urllib.request,urllib.error,json,hashlib,subprocess
r=pathlib.Path(__file__).resolve().parents[2];out=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
file=out/'artifacts/inventory001/sysaudio.sys'
symbols=out/'artifacts/sysaudio-symbols001';symbols.mkdir(exist_ok=False)
pe=pefile.PE(str(file));key=f'{pe.FILE_HEADER.TimeDateStamp:08X}{pe.OPTIONAL_HEADER.SizeOfImage:x}'
url=f'https://msdl.microsoft.com/download/symbols/sysaudio.dbg/{key}/sysaudio.dbg'
try:
 with urllib.request.urlopen(url,timeout=20) as response:data=response.read(20*1024*1024)
except urllib.error.HTTPError as e:
 if e.code!=404:raise
 url=url[:-1]+'_'
 with urllib.request.urlopen(url,timeout=20) as response:compressed=response.read(20*1024*1024)
 archive=symbols/'sysaudio.db_';archive.write_bytes(compressed)
 winpath=str(archive).replace('\\','/');linuxpath='/mnt/'+winpath[0].lower()+winpath[2:]
 subprocess.run(['wsl','-d','Ubuntu','--','/home/paul/xbox-windows-native/toolchains/7zip/root/usr/lib/7zip/7z','x','-y','-o'+linuxpath.rsplit('/',1)[0]+'/sysaudio-expanded',linuxpath],check=True,stdout=subprocess.DEVNULL)
 data=(archive.parent/'sysaudio-expanded/sysaudio.dbg').read_bytes()
assert data[:2]==b'DI'
head=struct.unpack_from('<HHHH10I',data)
assert head[4]==pe.FILE_HEADER.TimeDateStamp and head[7]==pe.OPTIONAL_HEADER.SizeOfImage
(symbols/'sysaudio.dbg').write_bytes(data)
i=data.index(b'NB10');_,_,stamp,age=struct.unpack_from('<4sIII',data,i)
name=data[i+16:].split(b'\0',1)[0].decode().replace('\\','/').split('/')[-1]
assert name=='sysaudio.pdb'
key=f'{stamp:08X}{age:x}';pdburl=f'https://msdl.microsoft.com/download/symbols/{name}/{key}/{name}'
with urllib.request.urlopen(pdburl,timeout=20) as response:pdb=response.read(100*1024*1024)
target=symbols/'sysaudio.pdb';target.write_bytes(pdb)
record={'dbg_url':url,'pdb_url':pdburl,'dbg_matches_image_timestamp_and_size':True,'pdb_id':key,'sha256':hashlib.sha256(pdb).hexdigest()}
(out/'sysaudio-symbols.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
