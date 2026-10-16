"""Assemble the new utility preview only; no Windows/firmware/private input."""
import hashlib,json,pathlib,posixpath,re,shutil,struct,subprocess,sys
K=pathlib.Path(__file__).resolve().parent;W=K.parent.parent
sys.path.insert(0,str(W/'tools'));import tester_bundle as bundle
stage=W/'work/tester417-utilities001';archive=pathlib.Path('E:/xwn417/xwn-utilities-preview-417.zip')
assert not stage.exists() and not archive.exists()
assert shutil.disk_usage('C:/').free-40*1024**2>=20*1024**3
assert shutil.disk_usage('E:/').free-16*1024**2>=20*1024**3
build=json.loads((K/'build002.json').read_text());native=pathlib.Path(build['output'])
sha=lambda b:hashlib.sha256(b).hexdigest()
assert build['compiled'] and build['sdk_unchanged'] and json.loads((K/'smoke002.json').read_text())['report_scope_passed']
def put(name,data):
 p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
for name in ('main.c','Makefile'):
 data=(native/name).read_bytes();assert sha(data)==build['sources'][name]
 put('source/hardware-report/'+name,data)
xbe=(native/'bin/default.xbe').read_bytes();assert sha(xbe)==build['outputs']['bin/default.xbe']['sha256']
assert xbe[:4]==b'XBEH'
base=struct.unpack_from('<I',xbe,0x104)[0];count=struct.unpack_from('<I',xbe,0x11c)[0];at=struct.unpack_from('<I',xbe,0x120)[0]-base
sections=[]
for i in range(count):
 flags,va,size,raw,n,name,refs,head,tail=struct.unpack_from('<9I',xbe,at+56*i)
 assert raw+n<=len(xbe) and n<=size
 label=xbe[name-base:xbe.index(b'\0',name-base)].decode()
 sections.append(dict(name=label,bytes=n,sha256=sha(xbe[raw:raw+n])))
pe=(native/'main.exe').read_bytes();peoff=struct.unpack_from('<I',pe,60)[0]
assert pe[peoff:peoff+4]==b'PE\0\0' and struct.unpack_from('<II',pe,peoff+24+96)==(0,0)
put('E/Applications/XWNInfo/default.xbe',xbe)
for name in ('tester_bundle.py','hardware_report.py','fatx_names.py'):
 put('host/'+name,(W/'tools'/name).read_bytes())
for name in ('testers.md','tester-bundles.md','tester-report-template.md'):
 text=(W/'docs'/name).read_text(encoding='utf-8-sig')
 def link(m):
  target=m[2]
  if '://' in target or target.startswith('#'):return m[0]
  return '['+m[1]+'](https://github.com/PaulMDemers/xbox-windows-native/blob/main/'+posixpath.normpath('docs/'+target)+')'
 text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,text)
 put('docs/'+name,text.encode())
put('licenses/project-MIT.txt',(W/'LICENSE').read_bytes())
sdk=pathlib.Path('C:/nxdk')
head=subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD']).decode().strip();assert head==build['sdk_head']
assert not subprocess.check_output(['git','-C',str(sdk),'status','--porcelain','-uno']).strip()
paths=subprocess.check_output(['git','-C',str(sdk),'ls-files','--recurse-submodules','-z','lib','LICENSES']).decode().split('\0')
roots=('lib/hal/','lib/nxdk/','lib/winapi/','lib/xboxrt/','lib/xboxkrnl/','lib/pdclib/','lib/usb/','lib/net/','lib/pbkit/','lib/zlib/','lib/libpng/','lib/libjpeg/','LICENSES/')
sdkfiles=[]
for name in paths:
 p=sdk/name
 if not name.startswith(roots) or not p.is_file() or p.is_symlink():continue
 data=p.read_bytes()
 if b'\0' in data or p.suffix.lower() in ('.svg','.jpg','.png','.html','.pdf','.map'):continue
 dest=('licenses/nxdk/'+name[9:]) if name.startswith('LICENSES/') else 'source/nxdk/'+name
 put(dest,data);sdkfiles.append(name)
submodules=subprocess.check_output(['git','-C',str(sdk),'submodule','status','--recursive']).decode()
put('source/nxdk-submodules.txt',submodules.encode())
put('source/nxdk/.gitmodules',(sdk/'.gitmodules').read_bytes())
put('source/nxdk/Makefile',(sdk/'Makefile').read_bytes())
identity=dict(schema=1,tool='xwn-hardware-report-1',sdk_repository='https://github.com/XboxDev/nxdk',sdk_commit=head,
 source_sha256=build['sources'],xbe_sha256=sha(xbe),xbe_bytes=len(xbe),sections=sections,
 sdk_library_sha256={n:h for n,h in build['sdk_before'].items() if n.endswith('.lib')},
 evidence='Build002 and smoke002: emulator report/cold FATX allocation passed; physical test pending.',
 limitations='Prebuilt SDK libraries, not a full SDK rebuild. Source subset preserves linked-library source/notices; images/examples/tool executables omitted. No Windows, firmware, EEPROM or private recovery data.')
put('source/build-identity.json',(json.dumps(identity,indent=2)+'\n').encode())
put('licenses/NOTICE.txt',b'''XWN Hardware Report: original MIT code; see project-MIT.txt.
nxdk revision 58427c078b4ccb0121f359b6b6c536b3b2914976 and pinned submodules:
https://github.com/XboxDev/nxdk
The exact source files under source/nxdk retain individual copyright/license notices.
Applicable SDK license texts are under licenses/nxdk and alongside submodule sources,
including PDCLib COPYING.CC0, lwIP COPYING, and the image/USB library notices.
Including source does not relicense it under the project MIT license.
No shader compiler, proprietary firmware, Windows files or console keys included.
''')
put('README.txt',b'''XWN utilities preview 417 -- physical qualification pending

1. Read docs/testers.md and docs/tester-report-template.md.
2. Verify this ZIP: python host/tester_bundle.py verify PATH_TO_ZIP
   Also compare its outer SHA-256 with the maintainer's separate checksum.
3. FTP only E/Applications/XWNInfo to Xbox E:\\Applications\\XWNInfo.
   Do not overwrite an existing folder. Leave Xbox C and existing Apps alone.
4. Use UnleashX File Explorer: E:\\Applications\\XWNInfo\\default.xbe
5. Retrieve E:\\xwn-report-00.json (or next unused number) after return.
6. Check: python host/hardware_report.py xwn-report-00.json

This utility inventories hardware; it does not install or boot Windows.
Windows bundle preparation and physical validation remain separate.
No EEPROM contents, keys, serial numbers, firmware or Windows payload included.
The XBE passed an emulator smoke test; other hardware revisions are unqualified.
Keep docs/host/source/licenses on your PC. No flashing, partitioning or menu edit.
''')
m=bundle.collect(stage,'utilities');plan=K/'utilities-plan001.json';plan.write_text(json.dumps(m,indent=2)+'\n')
h=bundle.build(stage,plan,archive)
(archive.parent/(archive.name+'.sha256')).write_text(h+'  '+archive.name+'\n')
r=dict(archive=str(archive),sha256=h,bytes=archive.stat().st_size,files=len(m['files']),directories=len(m['directories']),
 logical_bytes=sum(x['bytes'] for x in m['files']),xbe_sha256=sha(xbe),sdk_text_files=len(sdkfiles),
 readback_verified=True,physical_access=False,windows_included=False,public_upload=False)
(K/'bundle001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
