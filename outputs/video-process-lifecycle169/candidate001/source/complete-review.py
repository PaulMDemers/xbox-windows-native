"""Add actual caller provenance and DDK/timing import evidence before freeze."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
p=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/umpnpmgr.dll');dst=k/'artifacts/umpnpmgr.dll'
assert not dst.exists() and sha(p)=='02fd896d3f2318a3bd624dd1357ec1f66ea67553ef96c602bede7c4ec5bef685';shutil.copyfile(p,dst);assert sha(dst)==sha(p)
pe=pefile.PE(str(dst));r=read(k/'sites.json');r['binaries']['umpnpmgr.dll']=dict(path=str(dst.relative_to(ws)).replace('\\','/'),sha256=sha(dst),preferred_base=pe.OPTIONAL_HEADER.ImageBase,timestamp=pe.FILE_HEADER.TimeDateStamp,image_size=pe.OPTIONAL_HEADER.SizeOfImage,
    provenance='Owned immutable0.1.0 file; new cold fixture preflight must match actual guest bytes, not assumed by same name')
r['dependency_pins']={str(p.relative_to(ws)).replace('\\','/'):sha(p) for p in [k.parent/'native-windows-nt5-kernel/process-layouts.json',k.parent/'native-windows-nt5-kernel/kernel-publics.json',k.parent/'native-windows-nt5-kernel/trace-entry.py',k.parent/'native-windows-prebuild/monitor_capture.py']}
(k/'sites.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
header='/home/paul/xbox-windows-native/build/video-reuse-001/source/sdk/include/psdk/winddi.h'
cmd=['wsl','-d','Ubuntu','--','python3','-c',"from pathlib import Path; import hashlib,json; p=Path('"+header+"'); s=p.read_text(); lines=s.splitlines(); print(json.dumps(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),declarations=[dict(line=i+1,source='\\n'.join(lines[i-3:i+3])) for i,v in enumerate(lines) if v.startswith('EngQueryPerformance')]),indent=2))"]
declarations=json.loads(subprocess.check_output(cmd));assert len(declarations['declarations'])==2
t=read(k/'timing-interface.json');pe=pefile.PE(str(ws/t['captured_win32k_path']))
iat=0xa01647c8;imports=[dict(dll=e.dll.decode(),name=v.name.decode() if v.name else None,iat=v.address) for e in pe.DIRECTORY_ENTRY_IMPORT for v in e.imports if v.address==iat]
assert len(imports)==1 and imports[0]['name']=='KeQueryPerformanceCounter'
t.update(nt5_source_contract_checked=True,ddk_declarations=declarations,actual_common_import=imports[0],runtime_contract_checked=False)
(k/'timing-interface.json').write_text(json.dumps(t,indent=2)+'\n',encoding='utf-8')
print('Owned caller pin and actual64-bit-output/stdcall DDK timing signatures reviewed')
