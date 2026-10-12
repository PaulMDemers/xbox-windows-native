"""Independent envelope check; core decoder stays byte-identical to284."""
import struct
import core_decode
def decode(data,owner,keys,ids,names):
 assert len(data)==5504 and owner>0
 h=struct.unpack_from('<8Q',data)
 assert h==(0x3538324e5758,285,5504,owner,2,0,0,1)
 result=core_decode.decode(data[64:],keys,ids,names)
 assert result['owner']==owner
 return dict(publication_envelope_valid=True,core=result,actual_runtime_qualified=False)
