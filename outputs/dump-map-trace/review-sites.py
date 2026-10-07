"""Pin successful-query targets from the exact reviewed FATX0103/HAL0102 binaries."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(k.parent/'dump-fsctl-trace/sites.json');r['scope']=__doc__
fatx=read(k/'fatx-review.json')['candidate001'];r['fatx_entry_rva']=int(fatx['resident_functions']['_VfatFileSystemControl']['rva'],16)
r['dump_context_global_rva']=0x780ec
r['dump_context_fields']=dict(mapping_pointer=0x14,mapping_bytes=0x18,requested_bytes=0x58)
r['dependencies']['dump-fsctl-trace/contract-review.json']=sha(k.parent/'dump-fsctl-trace/contract-review.json')
paths={'ntoskrnl.exe':Path(read(k.parent/'dump-fsctl-trace/modules.json')['ntoskrnl.exe']['path']),'hal.dll':k/'artifacts/hal-candidate001.dll','xwnfatx.sys':k/'artifacts/fatx-candidate001.sys'}
mods={}
for name,p in paths.items():
    pe=pefile.PE(str(p));mods[name]=dict(path=str(p.resolve()),sha256=sha(p),preferred_base=pe.OPTIONAL_HEADER.ImageBase,timestamp=pe.FILE_HEADER.TimeDateStamp,image_size=pe.OPTIONAL_HEADER.SizeOfImage)
assert mods['ntoskrnl.exe']['sha256']==r['kernel_sha256']
assert mods['hal.dll']['sha256']==read(k/'hal-review.json')['candidate001']['sha256']
assert mods['xwnfatx.sys']['sha256']==fatx['sha256']
for name,obj in [('sites.json',r),('modules.json',mods)]:
    p=k/name;assert not p.exists();p.write_text(json.dumps(obj,indent=2)+'\n')
print('Pinned candidate modules and prior reviewed kernel boundaries')
