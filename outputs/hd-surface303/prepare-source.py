"""Generate a small opt-in patch against the exact qualified118 display files."""
import difflib,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-text-clip205/display'
review=json.loads((old.parent/'source-review.json').read_text());dest=k/'source-review.json';assert not dest.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
files={n:(old/n).read_bytes() for n in ['surface.c','CMakeLists.txt']}
for n,b in files.items():assert sha(b)==review['source_files'][n]
display=k/'display';display.mkdir()
s=files['surface.c'].decode();assert s.count('#include "framebuf.h"')==1
s=s.replace('#include "framebuf.h"','#include "framebuf.h"\n#include "surface_bounds.h"')
a='''       ppdev->BitsPerPixel != 32 || !ppdev->ScreenWidth ||'''
b='''       VideoMemoryInfo.FrameBufferLength < ppdev->ScreenHeight * ppdev->ScreenDelta)'''
assert s.count(a)==1 and s.count(b)==1
start=s.index(a);end=s.index(b)+len(b)
legacy=s[start:end-1]
s=s[:start]+'''#if XWN_HD_SURFACE_BOUNDS
       !XwnSurfaceBytes(ppdev->ScreenWidth, ppdev->ScreenHeight, ppdev->ScreenDelta,
                        ppdev->BitsPerPixel, VideoMemoryInfo.FrameBufferLength,
                        VideoMemoryInfo.VideoRamLength)
#else
'''+legacy+'''
#endif
       )'''+s[end:]
c=files['CMakeLists.txt'].decode()+'''
option(XWN_HD_SURFACE_BOUNDS "Use bounded reported lengths for HD shadow surfaces" OFF)
if(XWN_HD_SURFACE_BOUNDS)
 target_compile_definitions(xwnown PRIVATE XWN_HD_SURFACE_BOUNDS=1)
else()
 target_compile_definitions(xwnown PRIVATE XWN_HD_SURFACE_BOUNDS=0)
endif()
'''
changed={'surface.c':s,'CMakeLists.txt':c,'surface_bounds.h':(k/'surface_bounds.h').read_text()}
patch=[];pins={}
for n,text in changed.items():
    (display/n).write_text(text);pins[n]=sha((display/n).read_bytes())
    before=files.get(n,b'').decode().splitlines(keepends=True);after=text.splitlines(keepends=True)
    prefix='win32ss/drivers/displays/framebuf/'+n
    patch.extend(difflib.unified_diff(before,after,fromfile='a/'+prefix if before else '/dev/null',tofile='b/'+prefix))
p=k/'0119-hd-surface-bounds.patch';p.write_text(''.join(patch))
dest.write_text(json.dumps(dict(parent_source_files={n:sha(b) for n,b in files.items()},source_files=pins,
    patch_sha256=sha(p.read_bytes()),scope='Opt-in returned-length validation only; drawing and ownership routines unchanged'),indent=2)+'\n')
print('Prepared bounded surface patch')
