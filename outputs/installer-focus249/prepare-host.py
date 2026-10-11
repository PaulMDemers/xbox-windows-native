"""Fresh diagnostic child of CLOSED248; change wait logging only, never old evidence."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'worker-barrier248';ws=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (k/'wizard.c').exists()
parent=k.parent/'setup-wizard-automation201'
build=json.loads((parent/'build006.json').read_text())
s=(parent/'wizard006.c').read_text()
assert sha(parent/'wizard006.c')==build['source_sha256']
assert build['binary_sha256']=='b3a42114e2d083d3d124cb54199a8d6c3fd63fee5a9ef6b196e4599d28b84fbb'
original=s
s=s.replace('static DWORD PendingPid,PendingTid,LastState;', 'static DWORD PendingPid,PendingTid,LastState,LastWait;\nstatic BOOL WaitLogged;')
marker='static BOOL CALLBACK top(HWND h,LPARAM unused) {'
assert s.count(marker)==1
addition='''/* Read-only diagnostic at a refused action. No activation, input or policy edits. */
static void wait_blob(const char *label,DWORD owner,const char *value) {
    static const char hex[]="0123456789abcdef";char encoded[1025],line[1152];DWORD i,n=lstrlenA(value),w=0;
    if(n>512)ExitProcess(103);
    for(i=0;i<n;i++){encoded[2*i]=hex[((BYTE)value[i])>>4];encoded[2*i+1]=hex[((BYTE)value[i])&15];}
    encoded[2*n]=0;wsprintfA(line,"%s %lu %lu %s\\r\\n",label,owner,n,encoded);n=lstrlenA(line);
    if(n>1024*1024-Written||!WriteFile(Log,line,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(91);
    Written+=n;
}
static void wait_snapshot(HWND refused,DWORD tid) {
    HWND fg=GetForegroundWindow();DWORD pid=0,ftid;char title[128]={0},cls[32]={0},command[512]={0};FILETIME born={0};HANDLE p;
    record("WAIT_SAMPLE249",GetTickCount()-Started,CurrentPid,(DWORD)refused);
    gui_state("WAIT249",tid);ftid=GetWindowThreadProcessId(fg,&pid);
    record("WAIT_FG249",pid,(DWORD)fg,ftid);
    record("WAIT_WINDOW249",IsWindow(fg),IsWindowVisible(fg),IsWindowEnabled(fg));
    record("WAIT_TEXT249",text(fg,title,sizeof(title)),GetClassNameA(fg,cls,sizeof(cls))!=0,0);
    wait_blob("WAIT_TITLE249",(DWORD)fg,title);wait_blob("WAIT_CLASS249",(DWORD)fg,cls);
    p=OpenProcess(PROCESS_QUERY_INFORMATION|PROCESS_VM_READ|SYNCHRONIZE,FALSE,pid);
    if(p){
        record("WAIT_OWNER249",pid,creation(p,&born),WaitForSingleObject(p,0));
        record("WAIT_CREATION249",pid,born.dwLowDateTime,born.dwHighDateTime);
        if(getcommand(p,command))wait_blob("WAIT_COMMAND249",pid,command);
        else record("WAIT_COMMAND_FAILED249",pid,GetLastError(),0);
        CloseHandle(p);
    }else record("WAIT_OPEN_FAILED249",pid,GetLastError(),0);
    record("WAIT_END249",GetTickCount()-Started,CurrentPid,(DWORD)refused);
}
'''
s=s.replace(marker,addition+marker)
oldline='if(GetForegroundWindow()!=h||!GetGUIThreadInfo(w.tid,&info)||info.hwndActive!=h||info.hwndCapture||info.hwndMenuOwner||info.hwndMoveSize){record("CANCEL_ACTIVE_WAIT",CurrentPid,(DWORD)h,0);return TRUE;}'
newline=oldline.replace('return TRUE;', 'if(!WaitLogged||GetTickCount()-LastWait>=5000){LastWait=GetTickCount();WaitLogged=TRUE;wait_snapshot(h,w.tid);}return TRUE;')
assert s.count(oldline)==1;s=s.replace(oldline,newline)
# Exact inverse proves every original eligibility/revalidation/input line remains.
back=s.replace(newline,oldline).replace(addition,'').replace('static DWORD PendingPid,PendingTid,LastState,LastWait;\nstatic BOOL WaitLogged;', 'static DWORD PendingPid,PendingTid,LastState;')
assert back==original
(k/'wizard.c').write_text(s)
shutil.copyfile(parent/'policy.h',k/'policy.h')
names=['audit-emulator.py','close-host.py','common.py','parsing.py','preservation.py','typed-state.py','supervise-emulator.py','run-emulator.py','Run.ps1','Invoke-248.ps1','trace.py','schema.py','lifecycle.py','lifecycle246.py','lifecycle247.py','closed.py','worker.py','analyze-worker.py']
for name in names:
 t=(old/name).read_text().replace('worker-barrier248','installer-focus249').replace('phase248','phase249').replace('Invoke-248','Invoke-249')
 (k/name.replace('Invoke-248','Invoke-249')).write_text(t)
for name in ['inputs','ram-source']:shutil.copytree(old/'artifacts'/name,k/'artifacts'/name)
shutil.copytree(old/'source',k/'source')
for name in ['build004.json','candidate004-source-pins.json']:shutil.copyfile(old/name,k/name)
(k/'preserve001/artifacts').mkdir(parents=True)
rows=[]
for row in json.loads((old/'baseline-inputs001.json').read_text())['files']:
 p=ws/row['path'];assert sha(p)==row['sha256'];to=k/'preserve001/artifacts'/p.name;shutil.copyfile(p,to);rows.append(dict(path=to.relative_to(ws).as_posix(),sha256=sha(to)))
(k/'baseline-inputs001.json').write_text(json.dumps(dict(passed=True,files=rows,physical_access=False),indent=2)+'\n')
(k/'source-review001.json').write_text(json.dumps(dict(passed=True,source_sha256=sha(k/'wizard.c'),parent_source_sha256=build['source_sha256'],parent_binary_sha256=build['binary_sha256'],exact_inverse_equals_parent=True,policy_sha256=sha(k/'policy.h'),new_input_activation_or_policy_calls=False,wait_log_max_bytes=1048576,sample_spacing_ms=5000,parent_wait_bound_ms=120000,physical_access=False),indent=2)+'\n')
print('249 new wait-only diagnostic prepared; same compiled247004 emulator')
