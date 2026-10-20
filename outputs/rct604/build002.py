"""Build original NT5 tracer controls, pin sources, headers, compiler and IAT."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn604/build002')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
sys.path.insert(0,str(K.parents[1]/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists()
out=K/'build002.json';assert not out.exists()
space=require_space('/mnt/c',20.02)
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
O.mkdir(parents=True)
for f in list(K.glob('*.c'))+list(K.glob('*.h')):shutil.copyfile(f,O/f.name)
(O/'fixture.def').write_text('EXPORTS\nprobe601 @7\nprobe_dib604 @9\n')
r=dict(status='building',compiler_sha256=sha(cc),space=space,physical_access=False,commands=[],headers={},rows=[])
def save():out.write_text(json.dumps(r,indent=2)+'\n')
def build(src,exe,dll=False):
 cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_DllMain@12' if dll else '-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-MD','-MF',exe+'.d','-o',exe,src]
 cmd+=['-shared','fixture.def'] if dll else []
 cmd+=['-lkernel32','-luser32','-ladvapi32','-lgdi32'];r['commands'].append(cmd);save()
 with (O/(exe+'.log')).open('wb') as log:subprocess.run(cmd,cwd=O,check=True,stdout=log,stderr=log,timeout=180)
 deps=(O/(exe+'.d')).read_text().replace('\\\n','').split(': ',1)[1].split()
 r['headers'].update({n:sha(n) for n in sorted(set(deps)) if Path(n).is_absolute()})
 r['rows'].append(dict(path=str(O/exe),sha256=sha(O/exe),bytes=(O/exe).stat().st_size));save()
try:
 build('fixture.c','fixture.dll',True);build('subject002.c','subject.exe')
 pe=pefile.PE(str(O/'subject.exe'));iat={v.name.decode():v.address for d in pe.DIRECTORY_ENTRY_IMPORT for v in d.imports if v.name and v.name in [b'LoadLibraryA',b'GetProcAddress']}
 assert len(iat)==2 and pe.FILE_HEADER.Machine==0x14c
 r['target_iat']=iat;r['target_image_base']=pe.OPTIONAL_HEADER.ImageBase;r['target_image_size']=pe.OPTIONAL_HEADER.SizeOfImage
 (O/'target_iat.h').write_text('#define IAT_LOAD601 0x%xu\n#define IAT_PROC601 0x%xu\n'%(iat['LoadLibraryA'],iat['GetProcAddress']))
 build('trace.c','trace.exe');build('runner002.c','run604.exe');r.update(status='compiled',exit_code=0)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
 r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
