"""Create the opt-in provider patch from pinned0093 source, without editing it."""
import difflib,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];root='/home/paul/xbox-windows-native/build/video-reuse-001/source'
def original(name):return subprocess.check_output(['wsl','-d','Ubuntu','--','cat',root+'/'+name]).decode()
tree=subprocess.check_output(['wsl','-d','Ubuntu','--','git','-C',root,'write-tree'],text=True).strip();assert tree=='329a29d61af1620a9fc005b0d8fcfb9e1a937d20'
changes={};pins={}
def change(name,fn):
 old=original(name);new=fn(old);assert old!=new;changes[name]=(old,new);pins[name]=hashlib.sha256(old.encode()).hexdigest()
def replace_once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def boot(s):
 s=replace_once(s,'#include <drivers/xbox/xgpu.h>','#include <drivers/xbox/xgpu.h>\n#ifdef XBOX_NT5_SHARED_FRAMEBUFFER\n#include "xwn_fb.h"\n#endif')
 s=replace_once(s,'    BOOLEAN Result = FALSE;','    BOOLEAN Result = FALSE;\n#ifdef XBOX_NT5_SHARED_FRAMEBUFFER\n    if (FrameBufferStart) { if (SetMode) VidResetDisplay(TRUE); return TRUE; }\n#endif')
 needle='    /* Check whether we have to set the video mode */'
 s=replace_once(s,needle,'''#ifdef XBOX_NT5_SHARED_FRAMEBUFFER
    {
        XWN_FB_VIEW View = {sizeof(View), XWN_FB_VERSION, FrameBufferStart,
            FrameBuffer, NV2A_VIDEO_MEMORY_SIZE, FrameBufferSize,
            FrameBufferWidth, FrameBufferHeight, FrameBufferWidth * BytesPerPixel,
            NV2A_VIDEO_MEMORY_SIZE - BackBufferSize, MmNonCached};
        if (!XwnFbPublish(&View))
        {
            MmUnmapIoSpace((PVOID)FrameBufferStart, NV2A_VIDEO_MEMORY_SIZE);
            FrameBufferStart = 0; BackBuffer = NULL; Result = FALSE;
            goto cleanup;
        }
    }
#endif

'''+needle)
 return s
change('drivers/base/bootvid/i386/xbox/bootvid.c',boot)
def bmake(s):
 s=replace_once(s,'        add_bootvid(xboxbvidnt5 i386/xbox/xboxbvid.cmake\n                    SPEC_FILE bootvidnt5.spec SOURCES nt5.c)', '''        option(XBOX_NT5_SHARED_FRAMEBUFFER "Share permanent UC bootvid mapping" OFF)
        set(XWN_BOOTVID_SPEC bootvidnt5.spec)
        if(XBOX_NT5_SHARED_FRAMEBUFFER)
            set(XWN_BOOTVID_SPEC bootvidshared.spec)
        endif()
        add_bootvid(xboxbvidnt5 i386/xbox/xboxbvid.cmake
                    SPEC_FILE ${XWN_BOOTVID_SPEC} SOURCES nt5.c)
        if(XBOX_NT5_SHARED_FRAMEBUFFER)
            target_sources(xboxbvidnt5 PRIVATE xwn_fb.c)
            target_compile_definitions(xboxbvidnt5 PRIVATE XBOX_NT5_SHARED_FRAMEBUFFER=1)
            target_include_directories(xboxbvidnt5 PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
            generate_import_lib(libxwnfbprovider bootvid.dll bootvidshared.spec "--version=${DLL_EXPORT_VERSION}" "")
        endif()''');return s
change('drivers/base/bootvid/CMakeLists.txt',bmake)
changes['drivers/base/bootvid/bootvidshared.spec']=('',original('drivers/base/bootvid/bootvidnt5.spec')+'@ stdcall XwnFbAcquire(ptr ptr)\n@ stdcall XwnFbRelease(ptr ptr)\n@ stdcall XwnFbReleaseOwner(ptr)\n')
for n in ['xwn_fb.h','xwn_fb.c']:changes['drivers/base/bootvid/'+n]=('',(k/n).read_text())
for n in ['xwn_fb.h','video_shared.c']:changes['win32ss/drivers/miniport/xboxvmp/nt5/'+n]=('',(k/n).read_text())
def mini(s):
 s=replace_once(s,'#include <drivers/xbox/xgpu.h>','''#include <drivers/xbox/xgpu.h>
#ifdef XBOX_NT5_SHARED_FRAMEBUFFER
ULONG NTAPI XwnSharedMap(PVOID, ULONG, ULONG, ULONG, ULONG, PVOID *);
ULONG NTAPI XwnSharedUnmap(PVOID, PVOID);
#endif''')
 s=replace_once(s,'            ULONG Space = VIDEO_MEMORY_SPACE_MEMORY;','#ifndef XBOX_NT5_SHARED_FRAMEBUFFER\n            ULONG Space = VIDEO_MEMORY_SPACE_MEMORY;\n#endif')
 needle='            Status = VideoPortMapMemory(Extension, V->Framebuffer, &Result.VideoRamLength,\n                                        &Space, &Result.VideoRamBase);'
 s=replace_once(s,needle,'''#ifdef XBOX_NT5_SHARED_FRAMEBUFFER
            Status = XwnSharedMap(Extension, V->Offset, V->Mode.VisScreenWidth,
                                  V->Mode.VisScreenHeight, V->Mode.ScreenStride, &Result.VideoRamBase);
#else
'''+needle+'\n#endif')
 needle='        Status = VideoPortUnmapMemory(Extension, ((PVIDEO_MEMORY)Request->InputBuffer)->RequestedVirtualAddress, NULL);'
 return replace_once(s,needle,'#ifdef XBOX_NT5_SHARED_FRAMEBUFFER\n        Status = XwnSharedUnmap(Extension, ((PVIDEO_MEMORY)Request->InputBuffer)->RequestedVirtualAddress);\n#else\n'+needle+'\n#endif')
change('win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c',mini)
change('win32ss/drivers/miniport/xboxvmp/nt5/video_pnp.c',lambda s:replace_once(s,'    if (OriginalUnload) OriginalUnload(Driver);','''    if (OriginalUnload) OriginalUnload(Driver);
#ifdef XBOX_NT5_SHARED_FRAMEBUFFER
    { VOID NTAPI XwnSharedClose(VOID); XwnSharedClose(); }
#endif'''))
change('win32ss/drivers/miniport/xboxvmp/nt5/CMakeLists.txt',lambda s:s+'''
if(XBOX_NT5_SHARED_FRAMEBUFFER)
    if(NOT XBOX_NT5_VIDEO_TRACE OR NOT XBOX_NT5_VIDEO_PNP_DIAGNOSTIC)
        message(FATAL_ERROR "Shared mapping requires owned unload wrapper")
    endif()
    target_compile_definitions(xboxvnt5 PRIVATE XBOX_NT5_SHARED_FRAMEBUFFER=1)
    target_sources(xboxvnt5 PRIVATE video_shared.c)
    add_importlibs(xboxvnt5 xwnfbprovider)
endif()
''')
patch=''.join(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+n if a else '/dev/null',tofile='b/'+n)) for n,(a,b) in changes.items())
dest=k/'0106-shared-uc-framebuffer.patch';assert not dest.exists();dest.write_text(patch,newline='\n')
(k/'patch-review.json').write_text(json.dumps(dict(parent_tree=tree,original_files=pins,patch_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),authored_sources={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['xwn_fb.c','xwn_fb.h','video_shared.c']},source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n');print('Pinned opt-in shared UC patch')
