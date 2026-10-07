"""Create a bounded direct-only NT5 display candidate from the pinned source lead."""
import difflib,hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
contract=read(k.parent/'video-late-cache-review/shadow-contract.json');src=Path(contract['source_root'])
out=k/'display';assert not out.exists();out.mkdir()
original={}
for n,h in contract['source_files'].items():
 p=src/n;assert sha(p)==h;original[n]=p.read_text();(out/n).write_text(original[n], newline='\n')
def edit(name,old,new):
 p=out/name;s=p.read_text();assert s.count(old)==1,(name,old);p.write_text(s.replace(old,new), newline='\n')
for prefix in ['add_library','set_module_type','add_pch','target_link_libraries','add_importlibs','add_dependencies']:
 edit('CMakeLists.txt',prefix+'(framebuf',prefix+'(xwndir')
edit('CMakeLists.txt','TARGET framebuf','TARGET xwndir')
edit('framebuf.h','L"framebuf"','L"xwndir"')
edit('enable.c','static DRVFN DrvFunctionTable[]', '''/* Read-only identity/geometry escape; no pointers or memory writes exposed. */
static ULONG APIENTRY
XwnDirectEscape(SURFOBJ *Surface, ULONG Escape, ULONG InBytes, PVOID In,
                ULONG OutBytes, PVOID Out)
{
   PPDEV p;
   ULONG Data[8];
   if (Escape != 0x58574431 || InBytes || In || !Surface || !Out ||
       OutBytes != sizeof(Data) || !Surface->dhpdev) return 0;
   p = (PPDEV)Surface->dhpdev;
   if (!p->ScreenPtr || !p->hSurfEng) return 0;
   Data[0] = 0x44525758; Data[1] = 107;
   Data[2] = p->ScreenWidth; Data[3] = p->ScreenHeight;
   Data[4] = p->ScreenDelta; Data[5] = p->BitsPerPixel;
   Data[6] = p->ScreenDelta * p->ScreenHeight; Data[7] = 0;
   memcpy(Out, Data, sizeof(Data));
   return 1;
}

static DRVFN DrvFunctionTable[]''')
edit('enable.c','   {INDEX_DrvEnablePDEV,','   {INDEX_DrvEscape, (PFN)XwnDirectEscape},\n   {INDEX_DrvEnablePDEV,')
edit('enable.c','   ppdev->hDriver = hDriver;','   RtlZeroMemory(&GdiInfo, sizeof(GdiInfo));\n   RtlZeroMemory(&DevInfo, sizeof(DevInfo));\n   ppdev->hDriver = hDriver;')
edit('screen.c','   if (Modes.NumModes == 0)','   if (Modes.NumModes == 0 || Modes.NumModes > 128 ||\n       Modes.ModeInformationLength < sizeof(VIDEO_MODE_INFORMATION) ||\n       Modes.ModeInformationLength > 4096 || ulTemp < sizeof(Modes))')
edit('screen.c','   *ModeInfoSize = Modes.ModeInformationLength;','   *ModeInfoSize = Modes.ModeInformationLength;')
# Query mode records must have been supplied in full before walking them.
edit('screen.c','                          &ulTemp))\n   {\n      EngFreeMem(*ModeInfo);','                          &ulTemp) ||\n       ulTemp < Modes.NumModes * Modes.ModeInformationLength)\n   {\n      EngFreeMem(*ModeInfo);')
edit('screen.c','      memset(pdm, 0, sizeof(DEVMODEW));','      if (cjSize - OutputSize < sizeof(DEVMODEW)) break;\n\n      memset(pdm, 0, sizeof(DEVMODEW));')
edit('surface.c','   ppdev->ScreenPtr = VideoMemoryInfo.FrameBufferBase;','''   /* Bound this prototype to the qualified positive-stride 32-bit contract. */
   ppdev->ScreenPtr = VideoMemoryInfo.VideoRamBase;
   if (ulTemp < sizeof(VideoMemoryInfo) || !ppdev->ScreenPtr ||
       VideoMemoryInfo.FrameBufferBase != ppdev->ScreenPtr ||
       ppdev->BitsPerPixel != 32 || !ppdev->ScreenWidth ||
       ppdev->ScreenWidth > 1920 || !ppdev->ScreenHeight ||
       ppdev->ScreenHeight > 1080 || ppdev->ScreenDelta != ppdev->ScreenWidth * 4 ||
       ppdev->ScreenHeight > 0x400000 / ppdev->ScreenDelta ||
       VideoMemoryInfo.FrameBufferLength < ppdev->ScreenHeight * ppdev->ScreenDelta)
      goto FailMapping;''')
edit('surface.c','   ULONG ulTemp;\n\n   /*','   ULONG ulTemp;\n\n   if (ppdev->ScreenPtr || ppdev->hSurfEng) return NULL;\n   RtlZeroMemory(&VideoMemoryInfo, sizeof(VideoMemoryInfo));\n\n   /*')
edit('surface.c','      default:\n         return NULL;','      default:\n         goto FailMapping;')
edit('surface.c','   if (hSurface == NULL)\n   {\n      return NULL;\n   }','   if (hSurface == NULL)\n   {\n      goto FailMapping;\n   }')
edit('surface.c','      EngDeleteSurface(hSurface);\n      return NULL;','      EngDeleteSurface(hSurface);\n      goto FailMapping;')
edit('surface.c','   return hSurface;\n}','''   return hSurface;

FailMapping:
   if (ppdev->ScreenPtr)
   {
      VideoMemory.RequestedVirtualAddress = ppdev->ScreenPtr;
      EngDeviceIoControl(ppdev->hDriver, IOCTL_VIDEO_UNMAP_VIDEO_MEMORY,
                         &VideoMemory, sizeof(VideoMemory), NULL, 0, &ulTemp);
      ppdev->ScreenPtr = NULL;
   }
   return NULL;
}''')
edit('surface.c','   EngDeleteSurface(ppdev->hSurfEng);','   if (ppdev->hSurfEng) EngDeleteSurface(ppdev->hSurfEng);')
edit('surface.c','   EngDeviceIoControl(((PPDEV)dhpdev)->hDriver, IOCTL_VIDEO_UNMAP_VIDEO_MEMORY,\n                      &VideoMemory, sizeof(VIDEO_MEMORY), NULL, 0, &ulTemp);','''   if (ppdev->ScreenPtr)
      EngDeviceIoControl(ppdev->hDriver, IOCTL_VIDEO_UNMAP_VIDEO_MEMORY,
                         &VideoMemory, sizeof(VideoMemory), NULL, 0, &ulTemp);
   ppdev->ScreenPtr = NULL;''')
# No mapping/cache/mode or miniport changes; diagnostics remain read-only.
patch=''
for n,before in original.items():
 after=(out/n).read_text()
 if after!=before:
  path='win32ss/drivers/displays/framebuf/'+n
  patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),'a/'+path,'b/'+path))
(k/'0107-direct-nt5-display.patch').write_text(patch, newline='\n')
(k/'patch-review.json').write_text(json.dumps(dict(parent_tree=contract['source_tree'],
 original_files=contract['source_files'],source_files={p.name:sha(p) for p in sorted(out.iterdir())},
 patch_sha256=sha(k/'0107-direct-nt5-display.patch'),generator_sha256=sha(Path(__file__)),
 scope='Renamed direct-only DDI; bounded mode queries and map unwind; zeroed caps; read-only escape. No shadow or GPU/cache changes.'),indent=2)+'\n')
print('Prepared direct-only source and patch')
