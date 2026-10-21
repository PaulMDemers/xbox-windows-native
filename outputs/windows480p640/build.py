import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['build001']
import os
assert os.environ.get('XWN_BUILD_LEASE')=='held'
sys.path.insert(0,str(k.parents[1]/'tools'));from build_space import require_space
space=require_space('/mnt/c',20.01)
out=Path('/mnt/c/xwn640')/case;out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cc=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
assert sha(cc)=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
pins={}
for name in ['probe.c']:
    data=(k/name).read_bytes();(out/name).write_bytes(data);pins[name]=sha(out/name)
command=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin',
         '-Wno-misleading-indentation','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0',
         '-o',str(out/'probe.exe'),str(out/'probe.c'),'-lkernel32','-luser32','-ladvapi32','-lgdi32','-lddraw']
run=subprocess.run(command,capture_output=True,text=True)
(out/'stdout.txt').write_text(run.stdout);(out/'stderr.txt').write_text(run.stderr)
r={'space':space,'compiled':run.returncode==0,'returncode':run.returncode,'command':command,'source_pins':pins,
   'compiler_sha256':sha(cc),'compiler_version':subprocess.check_output([str(cc),'--version'],text=True),
   'output_linux':str(out/'probe.exe'),'output_windows':'C:'+str(out/'probe.exe')[6:],
   'physical_access':False,'guest_launched':False,'warnings':run.stderr}
if run.returncode==0:r['binary_sha256']=sha(out/'probe.exe')
(k/(case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r));sys.exit(run.returncode)
