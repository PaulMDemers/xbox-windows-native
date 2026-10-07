"""Pin candidate NVNet and existing dump-stack modules before crash004."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mods=read(k.parent/'controlled-dump-observe/modules.json')
for n,p in [('trigger.sys',k/'artifacts/trigger.sys'),('nvnetnt5.sys',k.parent/'nvnet-shutdown-resident/artifacts/nvnet-candidate001.sys'),('ndis.sys',k.parent/'controlled-dump-observe/crash002/artifacts/after-ndis.sys')]:
    pe=pefile.PE(str(p));mods[n]=dict(path=str(p.resolve()),sha256=sha(p),preferred_base=pe.OPTIONAL_HEADER.ImageBase,timestamp=pe.FILE_HEADER.TimeDateStamp,image_size=pe.OPTIONAL_HEADER.SizeOfImage)
assert mods['nvnetnt5.sys']['sha256']==read(k/'nvnet-review.json')['candidate001']['sha256']
for n,m in mods.items():assert sha(Path(m['path']))==m['sha256']
(k/'modules.json').write_text(json.dumps(mods,indent=2)+'\n');print('Pinned',len(mods),'actual module binaries')
