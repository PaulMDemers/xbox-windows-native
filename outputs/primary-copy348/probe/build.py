import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['build001']
out=Path('/mnt/e/xwn348/probe')/case;out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cc=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
assert sha(cc)=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
pins={}
for name in ['gdi-probe.c','text-cases.c','large_cases.c','large_oracle.h']:
    data=(k/name).read_bytes();(out/name).write_bytes(data);pins[name]=sha(out/name)
command=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin',
         '-Wno-misleading-indentation','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0',
         '-o',str(out/'replay.exe'),str(out/'gdi-probe.c'),'-lkernel32','-luser32','-lgdi32']
run=subprocess.run(command,capture_output=True,text=True)
(out/'stdout.txt').write_text(run.stdout);(out/'stderr.txt').write_text(run.stderr)
r={'compiled':run.returncode==0,'returncode':run.returncode,'command':command,'source_pins':pins,
   'compiler_sha256':sha(cc),'compiler_version':subprocess.check_output([str(cc),'--version'],text=True),
   'output_linux':str(out/'replay.exe'),'output_windows':'E:'+str(out/'replay.exe')[6:],
   'physical_access':False,'guest_launched':False,'warnings':run.stderr}
if run.returncode==0:r['binary_sha256']=sha(out/'replay.exe')
(k/(case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r));sys.exit(run.returncode)
