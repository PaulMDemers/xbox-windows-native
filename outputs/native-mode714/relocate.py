"""Extract a bounded relocation recipe from the fresh ELF, not firmware bytes.
Only internal absolute32 and PC-relative32 entries are admitted. Kernel loader
integration still needs independent ownership/alias/page-walk validation.
"""
from pathlib import Path
import struct,re,hashlib
ORIGIN=0x100000
def entries(raw,blob):
 rows=[];seen=set()
 for line in raw.splitlines():
  a=line.split()
  if not a or not re.fullmatch('[0-9a-fA-F]{8}',a[0]):continue
  assert len(a)>=5 and a[2] in ('R_386_32','R_386_PC32'),line
  at=int(a[0],16)-ORIGIN;symbol=int(a[3],16)
  assert 0<=at<=len(blob)-4 and ORIGIN<=symbol<ORIGIN+len(blob),line
  assert all(at+j not in seen for j in range(4)),line
  seen.update(range(at,at+4));value=struct.unpack_from('<I',blob,at)[0]
  if a[2]=='R_386_32':assert ORIGIN<=value<ORIGIN+len(blob),line
  rows.append({'offset':at,'type':a[2],'symbol':a[4],'symbol_value':symbol,'value':value})
 assert rows and len(rows)==17
 return rows
def relocated(blob,rows,load):
 # A proposed32KiB bridge allocation: first4KiB entry/tables, then <=16KiB
 # transaction, then separately reserved request/result and stack. No allocation
 # is performed here. Bounds deliberately leave those other regions untouched.
 base=load-4096
 assert not base&4095 and 0x1000000<=base<=0x1ff8000 and len(blob)<=0x4000
 result=bytearray(blob);delta=load-ORIGIN
 for row in rows:
  if row['type']=='R_386_32':
   old=struct.unpack_from('<I',result,row['offset'])[0]
   assert old==row['value']
   new=old+delta;assert load<=new<load+len(blob)
   struct.pack_into('<I',result,row['offset'],new)
 return bytes(result)
