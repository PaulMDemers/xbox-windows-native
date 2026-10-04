from pathlib import Path
import json, subprocess
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f')
s=Path('/home/paul/xbox-windows-native/sources/reactos-extended')
m=json.loads((k/'patch-check-0071.json').read_text())
assert subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip()==m['result_tree']
d=s/'win32ss/drivers/miniport/xboxvmp/nt5'
p=d/'xboxvnt5.c';t=p.read_text();needle='    if (Status != NO_ERROR) VIDEO_FAIL(1, Status, 0, 0);'
assert t.count(needle)==1
t=t.replace(needle,needle+'''
#ifdef XBOX_NT5_VIDEO_PNP_DIAGNOSTIC
    if (Status == NO_ERROR) XwnVideoArmPnp(Context1);
#endif''')
t=t.replace('ULONG NTAPI DriverEntry(PVOID Context1, PVOID Context2)', '''#ifdef XBOX_NT5_VIDEO_PNP_DIAGNOSTIC
VOID NTAPI XwnVideoArmPnp(PVOID Driver);
#endif
ULONG NTAPI DriverEntry(PVOID Context1, PVOID Context2)''')
p.write_text(t)
(d/'video_pnp.c').write_bytes((k/'video-pnp-diagnostic.c').read_bytes())
p=d/'CMakeLists.txt';p.write_text(p.read_text()+'''
option(XBOX_NT5_VIDEO_PNP_DIAGNOSTIC "Stop before NT5 video PnP start" OFF)
if(XBOX_NT5_VIDEO_PNP_DIAGNOSTIC)
    if(NOT XBOX_NT5_VIDEO_DIAGNOSTIC OR XBOX_NT5_VIDEO_ENTRY_DIAGNOSTIC OR XBOX_NT5_VIDEO_ADAPTER_DIAGNOSTIC)
        message(FATAL_ERROR "PnP diagnostic requires failure checks and other checkpoints OFF")
    endif()
    target_compile_definitions(xboxvnt5 PRIVATE XBOX_NT5_VIDEO_PNP_DIAGNOSTIC=1)
    target_sources(xboxvnt5 PRIVATE video_pnp.c)
endif()
''')
subprocess.run(['git','-C',str(s),'add','-N',str(d/'video_pnp.c')],check=True)
patch=k/'0072-nt5-video-pnp-diagnostic.patch'
patch.write_bytes(subprocess.check_output(['git','-C',str(s),'diff']))
subprocess.run(['git','-C',str(s),'add',str(d)],check=True)
m.update(previous_tree=m['result_tree'],result_tree=subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip())
m['patches'].append('outputs/native-windows-physical-f/'+patch.name)
(k/'patch-check-0072.json').write_text(json.dumps(m,indent=2)+'\n');print(m['result_tree'])
