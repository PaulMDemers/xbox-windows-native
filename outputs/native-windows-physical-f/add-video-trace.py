from pathlib import Path
import json, subprocess
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f')
s=Path('/home/paul/xbox-windows-native/sources/reactos-extended')
m=json.loads((k/'patch-check-0072.json').read_text())
assert subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip()==m['result_tree']
d=s/'win32ss/drivers/miniport/xboxvmp/nt5'
p=d/'video_pnp.c';t=p.read_text()
t=t.replace('static PDRIVER_DISPATCH OriginalPnp;', '''static PDRIVER_DISPATCH OriginalPnp;
#ifdef XBOX_NT5_VIDEO_TRACE
VOID NTAPI XwnVideoTraceInit(VOID);
VOID NTAPI XwnVideoTrace(ULONG, ULONG, ULONG, ULONG);
VOID NTAPI XwnVideoTraceClose(VOID);
VOID NTAPI XwnVideoTracePci(VOID);
static PDRIVER_UNLOAD OriginalUnload;
static VOID NTAPI XwnVideoUnload(PDRIVER_OBJECT Driver)
{
    XwnVideoTrace(6, 0, 0, 0);
    XwnVideoTraceClose();
    if (OriginalUnload) OriginalUnload(Driver);
}
#define TRACE(e,a,b,c) XwnVideoTrace(e,(ULONG)(a),(ULONG)(b),(ULONG)(c))
#else
#define TRACE(e,a,b,c) ((void)0)
#endif''')
t=t.replace('    UCHAR Minor = Stack->MinorFunction;', '''    UCHAR Minor = Stack->MinorFunction;
    NTSTATUS Status;
    TRACE(4, Minor, Device, 0);''')
t=t.replace('        KeBugCheckEx(0xE0580001, 9, Raw ? Raw->Count : 0,\n                     Translated ? Translated->Count : 0, 0x53545254);', '''#ifdef XBOX_NT5_VIDEO_TRACE
        TRACE(7, Raw ? Raw->Count : 0, Translated ? Translated->Count : 0, 0);
#else
        KeBugCheckEx(0xE0580001, 9, Raw ? Raw->Count : 0,
                     Translated ? Translated->Count : 0, 0x53545254);
#endif''')
t=t.replace('    return OriginalPnp(Device, Irp);', '''    Status = OriginalPnp(Device, Irp);
    TRACE(5, Minor, Status, 0);
    return Status;''')
t=t.replace('    NTSTATUS Status = OriginalAddDevice(Driver, PhysicalDevice);', '''    NTSTATUS Status;
    TRACE(2, PhysicalDevice, 0, 0);
    Status = OriginalAddDevice(Driver, PhysicalDevice);
    TRACE(3, Status, PhysicalDevice, 0);''')
t=t.replace('    OriginalAddDevice = Driver->DriverExtension ?', '''#ifdef XBOX_NT5_VIDEO_TRACE
    XwnVideoTraceInit();
    OriginalUnload = Driver->DriverUnload;
    Driver->DriverUnload = XwnVideoUnload;
#endif
    OriginalAddDevice = Driver->DriverExtension ?''')
t=t.replace('    if (!OriginalAddDevice || !OriginalPnp)', '    TRACE(1, OriginalAddDevice, OriginalPnp, 0);\n#ifdef XBOX_NT5_VIDEO_TRACE\n    XwnVideoTracePci();\n#endif\n    if (!OriginalAddDevice || !OriginalPnp)')
p.write_text(t);(d/'video_trace.c').write_bytes((k/'video-trace.c').read_bytes())
p=d/'CMakeLists.txt';p.write_text(p.read_text()+'''
option(XBOX_NT5_VIDEO_TRACE "Trace NT5 video PnP to an existing seeded file" OFF)
if(XBOX_NT5_VIDEO_TRACE)
    if(NOT XBOX_NT5_VIDEO_PNP_DIAGNOSTIC)
        message(FATAL_ERROR "Video trace requires PnP diagnostic wrappers")
    endif()
    target_compile_definitions(xboxvnt5 PRIVATE XBOX_NT5_VIDEO_TRACE=1)
    target_sources(xboxvnt5 PRIVATE video_trace.c)
    add_importlibs(xboxvnt5 hal)
endif()
''')
subprocess.run(['git','-C',str(s),'add','-N',str(d/'video_trace.c')],check=True)
patch=k/'0073-nt5-video-persistent-trace.patch';patch.write_bytes(subprocess.check_output(['git','-C',str(s),'diff']))
subprocess.run(['git','-C',str(s),'add',str(d)],check=True)
m.update(previous_tree=m['result_tree'],result_tree=subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip(),clean_index_replay_verified=False)
m['patches'].append('outputs/native-windows-physical-f/'+patch.name)
(k/'patch-check-0073.json').write_text(json.dumps(m,indent=2)+'\n');print(m['result_tree'])
