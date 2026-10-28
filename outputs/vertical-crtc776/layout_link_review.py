"""Verify actual probe COFF instruction bytes in PE and XBE, excluding relocation operands."""
from pathlib import Path
import struct,hashlib,json,datetime
k=Path(__file__).resolve().parent;p=Path('C:/xwn776/build001');out=k/'layout-link-review001.json';assert not out.exists()
b=(p/'layout.obj').read_bytes();_,nsec,_,_,_,_,_=struct.unpack_from('<HHLLLHH',b)
r={'passed':False,'checks':[],'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
try:
 for filename in ('main.exe','bin/default.xbe'):
  image=(p/filename).read_bytes()
  for j in range(nsec):
   h=struct.unpack_from('<8sLLLLLLHHL',b,20+40*j);name=h[0].split(b'\0')[0].decode()
   if not h[3] or not h[9]&0x20:continue
   raw=b[h[4]:h[4]+h[3]];mask=bytearray(b'\1'*len(raw))
   for i in range(h[7]):
    off,idx,typ=struct.unpack_from('<LLH',b,h[5]+10*i);assert typ in (6,20);mask[off:off+4]=b'\0'*4
   segments=[];start=0
   while start<len(raw):
    if not mask[start]:start+=1;continue
    end=start
    while end<len(raw) and mask[end]:end+=1
    segments.append((start,end));start=end
   a,z=max(segments,key=lambda x:x[1]-x[0]);anchor=raw[a:z];candidates=[];pos=image.find(anchor)
   while pos!=-1:
    offset=pos-a
    if offset>=0 and all(not mask[i] or image[offset+i]==v for i,v in enumerate(raw)):candidates.append(offset)
    pos=image.find(anchor,pos+1)
   assert len(candidates)==1,(name,candidates)
   r['checks'].append({'image':filename,'sha256':hashlib.sha256(image).hexdigest(),'section':name,'bytes':len(raw),'relocations':h[7],'file_offset':candidates[0],'all_nonrelocation_bytes_exact':True,'anchor_bytes':len(anchor)})
 assert len(r['checks'])==2;r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
