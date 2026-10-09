"""Fresh phase/real-window diagnostic using198 and unchanged186 guard/probe checks."""
import ast, hashlib, json, shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-word-order186';driver=k.parent/'video-phase-profile198'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert not (k/'creation.json').exists()
names=['Build-Probe001.ps1','Run.ps1','atomic_json.py','audit-package.py','audit.py','check-leases.ps1','close-emulator.py','common.py','dib_analysis.py','freeze.py','inventory-devices.py','preflight.py','prepare-parent.py','prepare.py','restart_gate.h','review-build.py','runner.c','sample_analysis.py','sites.json','supervise.py','test-gate.c','xwnunused179.inf']
for name in names:
    s=(old/name).read_text().replace('video-word-order186','video-phase-runtime199').replace('video-word186','video-phase199').replace('nt5-word186','nt5-phase199').replace('xwnws186','xwnphase199').replace('windows-native-word186','windows-native-phase199')
    if name=='Run.ps1':
        start=s.index("if($Case -eq 'control001'){");end=s.index('\n@{utc=',start);s=s[:start]+s[end:]
    if name in ['freeze.py','prepare.py']:
        s=s.replace('video-word-store184','video-phase-profile198')
    if name=='prepare.py':
        s=s.replace('Same181 parent/hives/package/log history. Only matched115 display and new helper/startup;', 'Same181 parent/hives/package/log history. Only matched198 profile display and new helper/startup;')
    if name=='sample_analysis.py':s=s.replace('v8','v9').replace("'8','256','128'","'9','256','128'")
    if name=='audit.py':
        s=s.replace('from dib_analysis import analyze as analyze_dib','from dib_analysis import analyze as analyze_dib\nfrom timing_analysis import timing\nfrom window_analysis import window')
        s=s.replace("int(case=='candidate001')) for i in range(5)","0) for i in range(5)")
        at="r['dib_coverage_passed']=all(v['passed'] for v in r['dib_samples'])"
        s=s.replace(at,at+"\nr['phase_samples']=[timing(r.get('sample%d/gdi-baseline.txt'%i),int(case=='candidate001')) for i in range(5)]\nr['phase_coverage_passed']=all(v['passed'] for v in r['phase_samples'])\nr['window_samples']=[window(r.get('sample%d/gdi-baseline.txt'%i),int(case=='candidate001')) for i in range(5)]\nr['window_coverage_passed']=all(v['passed'] for v in r['window_samples'])")
        s=s.replace("and r['dib_coverage_passed']","and r['dib_coverage_passed'] and r['phase_coverage_passed'] and r['window_coverage_passed']")
        s=s.replace('Ordinary matched115 emulator copy/coverage.','Ordinary198 phase/real-window emulator observation.')
    if name=='freeze.py':
        s=s.replace("+[build/'row_store.h',build/'row-tests.c',build/'row-tests002.c']","+[build/'display/profile_math.h',build/'math-tests.c']")
        s=s.replace("same explicit null policy, no setup/debugger/physical action","same inherited emulator-only null policy, no setup/debugger/physical action")
    if name=='review-build.py':s=s.replace('v8','v9').replace('driver_changed=False','driver_changed=True')
    if name.endswith('.py'):ast.parse(s)
    if name in ['runner.c','restart_gate.h','test-gate.c','xwnunused179.inf']:shutil.copyfile(old/name,k/name)
    else:(k/name).write_bytes(s.encode())
(k/'artifacts').mkdir(exist_ok=True);shutil.copyfile(old/'artifacts/runner.exe',k/'artifacts/runner.exe')
for name in ['runner.c','restart_gate.h','test-gate.c','xwnunused179.inf']:
    assert (k/name).read_bytes()==(old/name).read_bytes(),name
probe=(old/'gdi-probe.c').read_text().replace('XWN_GDI_PROBE_VERSION",8','XWN_GDI_PROBE_VERSION",9').replace('XwnGdiProbeV8','XwnGdiProbeV9').replace('XWN scalar row stores115 longer - Esc cancels','XWN rendering/upload phases - Esc cancels')
timer=(k.parent/'video-body-runtime172/gdi-probe.c').read_text();block=timer[timer.index('    zero(data,sizeof(data));result=ExtEscape(Screen,0x58574433'):timer.index('\n    return TRUE;',timer.index('    zero(data,sizeof(data));result=ExtEscape(Screen,0x58574433'))]
needle='    for(i=21;i<32;i++)if(data[i]){record("FAIL_STATS_RESERVED",kind,phase,i);return FALSE;}\n    return TRUE;'
assert probe.count(needle)==1;probe=probe.replace(needle,needle.replace('    return TRUE;',block+'\n    return TRUE;'))
probe=probe.replace('static DWORD Failures;','static DWORD Failures, PaintRounds;\nstatic BOOL PaintPattern, PaintFailed;')
needle='if(message==WM_PAINT) {PAINTSTRUCT ps;BeginPaint(window,&ps);EndPaint(window,&ps);return 0;}'
replacement='''if(message==WM_PAINT) {
        PAINTSTRUCT ps;BeginPaint(window,&ps);
        if(PaintPattern) {
            if(!BitBlt(ps.hdc,0,0,W,H,Source,0,0,SRCCOPY)||
               !TextOutA(ps.hdc,5,5,"XWN phase window",16))PaintFailed=TRUE;
            ++PaintRounds;
        }
        EndPaint(window,&ps);return 0;
    }'''
assert probe.count(needle)==1;probe=probe.replace(needle,replacement)
extra=(k/'window_probe.inc').read_text();needle='void WINAPI mainCRTStartup(void) {';assert probe.count(needle)==1;probe=probe.replace(needle,extra+'\n'+needle)
needle='    SelectObject(Source,OldInput);SelectObject(Check,OldCheck);';assert probe.count(needle)==1;probe=probe.replace(needle,'    if(!Failures&&!windowcase())++Failures;\n'+needle)
(k/'gdi-probe.c').write_bytes(probe.encode())
timing=(k.parent/'video-body-runtime172/timing_analysis.py').read_text()
timing=timing.replace("assert [v for v in n if v[0]=='SOLID_stage_pass']==[('SOLID_stage_pass',0,1,0),('SOLID_stage_pass',1,1,0)]","assert [v for v in n if v[0]=='POST_TIMING_kind_pass']==[('POST_TIMING_kind_pass',i,1,0) for i in range(3)]")
timing=timing.replace('independent_solid_checks=2','posttiming_pixel_checks=3').replace('OFF comparison measures extra clock-query overhead, not all bookkeeping versus untouched112.','OFF/ON comparison measures enabled clock and tick-accounting increment; both retain common bookkeeping. Calibration is direct queries, not complete wrapper overhead.')
(k/'timing_analysis.py').write_bytes(timing.encode())
with (ws/'.gitattributes').open('ab') as f:f.write(b'\n/outputs/video-phase-runtime199/** -text whitespace=cr-at-eol\n')
(k/'creation.json').write_text(json.dumps(dict(prior_probe_sha256=sha(old/'gdi-probe.c'),unchanged_guard_sha256=sha(k/'artifacts/runner.exe'),new_probe_sha256=sha(k/'gdi-probe.c'),existing_pixel_checks_preserved=True,new_real_window_rounds=40,physical_access=False,guest_launch=False),indent=2)+'\n')
print('New199: identical186 guard, retained13 pixel checks/sample plus40 real window moves/paint/text/readbacks')
