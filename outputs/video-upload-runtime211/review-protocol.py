"""Prelaunch wrapper/syntax/version review, final frozen manifest; no guest access."""
import ast,hashlib,json,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'protocol-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
original=k.parent/'video-surface-history/Invoke-Exclusive.ps1';s=original.read_text()
s=s.replace('$run = Join-Path $workspace "work\\runs\\$RunId"','$run = Join-Path "E:/Codex-private-artifacts/xbox-windows-feasibility/upload211-runs" $RunId')
s=s.replace("(Join-Path $workspace 'work\\scratch')","'E:/Codex-private-artifacts/xbox-windows-feasibility/upload211-scratch'")
s=s.replace("& (Join-Path $integration 'with_xbox_resource.ps1') -Resource xemu -Action {",'& {')
assert s==(k/'Invoke-211.ps1').read_text(),'Only fresh E roots and lease acquired outside wrapper may differ'
run=(k/'Run.ps1').read_text();assert run.index('-Resource build -Action')<run.index('-Resource xemu -Action')<run.index('@{utc=')<run.index('Invoke-211.ps1')
assert '(Get-PSDrive C).Free -lt 20GB' in run and '(Get-PSDrive E).Free - (Get-Item -LiteralPath $seed).Length' in run
for p in k.glob('*.py'):ast.parse(p.read_text())
for n in ['sample_analysis.py','text_analysis.py']:assert 'VERSION' in (k/n).read_text() and ("'12','256','128'" if n.startswith('sample') else "'VERSION',12".replace("'VERSION'","'XWN_GDI_PROBE_VERSION'")) in (k/n).read_text()
ps="""$fail=@();Get-ChildItem -LiteralPath '%s' -Filter *.ps1|ForEach-Object{$t=$null;$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$t,[ref]$e);if($e){$fail+=$e}};if($fail){$fail;exit 1}"""%k.as_posix()
subprocess.run(['pwsh','-NoProfile','-Command',ps],check=True)
# Preserve the original host freeze made before compare/parser protocol review.
before=k/'artifacts/prelaunch-freeze001.json';assert not before.exists();shutil.copyfile(k/'emulator-frozen.json',before)
old=read(k/'emulator-frozen.json')
changed={n:dict(before=h,after=sha(ws/n)) for n,h in old.items() if sha(ws/n)!=h}
assert set(changed)=={(k/n).relative_to(ws).as_posix() for n in ['text_analysis.py','create-kit.py']},changed
r=dict(passed=True,physical_access=False,guest_launch=False,canonical_sha256=sha(original),wrapper_sha256=sha(k/'Invoke-211.ps1'),
 allowed_wrapper_changes=['fresh E run root','fresh E scratch root','external xemu lease acquired before any run creation'],
 python_and_powershell_syntax_passed=True,prelaunch_parser_version_correction=changed,prior_freeze_sha256=sha(before),
 source_pins={p.name:sha(p) for p in k.glob('*.py')})
dest.write_text(json.dumps(r,indent=2)+'\n')
pins=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))+[dest,k/'build-review.json',k/'probe-build001.json',k/'upload-parser-tests.json']+list((k/'artifacts').glob('*.exe'))
native=k.parent/'video-upload-accounting210'
pins+=[native/c/'artifacts/xwnown.dll' for c in ['control001','candidate001']]+[native/'build-review.json',native/'source-review.json',native/'host-tests001.json',k.parent/'video-phase-physical200/package-review.json']
(k/'emulator-frozen.json').write_text(json.dumps({p.relative_to(ws).as_posix():sha(p) for p in pins},indent=2)+'\n')
print('Protocol/canonical wrapper/syntax/final prelaunch source pins PASS')
