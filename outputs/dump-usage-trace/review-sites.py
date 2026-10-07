"""Pin kernel dispatch/completion boundaries, layouts and cold storage image identities."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
parser=k.parent/'native-windows-nt5-interrupts/read-pdb-layouts.py';ns={'__file__':str(parser)};exec(parser.read_text().split('selected={}')[0],ns)
pdb=ws/'work/symbols/ntoskrnl-2195-7376.pdb';public=k.parent/'native-windows-nt5-kernel/kernel-publics.json';pub=read(public);assert sha(pdb)==pub['pdb_sha256']
layouts={}
for name in ['_IRP','_IO_STACK_LOCATION','_IO_STATUS_BLOCK','_LDR_DATA_TABLE_ENTRY','_DEVICE_OBJECT','_DRIVER_OBJECT','_EPROCESS']:
 v=ns['structs'][name].copy();v['fields']=ns['fields'](v['field_list']);layouts[name]=v
layout=dict(pdb_sha256=sha(pdb),parser_sha256=sha(parser),structures=layouts,irp_current_stack_location_offset=96,offset_basis='Pinned IopfCallDriver reads [esi+0x60], subtracts the PDB IO_STACK_LOCATION size36 before dispatch.')
mods={};kernel=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe');mods['ntoskrnl.exe']=dict(path=str(kernel),sha256=sha(kernel))
f=k.parent/'fatx-directory-order/artifacts/xwnfatx.sys';mods['xwnfatx.sys']=dict(path=str(f.resolve()),sha256=sha(f))
previous=k.parent/'dump-config-trace/serial005';storage=read(previous/'storage-binaries.json')
for row in storage['files']:
 p=previous/'artifacts'/('before-'+row['name']);assert sha(p)==row['sha256'];mods[row['name']]=dict(path=str(p.resolve()),sha256=sha(p))
for row in mods.values():
 p=pefile.PE(row['path']);row.update(preferred_base=p.OPTIONAL_HEADER.ImageBase,timestamp=p.FILE_HEADER.TimeDateStamp,image_size=p.OPTIONAL_HEADER.SizeOfImage)
pe=pefile.PE(str(kernel));K=read(k.parent/'fatx-paging-buffer/sites.json')['kernel_base_expected'];sites=[]
for name,rva,n,initial in [('usage_call',0x21c2f,5,True),('usage_return',0x21c34,7,True),('dispatch',pub['symbols']['@IopfCallDriver@8']['rva'],15,False),('complete',pub['symbols']['@IopfCompleteRequest@8']['rva'],13,False),('free',pub['symbols']['_IopFreeIrp@4']['rva'],15,False)]:
 raw=pe.get_data(rva,n);relocs=[e.rva-rva for block in pe.DIRECTORY_ENTRY_BASERELOC for e in block.entries if e.type==3 and rva<=e.rva<rva+n];assert all(o+4<=n for o in relocs)
 data=bytearray(raw)
 for o in relocs:struct.pack_into('<I',data,o,(struct.unpack_from('<I',data,o)[0]+K-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 sites.append(dict(name=name,rva=rva,address=K+rva,raw=raw.hex(),relocated=data.hex(),relocations=relocs,initial=initial))
deps=['native-windows-nt5-kernel/kernel-publics.json','shutdown-popup-workload/site-review.json','native-windows-nt5-kernel/trace-entry.py']
r=dict(kernel_base_expected=K,kernel_sha256=sha(kernel),kernel_timestamp=pe.FILE_HEADER.TimeDateStamp,sites=sites,loaded_module_list_rva=pub['symbols']['_PsLoadedModuleList']['rva'],dispatch_pointer_rva=0x73a70,completion_pointer_rva=0x73a74,free_pointer_rva=0x73a7c,dependencies={n:sha(k.parent/n) for n in deps})
for name,data in [('sites.json',r),('layouts.json',layout),('modules.json',mods)]:
 p=k/name;assert not p.exists();p.write_text(json.dumps(data,indent=2)+'\n')
print('Pinned5 kernel boundaries,7 exact PDB layouts and8 cold module files')
