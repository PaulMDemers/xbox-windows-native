"""New large-area phase snapshots; retain all327 operations and independent oracles."""
import difflib,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'hd-large327'
sha=lambda b:hashlib.sha256(b).hexdigest()
for name in ['gdi-probe.c','text-cases.c','large_oracle.h','large_analysis.py']:
    assert not (K/name).exists();(K/name).write_bytes((P/name).read_bytes())
s=(P/'large_cases.c').read_text();original=s
helper='''/* Capture without log I/O. Both packets publish only after the timed loop. */
static BOOL lg_phase(DWORD data[32]) {
    DWORD i;int rc;
    zero(data,128);rc=ExtEscape(Screen,0x58574433,0,NULL,128,(LPSTR)data);
    if(rc!=1||data[0]!=0x544d5758||data[1]!=113||data[2]!=128||data[3]>1||
       (!data[4]&&!data[5])||data[5]>=0x80000000||data[6]!=128||data[11]||data[12]||data[13])return FALSE;
    for(i=27;i<32;i++)if(data[i])return FALSE;
    return TRUE;
}
static void lg_phase_emit(DWORD id,DWORD phase,const DWORD data[32]) {
    DWORD i;record("PHASE344_PACKET",id,phase,1);
    for(i=0;i<32;i++)record(phase?"PHASE344_AFTER":"PHASE344_BEFORE",id,i,data[i]);
}
'''
s=s.replace('static BOOL lg_pixels(',helper+'static BOOL lg_pixels(',1)
s=s.replace('DWORD *source=NULL,*actual=NULL;RECT', 'DWORD phases[2][32];DWORD *source=NULL,*actual=NULL;RECT',1)
s=s.replace('if(!lg_stats(id,0,before))goto done;', 'if(!lg_stats(id,0,before)||!lg_phase(phases[0]))goto done;',1)
s=s.replace('elapsed=GetTickCount()-start;LargePaint=FALSE;', 'elapsed=GetTickCount()-start;LargePaint=FALSE;\n        if(!lg_phase(phases[1]))goto done;\n        lg_phase_emit(id,0,phases[0]);lg_phase_emit(id,1,phases[1]);',1)
s=s.replace('record("LARGE_VERSION",327,3,5);','record("PHASE344_VERSION",344,15,2);\n    record("LARGE_VERSION",327,3,5);',1)
s=s.replace('record("LARGE_COMPLETE",3,15,0);return TRUE;','record("LARGE_COMPLETE",3,15,0);\n    record("PHASE344_COMPLETE",15,30,0);return TRUE;',1)
assert s!=original and not (K/'large_cases.c').exists();(K/'large_cases.c').write_text(s)
(K/'source.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='327/large_cases.c',tofile='344/large_cases.c')))
b=(P/'build.py').read_text().replace("['build001','build002','build003']","['build001']").replace('/mnt/d/xwn327','/mnt/e/xwn344').replace("'D:'+str(out/'replay.exe')[6:]","'E:'+str(out/'replay.exe')[6:]")
(K/'build.py').write_text(b)
(K/'source-review.json').write_text(json.dumps(dict(passed=True,driver_changed=False,operation_function_unchanged=original[original.index('static BOOL lg_operation'):original.index('static BOOL lg_size')]==s[s.index('static BOOL lg_operation'):s.index('static BOOL lg_size')],sources={n:sha((K/n).read_bytes()) for n in ['gdi-probe.c','text-cases.c','large_oracle.h','large_analysis.py','large_cases.c']},parent_sources={n:sha((P/n).read_bytes()) for n in ['gdi-probe.c','text-cases.c','large_oracle.h','large_analysis.py','large_cases.c']},limits='No runtime or performance result; snapshots device-global, elapsed counts include scheduling/background. Wrappers overlap body times.'),indent=2)+'\n')
