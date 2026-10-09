"""Actual compiled NT5 imports/residency and matched114 definition review."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();dest=k/'driver-review.json';assert not dest.exists()
b=read(k/'build-report.json');s=read(k/'source-review.json');host=read(k/'host-tests.json')
assert b['status']=='compiled' and b['parent_tree']==s['parent_tree'] and b['patch_sha256']==sha(k/'0114-bounded-dib-copy.patch')==s['patch_sha256']
assert host['passed'] and host['checks']==321785
for n,h in host['pins'].items():assert sha(k/n)==h,n
for n,h in s['source_files'].items():assert sha(k/'display'/n)==h,n
a,z=[v['definitions'] for v in b['builds']]
assert {n for n in a if a[n]!=z[n]}=={'XWN_DIB_FASTPATH'} and a['XWN_DIB_FASTPATH']=='OFF' and z['XWN_DIB_FASTPATH']=='ON'
assert all(v['source_tree']==b['source_tree'] for v in b['builds'])
tool='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/'
actual=ws/'outputs/video-physical-rehearsal160/artifacts/F/winnt/system32/win32k.sys';provider=pefile.PE(str(actual))
exports={v.name.decode():v for v in provider.DIRECTORY_ENTRY_EXPORT.symbols if v.name};reports=[]
for row in b['builds']:
 p=k/row['case']/'artifacts/xwnown.dll';assert sha(p)==row['files'][0]['sha256'];pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c
 imports={}
 for entry in pe.DIRECTORY_ENTRY_IMPORT:
  name=entry.dll.decode().lower();assert name=='win32k.sys'
  names=[v.name.decode() for v in entry.imports];assert all(n in exports and not exports[n].forwarder for n in names)
  imports[name]=names
 assert {'EngAcquireSemaphore','EngReleaseSemaphore','EngBitBlt','EngCopyBits'}<=set(imports['win32k.sys'])
 posix='/mnt/c/'+str(p).replace('\\','/')[3:]
 nm=subprocess.check_output(['wsl','-d','Ubuntu','--',tool+'i686-w64-mingw32-nm',posix],text=True,stderr=subprocess.DEVNULL)
 names=['_XwnDibRecord','_XwnDibSnapshot','_XwnBitBlt@44','_XwnCopyBits@24'];sites=[]
 for name in names:
  hit=re.search(r'^([0-9a-fA-F]+) [Tt] '+re.escape(name)+r'$',nm,re.M);assert hit,name
  address=int(hit.group(1),16);rva=address-pe.OPTIONAL_HEADER.ImageBase;section=pe.get_section_by_rva(rva)
  assert section and section.Characteristics&0x08000000 and section.Characteristics&0x20000000
  sites.append(dict(name=name,address=address,rva=rva,section=section.Name.rstrip(b'\0').decode(),bytes=pe.get_data(rva,32).hex()))
 dis=subprocess.check_output(['wsl','-d','Ubuntu','--',tool+'i686-w64-mingw32-objdump','-d',posix],text=True,stderr=subprocess.DEVNULL)
 (k/(row['case']+'-disassembly.txt')).write_bytes(dis.encode())
 # Both builds must retain the engine fallback imports. Only enabled build
 # includes row planner/copy code, proven additionally by live coverage later.
 reports.append(dict(case=row['case'],sha256=sha(p),bytes=p.stat().st_size,imports=imports,resident_sites=sites,source_tree=row['source_tree']))
dest.write_text(json.dumps(dict(passed=True,source_tree=b['source_tree'],only_definition_difference='XWN_DIB_FASTPATH',actual_nt5_imports_checked=True,ordinary_qualified=False,physical_qualified=False,provider_sha256=sha(actual),builds=reports,host_checks=host['checks'],limits='Compiled imports/resident code only; no runtime/pixel/performance qualification. Static unused-header warnings retained.'),indent=2)+'\n')
print('Matched114 imports/residency reviewed; runtime coverage still required')
