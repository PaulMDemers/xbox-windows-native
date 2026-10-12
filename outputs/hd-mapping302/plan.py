"""Pin owned kernel PDB, current native binaries and COFF static data symbols."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=ws/'outputs/native-windows-nt5/read-pdb-layouts.py';ns={'__file__':str(p)}
exec(p.read_text().split('selected={}')[0],ns)
structures={}
for n in ['_MMPFN','_MMPFNENTRY','_LDR_DATA_TABLE_ENTRY']:
    d=dict(ns['structs'][n]);d['fields']=ns['fields'](d['field_list']);structures[n]=d
flags=ns['types'][structures['_MMPFNENTRY']['fields']['PageLocation']['type_index']]
leaf,typ,length,position=struct.unpack_from('<HIBB',flags);assert leaf==0x1205 and length==3
pub=json.loads((ws/'outputs/native-windows-nt5-kernel/kernel-publics.json').read_text())
assert pub['pdb_sha256']==sha(ws/'work/symbols/ntoskrnl-2195-7376.pdb')
paths={'ntoskrnl.exe':Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe'),
       'bootvid.dll':Path('E:/xwn300/build001/candidate001/xboxbvid.dll'),
       'xboxvnt5.sys':Path('E:/xwn300/build001/candidate001/xboxvnt5.sys')}
mods={}
for n,p in paths.items():
    pe=pefile.PE(str(p));raw=p.read_bytes();syms={};count=pe.FILE_HEADER.NumberOfSymbols;start=pe.FILE_HEADER.PointerToSymbolTable
    strings=start+18*count;i=0
    while i<count:
        at=start+18*i;name8,value,section,ty,cls,aux=struct.unpack_from('<8sIhHBB',raw,at)
        if name8[:4]==b'\0'*4:
            off=struct.unpack_from('<I',name8,4)[0];a=strings+off;name=raw[a:raw.index(b'\0',a)].decode()
        else:name=name8.split(b'\0')[0].decode()
        if 0<section<=len(pe.sections):syms[name]=pe.sections[section-1].VirtualAddress+value
        i+=1+aux
    exports={v.name.decode():v.address for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
    mods[n]=dict(path=str(p),sha256=sha(p),timestamp=pe.FILE_HEADER.TimeDateStamp,
                 image_size=pe.OPTIONAL_HEADER.SizeOfImage,preferred_base=pe.OPTIONAL_HEADER.ImageBase,
                 symbols={s:syms[s] for s in ['_Published','_Ready','_Owner','_References','_FrameBufferStart'] if s in syms},exports=exports)
assert mods['ntoskrnl.exe']['sha256']=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
assert set(mods['bootvid.dll']['symbols'])=={'_Published','_Ready','_Owner','_References','_FrameBufferStart'}
r=dict(modules=mods,structures=structures,pfn_page_location=dict(length=length,position=position),
       public_symbols={n:pub['symbols'][n]['rva'] for n in ['_KiTrap00','_KiTrap0E','_PsLoadedModuleList','_MmPhysicalMemoryBlock','_MmPfnDatabase']},
       pdb_sha256=pub['pdb_sha256'],parser_sha256=sha(ws/'outputs/native-windows-nt5/read-pdb-layouts.py'),
       capture_after_launch_seconds=75,physical_bytes=67108864,scope='Offline snapshot interpretation; no assumed runtime bases')
dest=k/'plan.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print('Plan pinned')
