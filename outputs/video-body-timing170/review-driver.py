"""Actual compiled imports/residency and matched113 source/definition review."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();dest=k/'driver-review.json';assert not dest.exists()
b=read(k/'build-report.json');s=read(k/'source-review.json');host=read(k/'host-tests.json')
assert b['status']=='compiled' and b['parent_tree']==s['parent_tree'] and b['patch_sha256']==sha(k/'0113-body-timing.patch')==s['patch_sha256']
assert host['passed'] and host['checks']==4142
for n,d in host['pins'].items():assert sha(k/n)==d,n
for n,d in s['source_files'].items():assert sha(k/'display'/n)==d,n
control,candidate=b['builds'];a,z=control['definitions'],candidate['definitions']
assert {n for n in a if a[n]!=z[n]}=={'XWN_BODY_PROFILE'} and a['XWN_BODY_PROFILE']=='OFF' and z['XWN_BODY_PROFILE']=='ON'
assert control['source_tree']==candidate['source_tree']==b['source_tree']
tool='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/'
actual=ws/'outputs/video-physical-rehearsal160/artifacts/F/winnt/system32';provider=pefile.PE(str(actual/'win32k.sys'))
exports={v.name.decode():v for v in provider.DIRECTORY_ENTRY_EXPORT.symbols if v.name};reports=[]
for row in b['builds']:
 p=k/row['case']/'artifacts/xwnown.dll';assert sha(p)==row['files'][0]['sha256'];pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c
 imports={}
 for entry in pe.DIRECTORY_ENTRY_IMPORT:
  name=entry.dll.decode().lower();assert name=='win32k.sys',name
  names=[v.name.decode() for v in entry.imports];assert all(n in exports and not exports[n].forwarder for n in names),names
  imports[name]=names
 assert {'EngQueryPerformanceCounter','EngQueryPerformanceFrequency','EngAcquireSemaphore','EngReleaseSemaphore'}<=set(imports['win32k.sys'])
 posix='/mnt/c/'+str(p).replace('\\','/')[3:]
 nm=subprocess.check_output(['wsl','-d','Ubuntu','--',tool+'i686-w64-mingw32-nm',posix],text=True,stderr=subprocess.DEVNULL)
 names=['_XwnProfileStart','_XwnProfileEnd','_XwnProfileInit','_XwnProfileSnapshot','_XwnUploadBox','_XwnUploadInternal','_XwnBitBlt@44','_XwnCopyBits@24'];sites=[]
 for name in names:
  hit=re.search(r'^([0-9a-fA-F]+) [Tt] '+re.escape(name)+r'$',nm,re.M);assert hit,name
  address=int(hit.group(1),16);rva=address-pe.OPTIONAL_HEADER.ImageBase
  section=pe.get_section_by_rva(rva);assert section and section.Characteristics&0x08000000 and section.Characteristics&0x20000000
  sites.append(dict(name=name,address=address,rva=rva,section=section.Name.rstrip(b'\0').decode(),bytes=pe.get_data(rva,32).hex()))
 dis=subprocess.check_output(['wsl','-d','Ubuntu','--',tool+'i686-w64-mingw32-objdump','-d','--disassemble=_XwnProfileStart',posix],text=True,stderr=subprocess.DEVNULL)
 (k/(row['case']+'-clock-disassembly.txt')).write_text(dis)
 reports.append(dict(case=row['case'],sha256=sha(p),bytes=p.stat().st_size,imports=imports,resident_sites=sites,source_tree=row['source_tree']))
r=dict(passed=True,source_tree=b['source_tree'],only_definition_difference='XWN_BODY_PROFILE',actual_nt5_imports_checked=True,
 clock_runtime_qualified=False,ordinary_qualified=False,physical_qualified=False,provider_sha256=sha(actual/'win32k.sys'),builds=reports,
 host_arithmetic_checks=4142,limits='Compiled resident code/import evidence only. Unused static-header-function warnings retained; no timer/runtime or performance qualification.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Matched113 imports/resident symbols reviewed, runtime timer unverified')
