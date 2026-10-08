"""Fresh read-only escape diagnostic; never mutate an executed previous kit."""
import ast,shutil
from pathlib import Path
k=Path(__file__).resolve().parent; old=k.parent/'video-paired-timing166'
assert not (k/'Run.ps1').exists()
for name in ['common.py','prepare.py','preflight.py','audit.py','supervise.py','check-leases.ps1','Run.ps1','freeze.py']:
    text=(old/name).read_text(encoding='utf-8').replace('video-paired-timing166','video-hook-counters167').replace('vperf166','vhooks167').replace('xwnvt166','xwnvh167')
    text=text.replace("['control001','candidate001']","['candidate001']").replace("ValidateSet('control001','candidate001')","ValidateSet('candidate001')")
    if name=='prepare.py':
        text=text.replace("k/'artifacts/runner.exe'","k/'artifacts/runner.exe'").replace("k.parent/'video-next/probe-v3/artifacts/gdi-probe.exe'","k/'artifacts/gdi-probe.exe'")
    if name=='freeze.py':
        text=text.replace("k.parent/'video-next/probe-v3/artifacts/gdi-probe.exe'","k/'artifacts/gdi-probe.exe'").replace("k/'runner.c'","k/'gdi-probe.c'")
    (k/name).write_bytes(text.encode('utf-8'))
(k/'artifacts').mkdir(exist_ok=False)
shutil.copyfile(old/'artifacts/runner.exe',k/'artifacts/runner.exe')
text=(k.parent/'video-next/probe-v3/gdi-probe.c').read_text(encoding='utf-8')
extra='''/* Existing RAM0112 escapes. Full-screen comparison runs OUTSIDE the timer. */
static BOOL snapshot(DWORD kind,DWORD phase) {
    DWORD data[32],start,elapsed,i;int result;
    zero(data,sizeof(data));
    if(!GdiFlush()){record("FAIL_STATS_FLUSH",kind,phase,GetLastError());return FALSE;}
    start=GetTickCount();
    result=ExtEscape(Screen,0x58574432,0,NULL,sizeof(data),(LPSTR)data);
    elapsed=GetTickCount()-start;
    record("STATS_CALL_kind_phase_result",kind,phase,(DWORD)result);
    record("STATS_LATENCY_kind_phase_ms",kind,phase,elapsed);
    for(i=0;i<32;i++)record(phase?"STATS_AFTER_kind_index_value":"STATS_BEFORE_kind_index_value",kind,i,data[i]);
    if(result!=1||data[0]!=0x53525758||data[1]!=112||data[20]!=1) {
        record("FAIL_STATS_IDENTITY",kind,phase,0);return FALSE;
    }
    if(data[19]){record("FAIL_SCANOUT_MISMATCH",kind,phase,data[19]);return FALSE;}
    for(i=21;i<32;i++)if(data[i]){record("FAIL_STATS_RESERVED",kind,phase,i);return FALSE;}
    return TRUE;
}
static BOOL identity(void) {
    DWORD data[8],i;int result;
    zero(data,sizeof(data));result=ExtEscape(Screen,0x58574431,0,NULL,sizeof(data),(LPSTR)data);
    record("IDENTITY_RESULT",(DWORD)result,0,0);
    for(i=0;i<8;i++)record("IDENTITY_index_value",i,data[i],0);
    if(result!=1||data[0]!=0x44525758||data[1]!=112||data[2]!=(DWORD)GetDeviceCaps(Screen,HORZRES)||
       data[3]!=(DWORD)GetDeviceCaps(Screen,VERTRES)||data[4]!=data[2]*4||data[5]!=32||
       data[6]!=data[4]*data[3]||data[7]!=1) {
        record("FAIL_IDENTITY",(DWORD)result,0,0);return FALSE;
    }
    return TRUE;
}
'''
text=text.replace('static BOOL messages(void)',extra+'\nstatic BOOL messages(void)')
text=text.replace('    start=GetTickCount();\n    do {','    if(!snapshot(kind,0)){++Failures;return;}\n    start=GetTickCount();\n    do {')
text=text.replace('    record("TIMING_kind_count_ms",kind,count,elapsed);','    record("TIMING_kind_count_ms",kind,count,elapsed);\n    if(!snapshot(kind,1))++Failures;')
text=text.replace('"XWN_GDI_PROBE_VERSION",3','"XWN_GDI_PROBE_VERSION",4').replace('XwnGdiProbeV3','XwnGdiProbeV4').replace('XWN video baseline v3 - Esc cancels','XWN existing driver counters v4 - Esc cancels')
text=text.replace('    GdiSetBatchLimit(1);','    GdiSetBatchLimit(1);\n    if(!identity())++Failures;')
(k/'gdi-probe.c').write_bytes(text.encode('utf-8'))
text=(k.parent/'video-next/probe-v3/Build-Probe.ps1').read_text(encoding='utf-8').replace('video-next/probe-v3','video-hook-counters167')
text=text.replace("$ErrorActionPreference='Stop'","$ErrorActionPreference='Stop'\nif((Get-PSDrive C).Free -lt 20GB){throw '20 GiB guard'}")
(k/'Build-Probe.ps1').write_bytes(text.encode('utf-8'))
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
print('Fresh candidate-only counters diagnostic created; driver unchanged')
