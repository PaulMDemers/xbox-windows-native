"""Pin new helpers and actual COFF/provider/kernel symbols before mutation."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(pe):
 data=pe.__data__;pos=pe.FILE_HEADER.PointerToSymbolTable;n=pe.FILE_HEADER.NumberOfSymbols;strings=pos+18*n;i=0;r={}
 while i<n:
  raw,value,section,typ,cls,aux=struct.unpack_from('<8sIhHBB',data,pos+18*i)
  if raw[:4]==b'\0'*4:
   off=struct.unpack_from('<I',raw,4)[0];start=strings+off;name=data[start:data.find(b'\0',start)].decode('ascii')
  else:name=raw.rstrip(b'\0').decode('ascii')
  if section>0:r[name]=pe.sections[section-1].VirtualAddress+value
  i+=1+aux
 return r
r={'scope':__doc__,'physical_access':False,'helpers':{},'providers':{}}
for n in ['probe.exe','trigger.sys']:
 p=k/'artifacts'/n;pe=pefile.PE(str(p));imports={d.dll.decode():[e.name.decode() if e.name else e.ordinal for e in d.imports] for d in pe.DIRECTORY_ENTRY_IMPORT}
 assert pe.OPTIONAL_HEADER.MajorSubsystemVersion==5 and pe.OPTIONAL_HEADER.MinorSubsystemVersion==0
 assert set(imports)<={'KERNEL32.dll','ADVAPI32.dll','ntoskrnl.exe'}
 if n=='trigger.sys':
  assert 'KeBugCheckEx' in imports['ntoskrnl.exe'];assert not any(s.Name.startswith((b'PAGE',b'INIT')) for s in pe.sections)
 r['helpers'][n]={'sha256':sha(p),'bytes':p.stat().st_size,'imports':imports,'symbols':symbols(pe)}
previous=json.loads((ws/'outputs/video-boot-layout219/build-review.json').read_text())
for case in ['control001','candidate001']:
 p=ws/'outputs/video-boot-layout219/artifacts/build001'/case/'xboxbvid.dll';pe=pefile.PE(str(p));s=symbols(pe)
 assert sha(p)==previous['binaries'][case]['sha256']
 required=['_FrameBufferStart','_BackBuffer','_Owner','_References','_Ready','_Published','_ResetDisplay']
 assert all(n in s for n in required)
 r['providers'][case]={'sha256':sha(p),'timestamp':pe.FILE_HEADER.TimeDateStamp,'image_size':pe.OPTIONAL_HEADER.SizeOfImage,'symbols':s,'exports':previous['binaries'][case]['exports']}
kernel=ws/'outputs/video-upload-runtime211/artifacts/F/winnt/system32/ntoskrnl.exe';r['kernel_sha256']=sha(kernel)
r['passed']=True
dest=k/'review.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':True,'helpers':{n:v['sha256'] for n,v in r['helpers'].items()}}))
