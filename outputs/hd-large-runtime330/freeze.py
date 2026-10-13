"""Preflight syntax, exact inherited source pins and all invoked host helpers."""
import ast,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (K/'emulator-frozen.json').exists()
old=json.loads((K.parent/'hd-emulator323/emulator-frozen.json').read_text())
for name,h in old.items():assert sha(W/name)==h,name
files=[W/n for n in old]
files+=list(K.glob('*.py'))+list(K.glob('*.ps1'))+list(K.glob('*.md'))
files+=[K/'emu001/fixture.json',K/'source-review.json',K.parent/'artifact-recovery329/seed001/fixture.json',K.parent/'artifact-recovery329/seed001/content-review002.json']
files+=list((K.parent/'hd-large327').glob('*.py'))+list((K.parent/'hd-large327').glob('*.c'))+list((K.parent/'hd-large327').glob('*.h'))
files+=[K.parent/'hd-large327/build-review003.json',K.parent/'hd-large327/parser001.json']
for p in files:
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
ps=Path('C:/Users/Paul/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe')
script="param($Root)\n$ErrorActionPreference='Stop'\nGet-ChildItem -LiteralPath $Root -Filter '*.ps1' | ForEach-Object {$t=$null;$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$t,[ref]$e);if($e.Count){throw ($e | Out-String)}}\n'PowerShell syntax passed'\n"
check=Path('E:/xwn330/preflight001.ps1');assert not check.exists();check.parent.mkdir(exist_ok=True);check.write_text(script)
subprocess.run([str(ps),'-NoProfile','-File',str(check),str(K)],check=True)
pins={p.relative_to(W).as_posix():sha(p) for p in files}
host=json.loads((K.parent/'hd-emulator323/host-frozen.json').read_text())
for p,h in host.items():assert sha(Path(p))==h,p
for p in ['E:/xwn329/retained-builds001/xemu-hd322.exe','E:/xwn327/build003/replay.exe','C:/Emulators/xemu/system/bios/Complex_4627.bin','C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin',str(W/'outputs/native-windows-extended-storage/artifacts/f-boot-length-004.iso')]:host[p]=sha(Path(p))
(K/'emulator-frozen.json').write_text(json.dumps(pins,indent=2)+'\n')
(K/'host-frozen.json').write_text(json.dumps(host,indent=2)+'\n')
(K/'preflight001.json').write_text(json.dumps(dict(passed=True,inherited_pins=len(old),source_pins=len(pins),host_pins=len(host),python_syntax=True,powershell_syntax=True,physical_access=False),indent=2)+'\n')
print('Frozen',len(pins),'source and',len(host),'host/media pins')
