"""Prepare uniquely named204 ordinary runtime inputs; no build or launch."""
import json,hashlib,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-unattended202'
assert not (k/'gdi-probe.c').exists()
source=(k.parent/'video-phase-runtime199/gdi-probe.c').read_text(encoding='utf-8')
assert hashlib.sha256((k.parent/'video-phase-runtime199/gdi-probe.c').read_bytes()).hexdigest()==json.loads((k.parent/'video-phase-runtime199/probe-build002.json').read_text())['source_sha256']
source=source.replace('"XWN_GDI_PROBE_VERSION",9,W,H','"XWN_GDI_PROBE_VERSION",10,W,H').replace('XwnGdiProbeV9','XwnGdiProbeV10')
source=source.replace('void WINAPI mainCRTStartup(void)', '#include "text-cases.c"\n\nvoid WINAPI mainCRTStartup(void)')
source=source.replace('    Window=CreateWindowExA(', '    if(!backdropcreate()){record("FAIL_BACKDROP",GetLastError(),0,0);ExitProcess(1);}\n    Window=CreateWindowExA(')
source=source.replace('    if(!Failures&&!windowcase())++Failures;', '    for(i=0;i<13&&!Failures;i++)if(!textcase(i))++Failures;\n    if(!Failures&&!windowcase())++Failures;')
source=source.replace('    record(Failures?"FAIL":"PASS"', '    if(Backdrop)DestroyWindow(Backdrop);\n    record(Failures?"FAIL":"PASS"')
(k/'gdi-probe.c').write_text(source,encoding='utf-8',newline='\n')
for name in ['common.py','Run.ps1','supervise-emulator.py','typed-state.py','audit-emulator.py','prepare-emulator.py',
             'runner_analysis.py','boundary_analysis.py','interval_policy.py','sample_analysis.py','dib_analysis.py','timing_analysis.py','window_analysis.py']:
 data=(old/name).read_text(encoding='utf-8').replace('unattended202','text204').replace('video202','text204').replace('xwnpre202a','xwntxt204a').replace('xwnpre202b','xwntxt204b')
 if name=='sample_analysis.py':data=data.replace("'9','256','128'","'10','256','128'")
 if name=='prepare-emulator.py':
  data=data.replace("payloads=read(k.parent/'video-phase-physical200/package-review.json')['cases'][case]", "payloads=read(k.parent/'video-phase-physical200/package-review.json')['cases'][case]\npayloads=[dict(row,source=str((k.parent/'video-text-bounds203'/case/'artifacts/xwnown.dll').relative_to(ws)),sha256=sha(k.parent/'video-text-bounds203'/case/'artifacts/xwnown.dll')) if row['target'].endswith('/xwnown.dll') else row for row in payloads]")
 if name=='audit-emulator.py':
  data=data.replace('from window_analysis import window','from window_analysis import window\nfrom text_analysis import analyze as text_analysis')
  data=data.replace("timing(v,int(case=='candidate001'))",'timing(v,0)').replace("window(v,int(case=='candidate001'))",'window(v,0)')
  data=data.replace("r['actual_caps']=", "r['text_samples']=[text_analysis(v,int(case=='candidate001')) for v in texts]\nr['actual_caps']=",1)
  data=data.replace("['dib_samples','phase_samples','window_samples']","['dib_samples','phase_samples','window_samples','text_samples']")
  data=data.replace('exact199 pixel/window/clock scope','new204 text bytes/pixels plus retained199 copy/window/clock scope')
 (k/name).write_text(data,encoding='utf-8',newline='\n')
(k/'artifacts').mkdir(exist_ok=False)
for name in ['runner.exe','wizard.exe']:shutil.copyfile(old/'artifacts'/name,k/'artifacts'/name)
build=(k.parent/'video-phase-runtime199/Build-Probe002.ps1').read_text().replace('gdi-probe.exe','replay.exe').replace('probe-build002.json','probe-build001.json')
build=build.replace('-fno-builtin', '-fno-builtin -Wno-misleading-indentation')
(k/'Build-Probe.ps1').write_text(build,encoding='utf-8',newline='\n')
print('New204 text source and fresh ordinary protocol prepared; no launch')
