from pathlib import Path
import struct,sys,json
sys.path.insert(0,'work/python-packages');import pefile
out=Path('outputs/native-windows-nt5-kernel');obj=Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/build/kernel-autorun/boot/freeldr/freeldr/CMakeFiles/freeldr_common.dir/lib/fs/ntfs.c.obj').read_bytes();pe=pefile.PE(str(out/'artifacts/autorun-006/freeldr_pe.exe'))
_,nsec,_,sympos,nsym,opts,_=struct.unpack_from('<HHIIIHH',obj);sections=[]
for i in range(nsec):
 h=struct.unpack_from('<8s6I2HI',obj,20+opts+i*40);sections.append({'name':h[0],'size':h[3],'raw':h[4],'reloc':h[5],'count':h[7]})
strpos=sympos+nsym*18;syms=[];i=0
while i<nsym:
 raw,value,sec,typ,cls,aux=struct.unpack_from('<8sIhHBB',obj,sympos+i*18)
 if raw[:4]==bytes(4):a=strpos+struct.unpack_from('<I',raw,4)[0];name=obj[a:obj.find(bytes(1),a)].decode()
 else:name=raw.rstrip(bytes(1)).decode()
 if sec>0 and typ==0x20:syms.append((name,value,sec))
 i+=1+aux
text=pe.sections[0];code=text.get_data();result={}
for name,start,sec in syms:
 if not name.startswith('_Ntfs'):continue
 section=sections[sec-1];end=min([v for _,v,s in syms if s==sec and v>start]+[section['size']]);pattern=obj[section['raw']+start:section['raw']+end];mask=bytearray([1])*len(pattern)
 for j in range(section['count']):
  at,_,typ=struct.unpack_from('<IIH',obj,section['reloc']+j*10)
  if start<=at<end:mask[at-start:at-start+4]=bytes(4)
 # Use the longest contiguous unrelocated region to locate each function.
 spans=[];a=0
 while a<len(mask):
  if not mask[a]:a+=1;continue
  b=a
  while b<len(mask) and mask[b]:b+=1
  spans.append((a,b));a=b
 a,b=max(spans,key=lambda x:x[1]-x[0]);candidates=[];pos=0
 while True:
  pos=code.find(pattern[a:b],pos)
  if pos<0:break
  target=pos-a
  if target>=0 and all(not mask[j] or code[target+j]==v for j,v in enumerate(pattern)):candidates.append(target)
  pos+=1
 assert len(candidates)==1,(name,candidates)
 result[name]=pe.OPTIONAL_HEADER.ImageBase+text.VirtualAddress+candidates[0]
(out/'ntfs-functions.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
