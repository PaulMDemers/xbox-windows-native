"""Convert referenced hashed leaf indexes to NT 5.0-compatible linear indexes.

hivex creates lh indexes even in a version 1.3 hive. Windows 2000 recognizes
li, lf and ri. The conversion reuses each allocated cell without resizing it.
Only reachable stable key indexes are visited; arbitrary cell payloads are not
interpreted as indexes. Values, key names, security cells and the header stay
byte-for-byte unchanged.
"""
import struct

def normalize(data):
 original=bytes(data);data=bytearray(data)
 assert data[:4]==b'regf'
 assert struct.unpack_from('<II',data,20)==(1,3)
 length=struct.unpack_from('<I',data,40)[0]
 assert length+4096<=len(data)
 cells={};position=4096
 while position<4096+length:
  assert data[position:position+4]==b'hbin'
  offset,size=struct.unpack_from('<II',data,position+4)
  assert offset==position-4096 and size>=4096 and size%4096==0
  end=position+size;assert end<=4096+length
  cell=position+32
  while cell<end:
   signed=struct.unpack_from('<i',data,cell)[0];n=abs(signed)
   assert n>=8 and n%8==0 and cell+n<=end
   if signed<0:cells[cell-4096]=(cell+4,n-4)
   cell+=n
  assert cell==end;position=end
 def allocated(index,signature=None):
  at,size=cells[index]
  if signature:assert data[at:at+2]==signature
  return at,size
 seen_keys=set();seen_indexes=set();changes=[]
 def index_children(index):
  assert index not in seen_indexes;seen_indexes.add(index)
  at,size=allocated(index);kind=bytes(data[at:at+2]);n=struct.unpack_from('<H',data,at+2)[0]
  assert kind in [b'li',b'lf',b'lh',b'ri']
  stride=8 if kind in [b'lf',b'lh'] else 4
  assert 4+n*stride<=size
  entries=[struct.unpack_from('<I',data,at+4+i*stride)[0] for i in range(n)]
  if kind==b'ri':return [child for entry in entries for child in index_children(entry)]
  if kind==b'lh':
   data[at:at+4+n*8]=b'li'+struct.pack('<H',n)+struct.pack('<'+'I'*n,*entries)+bytes(n*4)
   changes.append({'cell':hex(index),'children':n,'from':'lh','to':'li'})
  return entries
 def key(index):
  assert index not in seen_keys;seen_keys.add(index)
  at,size=allocated(index,b'nk');assert size>=76
  count=struct.unpack_from('<I',data,at+20)[0]
  if count:
   children=index_children(struct.unpack_from('<I',data,at+28)[0]);assert len(children)==count
   for child in children:key(child)
 key(struct.unpack_from('<I',data,36)[0])
 assert data[:4096]==original[:4096] and len(data)==len(original)
 return bytes(data),{'keys_checked':len(seen_keys),'indexes_checked':len(seen_indexes),'converted':changes}
