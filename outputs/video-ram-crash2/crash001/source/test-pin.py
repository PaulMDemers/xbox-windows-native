"""Exercise the actual pin implementation with fixed-image and relocated PE bytes."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
mods=json.loads((k/'modules.json').read_text());pes={n:pefile.PE(m['path']) for n,m in mods.items()}
source=(k/'trace.py').read_text();body=source[source.index('def pin('):source.index('\ndef arm(')]
tests=[]
for name,delta,header_missing in [('probe.exe',0,False),('xwnown.dll',0xbffd0000,False),('xwnown.dll',0xbffd0000,True)]:
 pe=pes[name];base=pe.OPTIONAL_HEADER.ImageBase+delta;memory=bytearray(pe.get_memory_mapped_image())
 for block in getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[]):
  for e in block.entries:
   if e.type==3:struct.pack_into('<I',memory,e.rva,(struct.unpack_from('<I',memory,e.rva)[0]+delta)&0xffffffff)
 class Remote:
  def read(self,a,n):
   if header_missing and a==base:raise AssertionError('E14')
   assert base<=a<a+n<=base+len(memory);return bytes(memory[a-base:a-base+n])
 g=Remote();r=dict(runtime_pins=[]);ns=dict(loaded=[dict(base=base,size=(mods[name]['image_size']+4095)&~4095,name=name)],pes=pes,mods=mods,g=g,r=r,headers={},struct=struct)
 ns['u32']=lambda a:struct.unpack('<I',g.read(a,4))[0];exec(body,ns)
 sec=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.text');offset=0
 while offset<sec.Misc_VirtualSize:
  i=ns['pin'](base+sec.VirtualAddress+offset,min(48,sec.Misc_VirtualSize-offset));offset+=len(bytes.fromhex(r['runtime_pins'][i]['raw']))
 assert offset==sec.Misc_VirtualSize
 memory[sec.VirtualAddress]^=1
 try:ns['pin'](base+sec.VirtualAddress)
 except AssertionError:rejected=True
 else:raise AssertionError('Corrupted executable byte accepted')
 tests.append(dict(module=name,base=base,header_missing=header_missing,bytes_checked=offset,pins=len(r['runtime_pins']),corruption_rejected=rejected))
result=dict(passed=True,cases=tests,trace_sha256=hashlib.sha256(source.encode()).hexdigest(),limits='Host transport simulation against actual pinned PE bytes, not guest residency.')
dest=k/'pin-tests.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
