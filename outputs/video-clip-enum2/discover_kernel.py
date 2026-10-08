"""Identify the live pinned kernel using two independent x86 IDT gates."""
import re,struct
def discover(read,registers,pe,publics):
 idt,limit=[int(v,16) for v in re.search(r'IDT=\s*([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',registers).groups()]
 assert idt>=0x80000000 and limit>=0x2e*8+7
 gates=[]
 for vector,name in [(0,'_KiTrap00'),(0x2e,'_KiSystemService')]:
  raw=read(idt+vector*8,8);lo,selector,reserved,flags,hi=struct.unpack('<HHBBH',raw)
  assert selector==8 and reserved==0 and flags&0x80 and flags&0x1f in [14,15]
  entry=lo|(hi<<16);base=entry-publics[name]['rva'];assert base>=0x80000000 and base%4096==0
  gates.append(dict(vector=vector,name=name,raw=raw.hex(),entry=entry,rva=publics[name]['rva'],base=base))
 assert gates[0]['base']==gates[1]['base'];base=gates[0]['base']
 assert read(base,2)==b'MZ';nt=struct.unpack('<I',read(base+60,4))[0];assert nt<4096
 assert read(base+nt,4)==b'PE\0\0'
 stamp=struct.unpack('<I',read(base+nt+8,4))[0];size=struct.unpack('<I',read(base+nt+80,4))[0]
 assert stamp==pe.FILE_HEADER.TimeDateStamp and size==pe.OPTIONAL_HEADER.SizeOfImage
 return base,dict(idt=idt,limit=limit,gates=gates,kernel_base=base,timestamp=stamp,image_size=size)
