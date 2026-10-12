"""Fresh source replay and opt-in reservation patch; never edits prior checkouts."""
import difflib, hashlib, json, os, pathlib, subprocess, sys
K=pathlib.Path(__file__).resolve().parent; W=K.parents[1]
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
sys.path.insert(0,str(W/'tools'));from build_space import require_space
out=pathlib.Path('/home/paul/xbox-windows-native/build/hd-reservation300-build001')
assert not out.exists();space=require_space(out);out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
src=out/'source';crom=out/'cromwell';r=dict(space=space,status='preparing',changes={},commands=[])
def run(args):
 r['commands'].append(list(map(str,args)));subprocess.run(args,check=True,stdout=log,stderr=log)
def change(root,name,old,new):
 p=root/name;before=p.read_text();assert before.count(old)==1,(name,old[:70]);p.write_text(before.replace(old,new))
def tree(root):return subprocess.check_output(['git','-C',str(root),'write-tree'],text=True).strip()
try:
 with (out/'prepare.log').open('w') as log:
  lock=read(W/'outputs/video-trace-reuse/inputs.json')
  for n,h in lock['patch_sha256'].items():assert sha(W/n)==h,n
  shared=read(W/'outputs/video-shared-framebuffer/patch-review.json')
  patch=W/'outputs/video-shared-framebuffer/0106-shared-uc-framebuffer.patch'
  assert sha(patch)==shared['patch_sha256']
  manifest=W/lock['manifest']
  assert hashlib.sha256(json.dumps(read(manifest),sort_keys=True,separators=(',',':')).encode()).hexdigest()==lock['manifest_json_sha256']
  run(['git','init','-q',str(src)])
  run(['git','-C',str(src),'fetch','--depth=1','/home/paul/xbox-windows-native/build/video-reuse-001/source',lock['base_commit']])
  run(['git','-C',str(src),'checkout','--detach','FETCH_HEAD'])
  run([sys.executable,str(W/'tools/apply-series.py'),'--source',str(src),'--manifest',str(manifest)])
  assert tree(src)==shared['parent_tree']
  run(['git','-C',str(src),'apply','--index',str(patch)])
  r['reactos_parent_tree']=tree(src)
  assert r['reactos_parent_tree']==read(W/'outputs/video-shared-framebuffer/build-report.json')['source_tree']
  run(['git','init','-q',str(crom)])
  run(['git','-C',str(crom),'fetch','--depth=1','/home/paul/xbox-windows-native/sources/cromwell','9fc54d0c7cbed7bc3c70373642d833684853011f'])
  run(['git','-C',str(crom),'checkout','--detach','FETCH_HEAD'])
  cpins={'outputs/native-windows-physical-loader/cromwell-base.patch':'69964e0a5f5557881486b4668ddd2e940ecbf1cc26110e1960366ca7ecf5e12e','outputs/native-windows-physical-f/cromwell-f-launcher.patch':'1a47d42c371540549a8fb1f4de40404ca8436e4ad35f1e2c8236f82bc367fbb2'}
  cpins['outputs/launcher-relocation293/relocation.patch']=read(W/'outputs/launcher-relocation293/source-plan.json')['patch_sha256']
  for n,h in cpins.items():
   assert sha(W/n)==h;run(['git','-C',str(crom),'apply',str(W/n)])
  run(['git','-C',str(crom),'add','-u']);r['cromwell_parent_tree']=tree(crom)
  assert r['cromwell_parent_tree']=='d8de181fb893f0360e8e8e947b5768b25101e678'
  paths=['CMakeLists.txt','sdk/include/reactos/drivers/xbox/xgpu.h','drivers/base/bootvid/xwn_fb.h','win32ss/drivers/miniport/xboxvmp/nt5/xwn_fb.h','drivers/base/bootvid/xwn_fb.c','drivers/base/bootvid/i386/xbox/bootvid.c','win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c','win32ss/drivers/miniport/xboxvmp/nt5/video_shared.c','boot/freeldr/freeldr/arch/i386/xbox/xboxvideo.c','boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c']
  cpaths=['include/memory_layout.h','boot/BootResetAction.c','boot/LoadReactOS.c']
  originals={('reactos',n):(src/n).read_bytes() for n in paths}
  originals.update({('cromwell',n):(crom/n).read_bytes() for n in cpaths})
  change(src,'CMakeLists.txt','project(REACTOS)','''project(REACTOS)
option(XBOX_NT5_HD_RESERVATION "Opt-in retail64 nine-MiB framebuffer contract" OFF)
if(XBOX_NT5_HD_RESERVATION)
    if(NOT SARCH STREQUAL "xbox" OR NOT XBOX_NT5_HAL OR NOT XBOX_NT5_SHARED_FRAMEBUFFER)
        message(FATAL_ERROR "HD reservation requires Xbox NT5 shared framebuffer")
    endif()
    if(XBOX_NATIVE_FATX_PAGING_PREFLIGHT)
        message(FATAL_ERROR "Legacy paging diagnostic is not HD-reservation aware")
    endif()
    add_definitions(-DXBOX_NT5_HD_RESERVATION=1)
endif()''')
  n='sdk/include/reactos/drivers/xbox/xwn_hd_layout.h';(src/n).write_bytes((K/'xwn_hd_layout.h').read_bytes());originals[('reactos',n)]=b''
  old='#define NV2A_VIDEO_MEMORY_SIZE  (4 * 1024 * 1024) /* FIXME: obtain fb size from firmware somehow (Cromwell reserves high 4 MB of RAM) */'
  change(src,'sdk/include/reactos/drivers/xbox/xgpu.h',old,'#ifdef XBOX_NT5_HD_RESERVATION\n#include <drivers/xbox/xwn_hd_layout.h>\n#define NV2A_VIDEO_MEMORY_SIZE XWN_HD_FB_BYTES\n#else\n'+old+'\n#endif')
  for n in ['drivers/base/bootvid/xwn_fb.h','win32ss/drivers/miniport/xboxvmp/nt5/xwn_fb.h']:
   change(src,n,'#define XWN_FB_VERSION 1\n#define XWN_FB_BYTES 0x00400000','''#ifdef XBOX_NT5_HD_RESERVATION
#include <drivers/xbox/xwn_hd_layout.h>
#define XWN_FB_VERSION 2
#define XWN_FB_BYTES XWN_HD_FB_BYTES
#else
#define XWN_FB_VERSION 1
#define XWN_FB_BYTES 0x00400000
#endif''')
  n='drivers/base/bootvid/xwn_fb.c'
  change(src,n,'        (View->Physical != 0x03c00000 && View->Physical != 0x07c00000) ||','''#ifdef XBOX_NT5_HD_RESERVATION
        View->Physical != XWN_HD_FB_PHYSICAL ||
#else
        (View->Physical != 0x03c00000 && View->Physical != 0x07c00000) ||
#endif''')
  change(src,n,'    if (InterlockedCompareExchange(&Ready, -1, 0) != 0) return FALSE;','''#ifdef XBOX_NT5_HD_RESERVATION
    if (!XwnHdLayoutValid(View->Physical, View->ReservedBytes, View->Width,
                          View->Height, View->Stride, View->HiddenOffset)) return FALSE;
#endif
    if (InterlockedCompareExchange(&Ready, -1, 0) != 0) return FALSE;''')
  change(src,n,'    if (InterlockedCompareExchange(&Ready, 1, 1) != 1) return STATUS_DEVICE_NOT_READY;','''#ifdef XBOX_NT5_HD_RESERVATION
    if (View->ReservedBytes != XWN_FB_BYTES) return Status;
#endif
    if (InterlockedCompareExchange(&Ready, 1, 1) != 1) return STATUS_DEVICE_NOT_READY;''')
  n='drivers/base/bootvid/i386/xbox/bootvid.c'
  change(src,n,'    FrameBuffer &= 0x0FFFFFFF;','''    FrameBuffer &= 0x0FFFFFFF;
#ifdef XBOX_NT5_HD_RESERVATION
    if (FrameBuffer != XWN_HD_FB_PHYSICAL || FrameBufferWidth > 1920 || FrameBufferHeight > 1080)
        goto cleanup;
#endif''')
  change(src,n,'    /* Return the address back to GPU memory mapped I/O */','''#ifdef XBOX_NT5_HD_RESERVATION
    if (BackBufferSize != XWN_HD_BOOT_BACK_BYTES ||
        !XwnHdLayoutValid(FrameBuffer, NV2A_VIDEO_MEMORY_SIZE, FrameBufferWidth,
                          FrameBufferHeight, FrameBufferWidth * BytesPerPixel,
                          NV2A_VIDEO_MEMORY_SIZE - BackBufferSize)) goto cleanup;
#endif
    /* Return the address back to GPU memory mapped I/O */''')
  n='win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c'
  change(src,n,'        (V->Offset != 0x03c00000 && V->Offset != 0x07c00000) ||','''#ifdef XBOX_NT5_HD_RESERVATION
        !XwnHdLayoutValid(V->Offset, NV2A_VIDEO_MEMORY_SIZE, Width, Height, Pitch, XWN_HD_HIDDEN_OFFSET) ||
#else
        (V->Offset != 0x03c00000 && V->Offset != 0x07c00000) ||
#endif''')
  n='win32ss/drivers/miniport/xboxvmp/nt5/video_shared.c'
  change(src,n,'    View.Size = sizeof(View); View.Version = XWN_FB_VERSION;','''    View.Size = sizeof(View); View.Version = XWN_FB_VERSION;
#ifdef XBOX_NT5_HD_RESERVATION
    View.ReservedBytes = XWN_FB_BYTES;
#endif''')
  n='boot/freeldr/freeldr/arch/i386/xbox/xboxvideo.c'
  change(src,n,'    ScreenWidth = READ_REGISTER_ULONG', '''#ifdef XBOX_NT5_HD_RESERVATION
    if ((FrameBuffer & 0x0FFFFFFF) != XWN_HD_FB_PHYSICAL || FrameBufferSize != XWN_HD_FB_BYTES)
        FrLdrBugCheckWithMessage(0, __FILE__, __LINE__, "HD framebuffer map mismatch");
#endif
    ScreenWidth = READ_REGISTER_ULONG''')
  change(src,n,'    /* Get BPP directly from NV2A CRTC', '''#ifdef XBOX_NT5_HD_RESERVATION
    if (ScreenWidth < 640 || ScreenWidth > 1920 || ScreenHeight < 480 || ScreenHeight > 1080)
        FrLdrBugCheckWithMessage(0, __FILE__, __LINE__, "HD framebuffer geometry mismatch");
#endif
    /* Get BPP directly from NV2A CRTC''')
  change(src,n,'    /* Verify screen resolution */','''#ifdef XBOX_NT5_HD_RESERVATION
    if (BytesPerPixel != 4 ||
        !XwnHdLayoutValid(FrameBuffer & 0x0FFFFFFF, FrameBufferSize, ScreenWidth, ScreenHeight,
                          8 * (((NvGetCrtc(0x19) & 0xE0) << 3) | NvGetCrtc(0x13)), XWN_HD_HIDDEN_OFFSET))
        FrLdrBugCheckWithMessage(0, __FILE__, __LINE__, "HD framebuffer pitch mismatch");
#endif
    /* Verify screen resolution */''')
  n='boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c'
  change(src,n,'    if (MbMap)\n    {','''#ifdef XBOX_NT5_HD_RESERVATION
    if (!MbMap || Count != 2 || InstalledMemoryMb != 64)
        FrLdrBugCheckWithMessage(0, __FILE__, __LINE__, "HD reservation requires exact retail64 map");
    for (i = 0; i < Count; ++i)
        if (!XwnHdMapEntryValid(i, MbMap[i].base_addr_low, MbMap[i].base_addr_high,
                               MbMap[i].length_low, MbMap[i].length_high, MbMap[i].type))
            FrLdrBugCheckWithMessage(0, __FILE__, __LINE__, "HD reservation map entry mismatch");
#endif
    if (MbMap)
    {''')
  change(crom,'include/memory_layout.h','#define MAX_INITRD_END     0x03800000','''#ifdef XWN_HD_RESERVATION
#define MAX_INITRD_END     0x03700000
#else
#define MAX_INITRD_END     0x03800000
#endif''')
  change(crom,'include/memory_layout.h','#define FB_SIZE 0x00400000','''#ifdef XWN_HD_RESERVATION
#define FB_SIZE 0x00900000
#else
#define FB_SIZE 0x00400000
#endif''')
  change(crom,'boot/BootResetAction.c','memset((void *)FB_START,0x00,0x400000);','memset((void *)FB_START,0x00,FB_SIZE);')
  change(crom,'boot/LoadReactOS.c','\tif (mbHeader == NULL)\n\t\treturn;','''\tif (mbHeader == NULL)
\t\treturn;
#ifdef XWN_HD_RESERVATION
\tif (xbox_ram != 64) {
\t\tprintk("HD reservation requires a 64 MB console.\\n");
\t\treturn;
\t}
#endif''')
  for label,root in [('reactos',src),('cromwell',crom)]:
   diffs=[]
   for (l,n),before in originals.items():
    if l!=label:continue
    after=(root/n).read_bytes()
    r['changes'][l+'/'+n]=dict(before=hashlib.sha256(before).hexdigest(),after=hashlib.sha256(after).hexdigest())
    diffs.extend(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+n if before else '/dev/null',tofile='b/'+n))
   (K/(label+'-reservation.patch')).write_text(''.join(diffs))
   run(['git','-C',str(root),'add','-A']);r[label+'_candidate_tree']=tree(root)
  r['status']='source_prepared';r['patches']={str(p.name):sha(p) for p in K.glob('*-reservation.patch')}
except Exception as e:r.update(status='failed',error=repr(e));raise
finally:
 (K/'source-review001.json').write_text(json.dumps(r,indent=2)+'\n')
 print(r['status'])
