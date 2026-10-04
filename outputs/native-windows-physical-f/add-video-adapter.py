from pathlib import Path
import json,subprocess
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f');s=Path('/home/paul/xbox-windows-native/sources/reactos-extended');m=json.loads((k/'patch-check-0070.json').read_text());assert subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip()==m['result_tree']
p=s/'win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c';t=p.read_text();needle='    V->ApertureLength = Ranges[1].RangeLength;';assert t.count(needle)==1;t=t.replace(needle,needle+'''
#ifdef XBOX_NT5_VIDEO_ADAPTER_DIAGNOSTIC
    /* Preserve Windows-assigned resources before hardware initialization. */
    VIDEO_FAIL(8, V->ControlPhysical.LowPart,
               V->FramebufferAperture.LowPart, V->ApertureLength);
#endif''');p.write_text(t)
p=p.parent/'CMakeLists.txt';t=p.read_text();t+='''
option(XBOX_NT5_VIDEO_ADAPTER_DIAGNOSTIC "Stop after NT5 video resource discovery" OFF)
if(XBOX_NT5_VIDEO_ADAPTER_DIAGNOSTIC)
    if(NOT XBOX_NT5_VIDEO_DIAGNOSTIC OR XBOX_NT5_VIDEO_ENTRY_DIAGNOSTIC)
        message(FATAL_ERROR "Adapter diagnostic requires failure checks and entry checkpoint OFF")
    endif()
    target_compile_definitions(xboxvnt5 PRIVATE XBOX_NT5_VIDEO_ADAPTER_DIAGNOSTIC=1)
endif()
''';p.write_text(t)
patch=k/'0071-nt5-video-adapter-diagnostic.patch';patch.write_bytes(subprocess.check_output(['git','-C',str(s),'diff']));subprocess.run(['git','-C',str(s),'add','win32ss/drivers/miniport/xboxvmp/nt5'],check=True);m.update(previous_tree=m['result_tree'],result_tree=subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip());m['patches'].append('outputs/native-windows-physical-f/'+patch.name);(k/'patch-check-0071.json').write_text(json.dumps(m,indent=2)+'\n');print(m['result_tree'])
