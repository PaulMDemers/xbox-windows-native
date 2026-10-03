"""Decode S_PUB32_ST records from the exact installed kernel's PDB2."""
import hashlib,json,pathlib,struct,sys
out=pathlib.Path(__file__).resolve().parent;root=out.parents[1]
sys.path.insert(0,str(root/'work/python-packages'))
import pefile
parser=out.parent/'native-windows-nt5-interrupts/read-pdb-layouts.py'
ns={'__file__':str(parser)};exec(parser.read_text().split('selected={}')[0],ns)
pe=pefile.PE(str(out.parent/'native-windows-nt5/installed-files/WINNT/system32/ntoskrnl.exe'))
# Stream 7 is the symbol-record stream in this pinned PDB (hash checked below).
assert hashlib.sha256(ns['p']).hexdigest()=='29f5de2a8db7959875b8a615945bd6f16e50e5c5a9465dd8f71b37f37d671e9e'
data=ns['streams'][7];pos=0;records={}
while pos<len(data):
 size,kind=struct.unpack_from('<HH',data,pos);end=pos+size+2;assert end<=len(data)
 if kind==0x1009:
  flags,offset,segment=struct.unpack_from('<IIH',data,pos+4);length=data[pos+14]
  name=data[pos+15:pos+15+length].decode('ascii');assert pos+15+length<=end
  if 1<=segment<=len(pe.sections):
   sec=pe.sections[segment-1];assert offset<max(sec.Misc_VirtualSize,sec.SizeOfRawData)
   records[name]={'rva':sec.VirtualAddress+offset,'flags':flags,'segment':segment}
 pos=end
assert records['_KiSystemStartup@4']['rva']==0x151588
(out/'kernel-publics.json').write_text(json.dumps({'pdb_sha256':hashlib.sha256(ns['p']).hexdigest(),'symbols':records},indent=2)+'\n')
print(len(records),'public symbols decoded')
