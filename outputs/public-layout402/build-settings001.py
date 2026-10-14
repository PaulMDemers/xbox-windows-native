import hashlib,json,subprocess,shlex
from pathlib import Path
root=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
out=Path('/home/paul/xbox-windows-native/build/public-layout402-settings001')
assert not out.exists()
out.mkdir()
r=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
source=root/'src/utilities/display-settings/settings.c'
cmd=[str(r/'i386/bin/i686-w64-mingw32-gcc'),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wno-misleading-indentation','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-o',str(out/'display-settings.exe'),str(source),'-lkernel32','-luser32','-ladvapi32']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(r/'i386/bin/i686-w64-mingw32-gcc')==json.loads((root/'upstream/components.json').read_text())['rosbe_tool_pins']['i386/bin/i686-w64-mingw32-gcc']
with (out/'build.log').open('w') as log:
    result=subprocess.run([str(r/'RosBE.sh'),str(out),'0','i386'],input='set -e\n'+shlex.join(cmd)+'\n',text=True,stdout=log,stderr=subprocess.STDOUT,timeout=120)
record={'command':cmd,'source_sha256':sha(source),'compiler_sha256':sha(r/'i386/bin/i686-w64-mingw32-gcc'),'exit_code':result.returncode,'output':str(out)}
if result.returncode==0:
    record['artifact']={'file':'display-settings.exe','bytes':(out/'display-settings.exe').stat().st_size,'sha256':sha(out/'display-settings.exe')}
(root/'outputs/public-layout402/settings-build001.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
raise SystemExit(result.returncode)
