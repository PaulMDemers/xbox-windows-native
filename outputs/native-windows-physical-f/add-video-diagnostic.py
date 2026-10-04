from pathlib import Path
import json,subprocess
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f');s=Path('/home/paul/xbox-windows-native/sources/reactos-extended');prev=json.loads((k/'patch-check-0068.json').read_text());assert subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip()==prev['result_tree']
p=s/'win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c';t=p.read_text();t=t.replace('#include <drivers/xbox/xgpu.h>', '''#include <drivers/xbox/xgpu.h>

#ifdef XBOX_NT5_VIDEO_DIAGNOSTIC
/* Deliberate diagnostic stop: preserve the first failing native video stage.
 * Stage 1: VideoPortInitialize; 2: PCI ranges; 3: range sizes; 4: register map;
 * 5: firmware geometry; 6: aperture bounds; 7: framebuffer map.
 * No GPU mode changes or disk writes are introduced by this diagnostic. */
NTSYSAPI VOID NTAPI KeBugCheckEx(ULONG, ULONG_PTR, ULONG_PTR, ULONG_PTR, ULONG_PTR);
#define VIDEO_FAIL(stage, a, b, c) KeBugCheckEx(0xE0580001, stage, a, b, c)
#else
#define VIDEO_FAIL(stage, a, b, c) ((void)0)
#endif''')
t=t.replace('if (Status != NO_ERROR) return Status;', 'if (Status != NO_ERROR) { VIDEO_FAIL(2, Status, Config->SystemIoBusNumber, Slot); return Status; }',1)
t=t.replace('Ranges[1].RangeLength < NV2A_VIDEO_MEMORY_SIZE) return ERROR_DEV_NOT_EXIST;', 'Ranges[1].RangeLength < NV2A_VIDEO_MEMORY_SIZE)\n    { VIDEO_FAIL(3, Ranges[0].RangeLength, Ranges[1].RangeLength,\n                 Ranges[0].RangeInIoSpace | (Ranges[1].RangeInIoSpace << 8));\n      return ERROR_DEV_NOT_EXIST; }')
t=t.replace('if (!V->Control) return FALSE;', 'if (!V->Control) { VIDEO_FAIL(4, V->ControlPhysical.LowPart, V->ControlPhysical.HighPart, 0); return FALSE; }')
t=t.replace('        VideoPortFreeDeviceBase(Extension, V->Control);V->Control = NULL;return FALSE;', '''        if (Width < 320 || Width > 1920 || Height < 200 || Height > 1080 || Bytes != 4 ||
            Pitch < Width * Bytes || Pitch > 8192 || Height > NV2A_VIDEO_MEMORY_SIZE / Pitch)
            VIDEO_FAIL(5, Width, Height, (Pitch << 8) | Format);
        else
            VIDEO_FAIL(6, V->Offset, V->ApertureLength, V->FramebufferAperture.LowPart);
        VideoPortFreeDeviceBase(Extension, V->Control);V->Control = NULL;return FALSE;''')
t=t.replace('if (Status != NO_ERROR) break;', 'if (Status != NO_ERROR) { VIDEO_FAIL(7, Status, V->Framebuffer.LowPart, Result.VideoRamLength); break; }')
t=t.replace('    VIDEO_HW_INITIALIZATION_DATA Init;', '    VIDEO_HW_INITIALIZATION_DATA Init;\n    ULONG Status;')
t=t.replace('    return VideoPortInitialize(Context1, Context2, &Init, NULL);', '''    Status = VideoPortInitialize(Context1, Context2, &Init, NULL);
    if (Status != NO_ERROR) VIDEO_FAIL(1, Status, 0, 0);
    return Status;''');p.write_text(t)
p=p.parent/'CMakeLists.txt';t=p.read_text();t += '''
option(XBOX_NT5_VIDEO_DIAGNOSTIC "Stop at first failing NT5 video initialization stage" OFF)
if(XBOX_NT5_VIDEO_DIAGNOSTIC)
    target_compile_definitions(xboxvnt5 PRIVATE XBOX_NT5_VIDEO_DIAGNOSTIC=1)
    add_importlibs(xboxvnt5 ntoskrnl)
endif()
''';p.write_text(t)
patch=k/'0069-nt5-video-failure-diagnostic.patch';patch.write_bytes(subprocess.check_output(['git','-C',str(s),'diff']))
subprocess.run(['git','-C',str(s),'add','win32ss/drivers/miniport/xboxvmp/nt5'],check=True)
prev.update(previous_tree=prev['result_tree'],result_tree=subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip());prev['patches'].append('outputs/native-windows-physical-f/'+patch.name);(k/'patch-check-0069.json').write_text(json.dumps(prev,indent=2)+'\n');print(prev['result_tree'])
