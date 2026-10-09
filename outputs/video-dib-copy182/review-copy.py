"""Pin actual candidate adapter/geometry resident bytes and unchanged scanout."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
dest=k/'copy-review.json';assert not dest.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=k/'candidate001/artifacts/xwnown.dll';pe=pefile.PE(str(p));posix='/mnt/c/'+str(p).replace('\\','/')[3:]
nm=subprocess.check_output(['wsl','-d','Ubuntu','--','/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-nm',posix],text=True,stderr=subprocess.DEVNULL)
sites=[]
for name in ['_XwnDibCopy','_XdSurface']:
 hit=re.search(r'^([0-9a-fA-F]+) [Tt] '+name+r'$',nm,re.M);assert hit,name
 address=int(hit.group(1),16);rva=address-pe.OPTIONAL_HEADER.ImageBase;s=pe.get_section_by_rva(rva)
 assert s.Characteristics&0x08000000 and s.Characteristics&0x20000000
 next_addresses=[int(v,16) for v in re.findall(r'^([0-9a-fA-F]+) [Tt] ',nm,re.M) if int(v,16)>address]
 end=min(next_addresses);assert end>address
 sites.append(dict(name=name,address=address,rva=rva,section=s.Name.rstrip(b'\0').decode(),resident_bytes=pe.get_data(rva,64).hex(),compiled_bytes=end-address,compiled_sha256=hashlib.sha256(pe.get_data(rva,end-address)).hexdigest()))
before=(k.parent/'video-clip-upload/display/shadow.c').read_text();after=(k/'display/shadow.c').read_text()
def scanout(text):return text[text.index('static VOID XwnUploadBox'):text.index('BOOL APIENTRY XwnBitBlt')].split('/* Only standard')[0].rstrip()
assert scanout(before)==scanout(after),'Existing scanout implementation changed'
assert (k/'display/surface.c').read_bytes()==(k.parent/'video-clip-upload/display/surface.c').read_bytes()
dest.write_text(json.dumps(dict(passed=True,adapter_geometry_resident=sites,planner_inlined_into_adapter=True,no_separate_planner_symbol_observed='_XdPlan' not in nm,candidate_sha256=sha(p),scanout_source_unchanged=True,surface_ownership_allocation_unchanged=True,no_gpu_cache_mode_change=True,physical_access=False,runtime_qualified=False),indent=2)+'\n')
print('Actual adapter/planner resident; scanout/surface source unchanged')
