"""Compare the final raw physical framebuffer with the captured PNG exactly."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash001'
sys.path.insert(0,str(ws/'work/python-packages'));from PIL import Image
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');raw=Path(t['private_memory']);assert sha(raw)==t['private_memory_sha256'];data=raw.read_bytes()
view=t['boot_after']['published'];assert view[3:9]==[0x03c00000,0x400000,2359296,1024,576,4096]
image=Image.frombytes('RGB',(1024,576),data[view[3]:view[3]+2359296],'raw','BGRX')
captured=Image.open(out/'artifacts/crash.png').convert('RGB');assert captured.size==image.size and captured.tobytes()==image.tobytes()
colors=dict((rgb,count) for count,rgb in image.getcolors(4));assert set(colors)=={(0,0,0),(0,0,128),(255,255,255)} and colors[(255,255,255)]>0
r=dict(passed=True,physical_access=False,pixels_compared=589824,all_rgb_pixels_exact=True,crash_screen_sha256=sha(out/'artifacts/crash.png'),
 memory_sha256=sha(raw),trace_sha256=sha(out/'trace.json'),white_pixels=colors[(255,255,255)],
 visual_review='Assistant inspected an enlarged crop from this PNG: intended E058D103 with44554D50/103/10000/1 and physical-memory-dump-complete text are legible.',
 limits='Exact physical scanout/screenshot agreement for this one post-dump image; does not prove arbitrary rendering or physical hardware.')
dest=k/'screen-verification.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
