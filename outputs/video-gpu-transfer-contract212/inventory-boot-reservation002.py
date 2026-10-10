"""Actual bootvid reservation vs an explicitly hypothetical pbkit comment placement."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'boot-reservation.json';assert not dest.exists()
src=Path('/home/paul/xbox-windows-native/build/video-shared-framebuffer-001/source')
names=['drivers/base/bootvid/precomp.h','sdk/include/reactos/drivers/bootvid/display.h',
 'drivers/base/bootvid/i386/xbox/bootvid.c','drivers/base/bootvid/xwn_fb.c']
assert all((src/n).exists() for n in names)
art=k/'artifacts/boot-reservation';art.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
for n in names:
 q=art/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((src/n).read_bytes());assert sha(q)==sha(src/n);pins[n]=sha(q)
pre=(art/names[0]).read_text();display=(art/names[1]).read_text();boot=(art/names[2]).read_text()
value=lambda text,name:int(re.search(r'^#define\s+'+name+r'\s+(\d+)\b',text,re.M).group(1))
w,h,c=value(display,'SCREEN_WIDTH'),value(display,'SCREEN_HEIGHT'),value(pre,'BOOTCHAR_HEIGHT')
assert (w,h,c)==(640,480,13)
assert 'SCREEN_WIDTH * (SCREEN_HEIGHT + BOOTCHAR_HEIGHT + 1)' in boot
assert 'FrameBufferStart + NV2A_VIDEO_MEMORY_SIZE - BackBufferSize' in boot
length=w*(h+c+1);rows=[]
for base in [0x03c00000,0x07c00000]:
 lo=base+0x400000-length;hi=base+0x400000
 rows.append(dict(framebuffer_base=base,indexed_backbuffer_start=lo,indexed_backbuffer_end=hi,indexed_backbuffer_bytes=length))
pb=k/'artifacts/nxdk/lib/pbkit/pbkit.c';text=pb.read_text()
assert '#define INSTANCE_MEM_MAXSIZE' in text and '0x5000' in text and '// =0x83FEB000' in text
hypothesis=(0x03feb000,0x03ff0000);overlap=max(0,min(rows[0]['indexed_backbuffer_end'],hypothesis[1])-max(rows[0]['indexed_backbuffer_start'],hypothesis[0]))
assert overlap==0x5000
r=dict(passed=True,source_sha256=sha(Path(__file__)),source_pins=pins,pbkit_sha256=sha(pb),reservations=rows,
 hypothesis=dict(start=hypothesis[0],end=hypothesis[1],overlap_bytes=overlap,
 basis='Commented pb_GpuInstMem pointer after subtraction. That pointer has no further uses in this pinned pbkit source; actual PRAMIN backing/claim result is not established.'),
 actual_pramin_alias_proven=False,guest_launch=False,physical_access=False,gpu_register_access=False,
 limits='Static boot reservation arithmetic and a counterfactual source-comment placement only. Does not identify actual running firmware/GPU instance storage or a physical collision. Do not choose/overwrite a context location from this calculation.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Indexed boot backbuffer:',length,'bytes. Conditional commented-placement overlap:',overlap,'bytes; actual PRAMIN alias NOT established.')
