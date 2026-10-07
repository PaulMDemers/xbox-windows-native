"""Create a new, guarded matched-control runtime kit. Does not launch guests."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-direct-ddi';sel=k.parent/'video-direct-ddi-selection'
def replace(s,a,b):
 assert a in s,a
 return s.replace(a,b)
for name in ['atomic_json.py','audit.py','configuration.py','cold-map.py','preflight.py','Run.ps1','supervise.py','record-closure.py','common.py','prepare.py']:
 s=(sel/name).read_text().replace('video-direct-ddi-selection','video-ram-primary').replace('nt5-vddi-sel-','nt5-vram-').replace('xwnddi113','xwnram114').replace('0107-direct-nt5-display.patch','0108-ram-primary.patch')
 if name=='common.py':
  s=replace(s,"take('ATTEMPT_ONCE',[113,3,3])","take('ATTEMPT_ONCE',[114,3,3])")
  a=s.index("        take('DRIVER_EXPECT_RESPONSE'");b=s.index('        for size,',a)
  s=s[:a]+'''        take('DRIVER_EXPECT_RESPONSE',[int(candidate),1,0])
        take('DRIVER_ID_VERSION_MODE',[0x44525758,108 if candidate else 107,int(candidate)])
        take('DRIVER_WIDTH_HEIGHT_STRIDE',[1024,576,4096]);take('DRIVER_BPP_BYTES_RESERVED',[32,2359296,0])
'''+s[b:]
  s=replace(s,"take('VERIFIED_PRE_POST',[2,1,0]);","take('VERIFIED_PRE_POST',[2,1,0]);take('SHADOW_COHERENCE',[int(candidate),0,int(candidate)]);")
  s=replace(s,"        take('COMPLETE'",'''        if candidate:
            calls=[take('SHADOW_CALLBACK',[i,None,None]) for i in []] # filled with exact index checks below
            for i in range(14):
                index,count,reserved=take('SHADOW_CALLBACK');assert index==i and reserved==0;calls.append(count)
            uploads,low,high=take('SHADOW_UPLOADS_BYTES');assert uploads>0 and (low or high) and sum(calls)>0
            r['shadow_callbacks']=calls;r['shadow_uploads']=uploads;r['shadow_bytes']=low+(high<<32)
        take('COMPLETE' ''')
  s=s.replace("calls=[take('SHADOW_CALLBACK',[i,None,None]) for i in []] # filled with exact index checks below","calls=[]")
 if name in ['preflight.py','prepare.py']:
  s=s.replace("candidate001/artifacts/xwndir.dll","candidate001/artifacts/xwnram.dll")
 if name=='configuration.py':
  s=s.replace("('xwndir' if case=='candidate001' else 'framebuf')","('xwnram' if case=='candidate001' else 'xwndir')")
 if name=='prepare.py':
  s=replace(s,"driver=k/'candidate001/artifacts/xwnram.dll';assert sha(driver)==review['display_sha256']","driver=k/'candidate001/artifacts/xwnram.dll';assert sha(driver)==review['display_sha256']\ncontrol=k.parent/'video-direct-ddi/candidate001/artifacts/xwndir.dll';assert sha(control)=='019f5267a66cf0a018731d1a3db9f9c8ef737da5a7fbeb6965c1aa96948d0d68'")
  s=s.replace("['winnt/system32/xwndir.dll'","['winnt/system32/xwnram.dll','winnt/system32/xwndir.dll'")
  s=s.replace("write=case=='candidate001'","write=True")
  s=s.replace("('xwndir' if case=='candidate001' else 'framebuf')","('xwnram' if case=='candidate001' else 'xwndir')")
  s=s.replace("if case=='candidate001':h.node_set_value","h.node_set_value").replace("if case=='candidate001':h.commit(None)","h.commit(None)")
  s=s.replace(" for r in edits] if case=='candidate001' else []"," for r in edits]")
  s=s.replace("if case=='control001':assert system_bytes==original_system","assert system_bytes!=original_system")
  s=s.replace("w.write('winnt/system32/xwndir.dll',driver.read_bytes())","w.write('winnt/system32/xwndir.dll',control.read_bytes()),\n w.write('winnt/system32/xwnram.dll',driver.read_bytes())")
  s=s.replace("if case=='candidate001':m.replace(w,'winnt/system32/config/system',system_bytes)","m.replace(w,'winnt/system32/config/system',system_bytes)")
  s=s.replace('Only project-owned display selection changes in candidate.','Each child changes exactly the same two selectors to its authored display.')
  s=s.replace('xwndir payload present in both, only selected in candidate. No shadow/cache/mode/physical change.','Both xwndir and xwnram payloads present in both. Direct0107 control, private RAM0108 candidate. No cache/mode/physical change.')
 if name=='audit.py':
  s=s.replace('Matched Microsoft framebuf/control or authored direct DDI/candidate GDI correctness and emulator API-path timing.','Matched direct0107/control or RAM0108/candidate GDI correctness; candidate self-check is not independent scanout proof. Callback coverage is observed, not exhaustive.')
 (k/name).write_text(s,newline='\n')
s=(old/'probe.c').read_text().replace('xwnddi113','xwnram114').replace('113','114').replace('XwnVideoDirect','XwnVideoRam')
s=s.replace('static DWORD Failures;','static DWORD Failures,ExpectedShadow;')
a=s.index('  if(expected){');b=s.index('\n }\n if(!GetClientRect',a)
s=s[:a]+'''  ExpectedShadow=expected;
  record("DRIVER_ID_VERSION_MODE",data[0],data[1],data[7]);
  record("DRIVER_WIDTH_HEIGHT_STRIDE",data[2],data[3],data[4]);
  record("DRIVER_BPP_BYTES_RESERVED",data[5],data[6],0);
  if(response!=1||data[0]!=0x44525758||data[1]!=(expected?108:107)||data[2]!=1024||data[3]!=576||data[4]!=4096||data[5]!=32||data[6]!=2359296||data[7]!=expected)ExitProcess(21);'''+s[b:]
needle='static BOOL one('
stats='''static BOOL coherence(BOOL final){DWORD d[32],i;int response;
 if(!ExpectedShadow){if(!final)record("SHADOW_COHERENCE",0,0,0);return TRUE;}
 zero(d,sizeof(d));if(!GdiFlush())return FALSE;response=ExtEscape(Screen,0x58574432,0,NULL,sizeof(d),(LPSTR)d);
 if(response!=1||d[0]!=0x53525758||d[1]!=108||d[19]||d[20]!=1){fail("FAIL_SHADOW_COHERENCE",response,d[19],d[20]);return FALSE;}
 for(i=21;i<32;i++)if(d[i])return FALSE;
 if(!final)record("SHADOW_COHERENCE",1,d[19],d[20]);
 else {for(i=0;i<14;i++)record("SHADOW_CALLBACK",i,d[2+i],0);record("SHADOW_UPLOADS_BYTES",d[16],d[17],d[18]);}
 return TRUE;
}
'''
s=s.replace(needle,stats+needle)
s=replace(s,'record("VERIFIED_PRE_POST",2,1,0);return TRUE;','record("VERIFIED_PRE_POST",2,1,0);if(!coherence(FALSE)){fail("FAIL_COHERENCE_CASE",size,round,kind);return FALSE;}return TRUE;')
s=replace(s,' if(!ReleaseDC(Window,Screen)', ' if(!Failures&&!coherence(TRUE))fail("FAIL_FINAL_COHERENCE",0,0,0);\n if(!ReleaseDC(Window,Screen)')
(k/'probe.c').write_text(s,newline='\n')
(k/'Build-Probe.ps1').write_text((old/'Build-Probe.ps1').read_text(),newline='\n')
s=(old/'review.py').read_text().replace('0107-direct-nt5-display.patch','0108-ram-primary.patch').replace('xwndir.dll','xwnram.dll')
s=s.replace('Direct DDI identity and functional compatibility still require ordinary guest evidence.','RAM-primary identity/coherence and functional compatibility still require guest evidence; host engine is a shim.')
(k/'review.py').write_text(s,newline='\n')
