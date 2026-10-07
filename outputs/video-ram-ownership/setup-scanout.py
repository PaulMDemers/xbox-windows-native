"""New diagnostic child only after strict ordinary pair PASS; no old case reuse."""
from pathlib import Path
import json,shutil
p=Path(__file__).resolve().parent;k=p.parent/'video-ownership-scanout';old=p.parent/'video-ram-scanout3'
assert json.loads((p/'pair-review.json').read_text())['passed'];k.mkdir(exist_ok=False)
for name in ['display','tests']:shutil.copytree(p/name,k/name)
for name in ['0109-ram-ownership.patch','patch-review.json','build-report.json','source-verification.json','host-tests.json','ownership-tests.json','lifecycle-tests.json','tests-body.c','ownership-tests.c','lifecycle-tests.c']:
 shutil.copyfile(p/name,k/name)
(k/'candidate001/artifacts').mkdir(parents=True)
for name in ['xwnown.dll']:shutil.copyfile(p/'candidate001/artifacts'/name,k/'candidate001/artifacts'/name)
shutil.copyfile(p/'candidate001/build.json',k/'candidate001/build.json');(k/'artifacts').mkdir()
for name in ['atomic_json.py','audit.py','configuration.py','cold-map.py','preflight.py','Run.ps1','supervise.py','record-closure.py','common.py','prepare.py','review.py','Build-Probe.ps1','probe.c']:
 s=(p/name).read_text().replace('video-ram-ownership','video-ownership-scanout').replace('nt5-vown-','nt5-vownscan-').replace('xwnown116','xwnownscan117')
 if name in ['common.py','probe.c']:s=s.replace('116','117')
 if name in ['preflight.py','audit.py']:s=s.replace('debugger=False','debugger=True')
 if name=='audit.py':s+="\nr=read(out/'audit.json');r['ordinary_qualified']=False;r['limits']='Debugger diagnostic; independent physical-buffer verification separate.';save(out/'audit.json',r)\n"
 if name=='supervise.py':s=s.replace('for cycle in [1]:',"assert (k/'trace-armed.signal').exists(), 'Observer must be armed'\nfor cycle in [1]:")
 if name=='common.py':s=s.replace('        for size,',"        take('CURSOR_PARKED',[1000,550,0])\n        for size,")
 if name=='probe.c':
  reference=(old/'probe.c').read_text();a=reference.index('__declspec(dllexport)');b=reference.index('\n\ntypedef',a)
  start=s.index('__declspec(dllexport)');end=s.index('\n\ntypedef',start);s=s[:start]+reference[a:b]+s[end:]
  s=s.replace(' for(s=0;s<3&&!Failures;s++){',' if(!SetCursorPos(1000,550)||!GdiFlush())ExitProcess(31);\n record("CURSOR_PARKED",1000,550,0);\n for(s=0;s<3&&!Failures;s++){')
 (k/name).write_text(s,newline='\n')
for name in ['trace.py','verify.py','discover_kernel.py','mark-diagnostic.py']:
 s=(old/name).read_text().replace('nt5-vrscan3-','nt5-vownscan-').replace('video-ram-scanout3','video-ownership-scanout').replace('xwnram.dll','xwnown.dll')
 (k/name).write_text(s,newline='\n')
(k/'DESIGN.md').write_text('''# Independent ownership0109 scanout diagnostic

Fresh immutable child, exact ordinary-passing xwnown.dll, unchanged storage/
miniport/network/dump/cache/device policy. This is a separate debugger run.
Twelve initial/DIB-copy/overlap checkpoints compare raw physical03c00000 RGB
with a host-calculated pattern. The cursor is parked outside the test window.
Live IDT kernel discovery, exact relocated display text and probe/kernel code
pins are mandatory. Header E14 is explicitly recorded as unavailable; readable
header mismatches still fail. Full bounded breakpoint teardown and cold audit.

This rechecks the ownership change's copy path, not broader DDIs or hardware.
No old guest is relaunched or used as the parent. Registry concurrency and
foreign-pointer tests remain host-shim evidence, not actual multi-device GDI.
''',newline='\n')
