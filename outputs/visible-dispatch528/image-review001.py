"""Validate actual PPM markers; lossless PNG views from the unchanged captures."""
import hashlib,json,struct,zlib
from pathlib import Path
from capture import ppm
K=Path(__file__).resolve().parent;O=Path('C:/xwn528/emu002')
out=K/'image-review001.json';assert not out.exists()
r=dict(passed=False,physical_access=False,images=[])
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
try:
 for i,color in [(1,(0,96,192)),(2,(0,160,64))]:
  path=O/f'screen{i}.ppm';data=path.read_bytes();w,h,offset=ppm(data);assert (w,h)==(1280,720)
  capture=json.loads((K/f'capture002-{i}.json').read_text(encoding='utf-8'))
  assert capture['completed'] and hashlib.sha256(data).hexdigest()==capture['sha256']
  pixels=data[offset:]
  points=[(x,y) for x in (100,640,1180) for y in (580,640,700)]
  actual=[tuple(pixels[(y*w+x)*3:(y*w+x)*3+3]) for x,y in points];assert all(c==color for c in actual),actual
  top=pixels[:560*w*3];assert sum(top[n:n+3]==b'\xff\xff\xff' for n in range(0,len(top),3))>1000
  raw=b''.join(b'\0'+pixels[y*w*3:(y+1)*w*3] for y in range(h))
  png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
  view=O/f'screen{i}.png';assert not view.exists();view.write_bytes(png)
  r['images'].append(dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),width=w,height=h,sampled_points=points,sampled_RGB=actual,view=str(view),PNG_sha256=hashlib.sha256(png).hexdigest()))
 r.update(passed=True,blue_and_green_captured=True,interpretation='Marker meanings follow pinned528 app source; no physical-display or Windows qualification')
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('PASS two actual1280x720 blue/green captures; lossless private PNG views')
