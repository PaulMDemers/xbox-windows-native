"""Compile FATX structure offsets with the exact candidate0099 build flags; no driver rebuild."""
import hashlib,json,shlex,struct,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
root=Path('/home/paul/xbox-windows-native/build/fatx-cleanup-order-001');build=root/'build-fatx'
sdk=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
binary=build/'drivers/filesystems/vfatfs/vfatfs.sys'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(binary)=='c7e029096a70e36a300a2439dfdb0216d070710700ac89e282d0b59a03542e79'
subprocess.run(['git','-C',str(root/'source'),'diff','--quiet'],check=True)
assert subprocess.check_output(['git','-C',str(root/'source'),'write-tree'],text=True).strip()=='1c92d31299f370bbbca346be54c3a8d23012296f'
lines=subprocess.check_output([str(sdk/'bin/ninja'),'-t','commands','drivers/filesystems/vfatfs/CMakeFiles/vfatfs.dir/flush.c.obj'],cwd=build,text=True).splitlines()
commands=[shlex.split(s) for s in lines if s.startswith(str(sdk/'i386/bin/i686-w64-mingw32-gcc')+' ') and s.endswith('/vfatfs/flush.c')]
assert len(commands)==1
cmd=commands[0];art=k/'artifacts';art.mkdir(exist_ok=True)
fields={'global_volume_list':'FIELD_OFFSET(VFAT_GLOBAL_DATA, VolumeListHead)',
 'vcb_volume_link':'FIELD_OFFSET(DEVICE_EXTENSION, VolumeListEntry)',
 'vcb_dir_resource':'FIELD_OFFSET(DEVICE_EXTENSION, DirResource)',
 'vcb_fat_resource':'FIELD_OFFSET(DEVICE_EXTENSION, FatResource)',
 'vcb_fcb_list':'FIELD_OFFSET(DEVICE_EXTENSION, FcbListHead)',
 'fcb_link':'FIELD_OFFSET(VFATFCB, FcbListEntry)',
 'fcb_main_resource':'FIELD_OFFSET(VFATFCB, MainResource)',
 'fcb_paging_resource':'FIELD_OFFSET(VFATFCB, PagingIoResource)',
 'fcb_path':'FIELD_OFFSET(VFATFCB, PathNameU)',
 'fcb_flags':'FIELD_OFFSET(VFATFCB, Flags)',
 'fcb_refcount':'FIELD_OFFSET(VFATFCB, RefCount)',
 'resource_size':'sizeof(ERESOURCE)'}
source=art/'layouts.c';source.write_text('#include "vfat.h"\nconst ULONG XwnLayouts[]={'+','.join(fields.values())+'};\n')
for opt,name in [('-o','layouts.o'),('-MF','layouts.d'),('-MT','layouts.o')]:cmd[cmd.index(opt)+1]=str(art/name)
cmd[-1]=str(source)
subprocess.run(cmd,cwd=build,check=True)
subprocess.run([str(sdk/'i386/bin/i686-w64-mingw32-objcopy'),'-O','binary','-j','.rdata',str(art/'layouts.o'),str(art/'layouts.bin')],check=True)
raw=(art/'layouts.bin').read_bytes();size=len(fields)*4
assert size<=len(raw)<=size+31 and not any(raw[size:]), 'Unexpected data beyond section alignment padding'
object_symbols=subprocess.check_output([str(sdk/'i386/bin/i686-w64-mingw32-nm'),'-n',str(art/'layouts.o')],text=True)
assert [l for l in object_symbols.splitlines() if ' R ' in l]==['00000000 R _XwnLayouts']
values=dict(zip(fields,struct.unpack('<'+'I'*len(fields),raw[:size])))
assert values['resource_size']==56 and values['vcb_dir_resource']==0
nm=subprocess.check_output([str(sdk/'i386/bin/i686-w64-mingw32-nm'),'-n',str(binary)],text=True,stderr=subprocess.DEVNULL)
syms={p[2]:int(p[0],16)-0x10000 for l in nm.splitlines() if len(p:=l.split())==3 and p[1] in ['T','t','B','b','D','d']}
r=dict(scope=__doc__,driver_sha256=sha(binary),header_sha256=sha(root/'source/drivers/filesystems/vfatfs/vfat.h'),
       source_sha256=sha(source),compiler_sha256=sha(Path(cmd[0])),command=cmd,offsets=values,
       global_pointer_rva=syms['_VfatGlobalData'],symbols={n:syms[n] for n in ['_VfatClose','_VfatCleanup','_VfatFlushFile','_VfatFlushVolume']})
(k/'fatx-layouts.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(values,indent=2))
