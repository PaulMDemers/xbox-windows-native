"""Read-only pinned retail PE import inventory with an independent table walk."""
import datetime,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
p=Path('C:/xwn566/transfer002/game/RCT.EXE');b=p.read_bytes()
h=hashlib.sha256(b).hexdigest();assert h=='bdfebd64383b231de0252fe0726523d1c45aa2c4da919c2d7ed8bfb7aaa05c76'
pe=pefile.PE(data=b)
expected={d.dll.decode('ascii'):[i.name.decode('ascii') if i.name else '#'+str(i.ordinal) for i in d.imports] for d in pe.DIRECTORY_ENTRY_IMPORT}
def u16(o):return struct.unpack_from('<H',b,o)[0]
def u32(o):return struct.unpack_from('<I',b,o)[0]
assert b[:2]==b'MZ';nt=u32(60);assert b[nt:nt+4]==b'PE\0\0'
count=u16(nt+6);optional=nt+24;assert u16(optional)==0x10b
sections=optional+u16(nt+20)
def offset(rva):
 if rva<u32(optional+60):assert rva<len(b);return rva
 for i in range(count):
  s=sections+i*40;va=u32(s+12);rawsize=u32(s+16);raw=u32(s+20)
  if va<=rva<va+rawsize:
   o=raw+rva-va;assert o<len(b);return o
 raise ValueError('RVA outside backed file')
def cstring(o):
 end=b.index(0,o,min(o+1024,len(b)));return b[o:end].decode('ascii')
imports={};descriptor=offset(u32(optional+104))
for d in range(128):
 o=descriptor+20*d;original,stamp,forward,name,first=struct.unpack_from('<5I',b,o)
 if not any((original,stamp,forward,name,first)):break
 dll=cstring(offset(name));assert dll not in imports
 thunks=offset(original or first);names=[]
 for i in range(4096):
  entry=u32(thunks+i*4)
  if not entry:break
  names.append('#'+str(entry&65535) if entry&0x80000000 else cstring(offset(entry)+2))
 else:raise ValueError('Unterminated thunk table')
 imports[dll]=names
else:raise ValueError('Unterminated import table')
assert imports==expected
r=dict(completed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),retail_sha256=h,retail_bytes=len(b),pe32=True,independent_table_walk_agrees=True,imports=imports,physical_access=False,runtime_launched=False,game_modified=False,limits='On-disk import metadata only. Sparse imports and loader APIs do not establish calls executed at runtime, rendering path, acceleration or performance. Absence of a named DirectDraw import is not proof of its absence at runtime.',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
out=K/'import-inventory001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(dlls=len(imports),imports=sum(map(len,imports.values())),independent_agreement=True)))
