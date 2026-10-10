"""Fresh211 protocol and controlled move/paint/readback producer probe; no launch."""
import ast,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-scalar-runtime209';assert not (k/'creation.json').exists()
if (k/'common.py').exists():
 failed=json.loads((k/'factory-failed001.json').read_text());assert not failed['guest_launch']
 for n,h in failed['files'].items():
  if n!='create-kit.py':assert hashlib.sha256((k/n).read_bytes()).hexdigest()==h
names=['common.py','Run.ps1','Invoke-209.ps1','run-emulator.py','supervise-emulator.py','typed-state.py','audit-emulator.py','prepare-emulator.py',
 'runner_analysis.py','boundary_analysis.py','interval_policy.py','sample_analysis.py','dib_analysis.py','timing_analysis.py','window_analysis.py','text_analysis.py',
 'capture.py','capture-probe-providers.py','review.py','edit-binding.py','prepare-package.py','prepare-physical.py','physical-controller.py','watch-physical.py',
 'finish-physical.py','audit-physical.py','audit-physical-hives.py','verify-restored.py','close-case.py','gdi-probe.c','text-cases.c']
for name in names:
 s=(old/name).read_text()
 s=s.replace('video-scalar-runtime209','video-upload-runtime211').replace('video-scalar208','video-upload-accounting210')
 s=s.replace('xwnuc209','xwnua211').replace('scalar209','upload211').replace('display209','display211').replace('rollback209','rollback211').replace('Invoke-209','Invoke-211')
 if name=='sample_analysis.py':s=s.replace("'11','256','128'","'12','256','128'")
 if name=='text_analysis.py':s=s.replace("'XWN_GDI_PROBE_VERSION',11,256,128","'XWN_GDI_PROBE_VERSION',12,256,128")
 if name=='audit-emulator.py':
  s=s.replace("dib(v,int(case=='candidate001'))",'dib(v,0)').replace('text_analysis(v,0)','text_analysis(v,1)')
  s=s.replace('from common import *','from common import *\nfrom upload_analysis import analyze as uploads')
  s=s.replace("r['text_samples']=", "r['upload_samples']=[uploads(v,int(case=='candidate001')) for v in texts]\nr['text_samples']=")
  s=s.replace("'window_samples','text_samples'", "'window_samples','text_samples','upload_samples'")
 if name=='audit-physical.py':
  s=s.replace("rows_analyze(v,int(case=='candidate001'))",'rows_analyze(v,0)').replace('text_analyze(v,0)','text_analyze(v,1)')
  s=s.replace('from text_analysis import analyze as text_analyze','from text_analysis import analyze as text_analyze\nfrom upload_analysis import analyze as uploads')
  s=s.replace('texts=[text_analyze(v,1) for v in logs]','texts=[text_analyze(v,1) for v in logs]\nuploads_result=[uploads(v,int(case==\'candidate001\')) for v in logs]')
  s=s.replace('    text_samples=texts,text_coverage_passed=',"    upload_samples=uploads_result,upload_coverage_passed=all(v['passed'] for v in uploads_result),\n    text_samples=texts,text_coverage_passed=")
  s=s.replace("'text_coverage_passed','normal_restart_requested'", "'text_coverage_passed','upload_coverage_passed','normal_restart_requested'")
 if name=='prepare-package.py':
  s=s.replace("assert read(k.parent/'video-upload-accounting210/instruction-review.json')['passed']", "assert read(k.parent/'video-upload-accounting210/host-tests001.json')['passed']")
 if name=='prepare-physical.py':s=s.replace("['actual_scalar_coverage_passed']","['actual_upload_coverage_passed']")
 if name=='gdi-probe.c':
  s=s.replace('XWN_GDI_PROBE_VERSION",11','XWN_GDI_PROBE_VERSION",12').replace('XwnGdiProbeV11','XwnGdiProbeV12')
  needle='static BOOL windowcase(void) {';assert s.count(needle)==1
  s=s.replace(needle,'''/* Fixed-size read-only completed-copy packets, no file IO between phase reads. */
static BOOL uploadsnapshot(DWORD *d) {
    zero(d,632);
    return ExtEscape(Screen,0x58574438,0,NULL,632,(LPSTR)d)==1 &&
           d[0]==0x41555758 && d[1]==119 && d[2]==632 && d[3]<=1 &&
           d[4]==15 && !d[5] && !d[6] && !d[7];
}
static BOOL uploademit(DWORD step,DWORD phase,DWORD *d) {
    static char buffer[16384];DWORD i,length=0,written;
    for(i=0;i<158;i++) {
        if(length>sizeof(buffer)-128)return FALSE;
        length+=(DWORD)wsprintfA(buffer+length,"UPLOAD_WORD_tag_index_value %lu %lu %lu\\r\\n",step*4+phase,i,d[i]);
    }
    return WriteFile(Log,buffer,length,&written,NULL)&&written==length&&FlushFileBuffers(Log);
}
static BOOL windowcase(void) {''')
  s=s.replace('    DWORD *expected=NULL,i,j,start,elapsed,previous;BOOL ok=FALSE;', '    DWORD *expected=NULL,i,j,start,elapsed,previous,phase,upload[4][158];BOOL ok=FALSE;')
  a=s.index('    for(i=0;i<40;i++) {',s.index('static BOOL windowcase'));b=s.index('    elapsed=GetTickCount()-start;',a)
  s=s[:a]+'''    for(i=0;i<40;i++) {
        if(!messages()||!GdiFlush()||!uploadsnapshot(upload[0]))break;
        if(!SetWindowPos(Window,HWND_TOPMOST,40+(i&1)*32,40+(i&1)*16,0,0,SWP_NOSIZE|SWP_SHOWWINDOW)||
           !messages()||!GdiFlush()||!visible()||PaintFailed||!uploadsnapshot(upload[1]))break;
        if(!InvalidateRect(Window,NULL,FALSE)||!UpdateWindow(Window)||!GdiFlush()||
           !visible()||PaintFailed||!uploadsnapshot(upload[2]))break;
        if(!blit(200+i,Check,0,0,Screen,0,0)||!uploadsnapshot(upload[3]))break;
        for(j=0;j<W*H;j++)if((Pixels[j]&0xffffff)!=(expected[j]&0xffffff))break;
        if(j!=W*H) {record("MISMATCH_WINDOW_round_index",i,j,0);break;}
        for(phase=0;phase<4;phase++)if(!uploademit(i,phase,upload[phase]))break;
        if(phase!=4) {record("FAIL_UPLOAD_PACKET_WRITE",i,phase,GetLastError());break;}
        record("UPLOAD_STEP_exact",i,1,0);
    }
''' +s[b:]
 if name.endswith('.py'):ast.parse(s)
 (k/('Invoke-211.ps1' if name=='Invoke-209.ps1' else name)).write_text(s,newline='\n')
