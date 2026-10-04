from pathlib import Path
import subprocess,json
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f');s=Path('/home/paul/xbox-windows-native/sources/reactos-extended');m=json.loads((k/'patch-check-0069.json').read_text());assert subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip()==m['result_tree']
p=s/'win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c';t=p.read_text().replace('    ULONG Status;\n    VideoPortZeroMemory(&Init', '''    ULONG Status;
#ifdef XBOX_NT5_VIDEO_ENTRY_DIAGNOSTIC
    /* Prove invocation independently of PnP or VideoPort callbacks. */
    VIDEO_FAIL(0, (ULONG_PTR)Context1, (ULONG_PTR)Context2, 0x56454E54);
#endif
    VideoPortZeroMemory(&Init''');assert t!=p.read_text();p.write_text(t)
p=p.parent/'CMakeLists.txt';t=p.read_text();t+='''
option(XBOX_NT5_VIDEO_ENTRY_DIAGNOSTIC "Stop before NT5 video DriverEntry body" OFF)
if(XBOX_NT5_VIDEO_ENTRY_DIAGNOSTIC)
    if(NOT XBOX_NT5_VIDEO_DIAGNOSTIC)
        message(FATAL_ERROR "Video entry diagnostic requires video failure diagnostic")
    endif()
    target_compile_definitions(xboxvnt5 PRIVATE XBOX_NT5_VIDEO_ENTRY_DIAGNOSTIC=1)
endif()
''';p.write_text(t)
patch=k/'0070-nt5-video-entry-diagnostic.patch';patch.write_bytes(subprocess.check_output(['git','-C',str(s),'diff']));subprocess.run(['git','-C',str(s),'add','win32ss/drivers/miniport/xboxvmp/nt5'],check=True);m.update(previous_tree=m['result_tree'],result_tree=subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip());m['patches'].append('outputs/native-windows-physical-f/'+patch.name);(k/'patch-check-0070.json').write_text(json.dumps(m,indent=2)+'\n');print(m['result_tree'])
