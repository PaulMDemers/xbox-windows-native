"""Compile write-path offsets using exact candidate0101 flags; no driver change or runtime claim."""
import hashlib,json,shlex,struct,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
root=Path('/home/paul/xbox-windows-native/build/fatx-directory-order-001');build=root/'build-fatx'
sdk=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
binary=build/'drivers/filesystems/vfatfs/vfatfs.sys'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(binary)=='ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9'
subprocess.run(['git','-C',str(root/'source'),'diff','--quiet'],check=True)
assert subprocess.check_output(['git','-C',str(root/'source'),'write-tree'],text=True).strip()=='8e12297ca0ed53383fe9aaebef152c26aee5a43b'
lines=subprocess.check_output([str(sdk/'bin/ninja'),'-t','commands','drivers/filesystems/vfatfs/CMakeFiles/vfatfs.dir/flush.c.obj'],cwd=build,text=True).splitlines()
commands=[shlex.split(s) for s in lines if s.startswith(str(sdk/'i386/bin/i686-w64-mingw32-gcc')+' ') and s.endswith('/vfatfs/flush.c')]
assert len(commands)==1
cmd=commands[0];art=k/'artifacts';art.mkdir(exist_ok=True)
fields={'context_irp': 'FIELD_OFFSET(VFAT_IRP_CONTEXT, Irp)', 'context_stack': 'FIELD_OFFSET(VFAT_IRP_CONTEXT, Stack)', 'context_file': 'FIELD_OFFSET(VFAT_IRP_CONTEXT, FileObject)', 'file_fcb': 'FIELD_OFFSET(FILE_OBJECT, FsContext)', 'file_name': 'FIELD_OFFSET(FILE_OBJECT, FileName)', 'file_position': 'FIELD_OFFSET(FILE_OBJECT, CurrentByteOffset)', 'file_flags': 'FIELD_OFFSET(FILE_OBJECT, Flags)', 'fcb_path': 'FIELD_OFFSET(VFATFCB, PathNameU)', 'fcb_size': 'FIELD_OFFSET(VFATFCB, RFCB.FileSize)', 'irp_mdl': 'FIELD_OFFSET(IRP, MdlAddress)', 'irp_flags': 'FIELD_OFFSET(IRP, Flags)', 'irp_user_buffer': 'FIELD_OFFSET(IRP, UserBuffer)', 'irp_system_buffer': 'FIELD_OFFSET(IRP, AssociatedIrp.SystemBuffer)', 'irp_status': 'FIELD_OFFSET(IRP, IoStatus)', 'stack_length': 'FIELD_OFFSET(IO_STACK_LOCATION, Parameters.Write.Length)', 'stack_offset': 'FIELD_OFFSET(IO_STACK_LOCATION, Parameters.Write.ByteOffset)', 'mdl_mapped': 'FIELD_OFFSET(MDL, MappedSystemVa)', 'mdl_start': 'FIELD_OFFSET(MDL, StartVa)', 'mdl_offset': 'FIELD_OFFSET(MDL, ByteOffset)', 'mdl_flags': 'FIELD_OFFSET(MDL, MdlFlags)', 'file_size': 'sizeof(FILE_OBJECT)', 'irp_size': 'sizeof(IRP)'}
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
assert values['file_fcb']==12 and values['file_name']==48 and values['stack_offset']==12
# sizeof(FILE_OBJECT) is128 in these pinned headers; do not infer the native NT5 tail from it.
nm=subprocess.check_output([str(sdk/'i386/bin/i686-w64-mingw32-nm'),'-n',str(binary)],text=True,stderr=subprocess.DEVNULL)
syms={p[2]:int(p[0],16)-0x10000 for l in nm.splitlines() if len(p:=l.split())==3 and p[1] in ['T','t','B','b','D','d']}
r=dict(scope=__doc__,driver_sha256=sha(binary),header_sha256=sha(root/'source/drivers/filesystems/vfatfs/vfat.h'),
       limits='Compiler-derived driver field offsets; FILE_OBJECT size128 describes these headers, not a verified native NT5 object tail.', source_sha256=sha(source),compiler_sha256=sha(Path(cmd[0])),command=cmd,offsets=values,
       global_pointer_rva=syms['_VfatGlobalData'],symbols={n:syms[n] for n in ['_VfatWrite','_VfatWriteDiskPartial','_VfatGetUserBuffer']})
(k/'write-layouts.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(values,indent=2))