# Verify the audit gate actually includes the new producer result, before freeze.
for name in ['audit-emulator.py','audit-physical.py']:
 s=(k/name).read_text();assert 'upload_samples' in s,name
 assert ("'upload_samples'" if name=='audit-emulator.py' else "'upload_coverage_passed'") in s,name
(k/'artifacts').mkdir(exist_ok=True)
for name in ['runner.exe','wizard.exe']:shutil.copyfile(old/'artifacts'/name,k/'artifacts'/name)
shutil.copyfile(k.parent/'video-text-oracle206/Build-Probe.ps1',k/'Build-Probe.ps1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(k/'creation.json').write_text(json.dumps(dict(passed=True,physical_access=False,guest_launch=False,
 inherited_protocol_sha256={n:sha(old/n) for n in names},new_source_sha256={p.name:sha(p) for p in k.glob('*.c')},
 unchanged_runner_sha256=sha(k/'artifacts/runner.exe'),unchanged_wizard_sha256=sha(k/'artifacts/wizard.exe'),
 limits='Fresh211 IDs/namespaces. Four phase snapshots per40 controlled movements; no logging between snapshots. Same202 joinedrunner/201helper and existing strict gates. No physical access yet.'),indent=2)+'\n')
print('Fresh211 protocol/probe created; no launch')
