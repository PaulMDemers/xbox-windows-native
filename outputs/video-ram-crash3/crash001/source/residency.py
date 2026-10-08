"""Bounded physical-page evidence: absent display pages stay absent, never faulted in."""
import hashlib,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'video-shared-trace2'))
from walk import table,physical,read_virtual

def inspect_display(ram,cr3,base,pe,symbols):
 assert len(ram)==67108864
 sec=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.text')
 expected=bytearray(pe.get_data(sec.VirtualAddress,sec.Misc_VirtualSize));begin=base+sec.VirtualAddress;end=begin+len(expected)
 for block in getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[]):
  for e in block.entries:
   if e.type==3 and sec.VirtualAddress<=e.rva<sec.VirtualAddress+len(expected):
    off=e.rva-sec.VirtualAddress;assert off+4<=len(expected)
    struct.pack_into('<I',expected,off,(struct.unpack_from('<I',expected,off)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 rows=[];mapped=0;directory=table(ram,cr3&~4095);va=begin
 while va<end:
  n=min(4096-(va&4095),end-va);pde=directory[va>>22];pte=None
  if pde&1 and not pde&128:pte=table(ram,pde&~4095)[(va>>12)&1023]
  present=bool(pde&1 and (pde&128 or pte&1))
  row=dict(virtual=va,rva=va-base,bytes=n,pde=pde,pte=pte,present=present)
  if present:
   actual=read_virtual(ram,cr3,va,n);wanted=expected[va-begin:va-begin+n];assert actual==wanted,('mapped code mismatch',hex(va))
   row.update(physical=physical(ram,cr3,va),actual=actual.hex(),sha256=hashlib.sha256(actual).hexdigest());mapped+=n
  rows.append(row);va+=n
 assert len(rows)<=64
 for label in ['XwnUpload','DrvAssertMode']:
  va=base+symbols[label];assert begin<=va<va+32<=end
  assert read_virtual(ram,cr3,va,32)==expected[va-begin:va-begin+32]
 return dict(base=base,text_rva=sec.VirtualAddress,total_bytes=len(expected),mapped_bytes=mapped,unmapped_bytes=len(expected)-mapped,pages=rows,
  required_mapped_functions=['XwnUpload','DrvAssertMode'],whole_display_text_resident=mapped==len(expected))
