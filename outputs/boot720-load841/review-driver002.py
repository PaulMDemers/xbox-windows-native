"""Validate diagnostic imports and resident crash-report routines against owned NT5."""
import hashlib,json,struct,sys,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn841')
sys.path.insert(0,str(W/'work/python-packages'));import pefile
sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text())
out=K/'driver-review002.json';assert not out.exists();r={'passed':False,'physical_access':False}
try:
 build=read(K/'driver003.json');assert build['passed'];data=(P/'driver003/xwnfatx.sys').read_bytes();assert sha(data)==build['artifacts']['xwnfatx.sys']['sha256']
 pkg=read(W/'outputs/boot720-native835/package001.json');archive=Path('E:/xwn343/bundle002/stock-e-1080i-001.zip');assert sha(archive.read_bytes())==pkg['archive_sha256']
 providers={}
 with zipfile.ZipFile(archive) as z:
  for mod,key in [('ntoskrnl.exe','/E/winnt/system32/ntoskrnl.exe'),('hal.dll','/E/Applications/XWN16Boot835/loader/halxboxnt5.dll')]:
   meta=pkg['files'][key];b=z.read('payload'+meta['archive_path']);assert sha(b)==meta['sha256'];pe=pefile.PE(data=b)
   providers[mod]={'sha256':sha(b),'exports':{v.name.decode() for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name and not v.forwarder}}
 pe=pefile.PE(data=data);assert pe.FILE_HEADER.Machine==0x14c
 r['imports']={};r['providers']={m:v['sha256'] for m,v in providers.items()}
 for dll in pe.DIRECTORY_ENTRY_IMPORT:
  name=dll.dll.decode().lower();assert name in providers
  names=[v.name.decode() for v in dll.imports];assert all(n in providers[name]['exports'] for n in names);r['imports'][name]=names
 count=pe.FILE_HEADER.NumberOfSymbols;start=pe.FILE_HEADER.PointerToSymbolTable;strings=start+18*count;i=0;syms={}
 while i<count:
  raw,value,section,ty,cls,aux=struct.unpack_from('<8sIhHBB',data,start+18*i)
  if raw[:4]==bytes(4):at=strings+struct.unpack_from('<I',raw,4)[0];name=data[at:data.index(b'\0',at)].decode()
  else:name=raw.split(b'\0')[0].decode()
  if '841' in name and section>0:
   sec=pe.sections[section-1];syms[name]={'rva':sec.VirtualAddress+value,'section':sec.Name.rstrip(b'\0').decode(),'characteristics':hex(sec.Characteristics)}
   assert not sec.Name.startswith(b'PAGE') and not sec.Characteristics&0x02000000
  i+=1+aux
 assert any('callback841' in n for n in syms) and any('Cache841Initialize' in n for n in syms)
 r['resident_diagnostic_symbols']=syms;r['driver_sha256']=sha(data);r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n');print('841 imports/residency review:',r['passed'])
