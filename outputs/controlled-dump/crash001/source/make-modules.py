import json,hashlib,sys
from pathlib import Path
k=Path(__file__).resolve().parent;sys.path.insert(0,str(k.parents[1]/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mods=read(k.parent/'dump-map-trace/modules.json')
for n,row in read(k.parent/'dump-usage-trace/modules.json').items():
    if n not in mods:mods[n]=row
p=k/'artifacts/trigger.sys';pe=pefile.PE(str(p));mods['trigger.sys']=dict(path=str(p.resolve()),sha256=sha(p),preferred_base=pe.OPTIONAL_HEADER.ImageBase,timestamp=pe.FILE_HEADER.TimeDateStamp,image_size=pe.OPTIONAL_HEADER.SizeOfImage)
(k/'modules.json').write_text(json.dumps(mods,indent=2)+'\n')
