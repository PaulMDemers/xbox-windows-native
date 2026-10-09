"""New v5 read-only timing snapshots and independently expected solid pixels."""
import ast,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-hook-counters167';p=k/'gdi-probe.c';assert not p.exists()
text=(old/'gdi-probe.c').read_text().replace('XwnGdiProbeV4','XwnGdiProbeV5').replace('existing driver counters v4','elapsed bodies v5')
text=text.replace('record("XWN_GDI_PROBE_VERSION",4,W,H)','record("XWN_GDI_PROBE_VERSION",5,W,H)')
start=text.index('static BOOL snapshot(');end=text.index('static BOOL identity(',start)
piece=text[start:end]
assert piece.count('    return TRUE;')==1
piece=piece.replace('    return TRUE;',r'''
    zero(data,sizeof(data));result=ExtEscape(Screen,0x58574433,0,NULL,sizeof(data),(LPSTR)data);
    record("PROFILE_CALL_kind_phase_result",kind,phase,(DWORD)result);
    for(i=0;i<32;i++)record(phase?"PROFILE_AFTER_kind_index_value":"PROFILE_BEFORE_kind_index_value",kind,i,data[i]);
    if(result!=1||data[0]!=0x544d5758||data[1]!=113||data[2]!=128||data[3]>1||
       (data[4]==0&&data[5]==0)||data[5]>=0x80000000||data[6]!=128||data[11]||data[12]||data[13]) {
        record("FAIL_PROFILE_CONTRACT",kind,phase,0);return FALSE;
    }
    for(i=27;i<32;i++)if(data[i]){record("FAIL_PROFILE_RESERVED",kind,phase,i);return FALSE;}
    return TRUE;''')
text=text[:start]+piece+text[end:]
pos=text.index('static void timed(')
text=text[:pos]+r'''static BOOL solidcheck(DWORD stage) {
    DWORD i,expected=stage?0xffffff:0;
    if(!uncover(20+stage))return FALSE;
    if(!PatBlt(Screen,0,0,W,H,stage?WHITENESS:BLACKNESS)||!GdiFlush()) {
        record("FAIL_SOLID_API",stage,GetLastError(),0);return FALSE;
    }
    for(i=0;i<W*H;i++)Pixels[i]=0xdeadbeef;
    if(!blit(20+stage,Check,0,0,Screen,0,0)||!visible())return FALSE;
    for(i=0;i<W*H;i++)if((Pixels[i]&0xffffff)!=expected) {
        record("MISMATCH_SOLID_stage_index_actual",stage,i,Pixels[i]&0xffffff);return FALSE;
    }
    return TRUE;
}
'''+text[pos:]
line='    if(!Failures) {\n        for(i=0;i<5 && messages();i++)timed(i);'
assert text.count(line)==1
text=text.replace(line,'    for(i=0;i<2&&!Failures;i++) {check=solidcheck(i);record("SOLID_stage_pass",i,check,0);if(!check)++Failures;}\n'+line)
p.write_bytes(text.encode());(k/'artifacts').mkdir(exist_ok=True)
shutil.copyfile(old/'artifacts/runner.exe',k/'artifacts/runner.exe')
for name in ['Build-Probe.ps1','review-build.py','sample_analysis.py']:
 text=(old/name).read_text().replace('video-hook-counters167','video-body-timing170')
 if name=='review-build.py':text=text.replace('driver_changed=False','driver_changed=True').replace('v4 ExtEscape','v5 ExtEscape')
 if name=='sample_analysis.py':text=text.replace("'4','256','128'","'5','256','128'").replace('Fail-closed v4','Fail-closed v5')
 ast.parse(text) if name.endswith('.py') else None
 (k/name).write_bytes(text.encode())
print('New v5 helper source; no compile/launch, expected solids and profile contract')
