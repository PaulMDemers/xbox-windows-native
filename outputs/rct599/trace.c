/* MIT. Bounded process-local API-entry observer; no resolution-return claims. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include "target_iat.h"
typedef struct {DWORD id;HANDLE h;BOOL held;} THREAD;
typedef struct {DWORD address;BYTE original;BOOL armed;} BP;
static THREAD threads[64];static BP bp[2];static HANDLE process,logfile;
static DWORD step_id,step_bp,requests,started;static BOOL initial,failed,exited;
static void zero(void *p,DWORD n) {BYTE *b=p;while(n--)*b++=0;}
static void line(const char *s) {DWORD n=lstrlenA(s),w;if(!WriteFile(logfile,s,n,&w,0)||w!=n)failed=TRUE;}
static void event(const char *kind,DWORD a,DWORD b,DWORD c) {
    char s[160];wsprintfA(s,"%s %08lx %08lx %08lx\r\n",kind,a,b,c);line(s);
}
static BOOL readmem(DWORD address,void *dest,DWORD n) {
    SIZE_T got=0;return address&&ReadProcessMemory(process,(LPCVOID)address,dest,n,&got)&&got==n;
}
static BOOL bytewrite(DWORD address,BYTE value) {
    DWORD old,ignored;SIZE_T written=0;BYTE readback=0;BOOL ok,restored;
    if(!VirtualProtectEx(process,(LPVOID)address,1,PAGE_EXECUTE_READWRITE,&old))return FALSE;
    ok=WriteProcessMemory(process,(LPVOID)address,&value,1,&written)&&written==1;
    restored=VirtualProtectEx(process,(LPVOID)address,1,old,&ignored);
    return ok&&restored&&FlushInstructionCache(process,(LPCVOID)address,1)&&readmem(address,&readback,1)&&readback==value;
}
static THREAD *thread(DWORD id) {DWORD i;for(i=0;i<64;i++)if(threads[i].id==id)return &threads[i];return 0;}
static BOOL addthread(DWORD id,HANDLE h) {
    DWORD i;if(thread(id))return FALSE;
    for(i=0;i<64;i++)if(!threads[i].id) {
        threads[i].id=id;threads[i].h=h;threads[i].held=FALSE;
        if(step_id&&id!=step_id) {if(SuspendThread(h)==(DWORD)-1)return FALSE;threads[i].held=TRUE;}
        return TRUE;
    }return FALSE;
}
static BOOL holdothers(DWORD id) {
    DWORD i;for(i=0;i<64;i++)if(threads[i].id&&threads[i].id!=id) {
        if(threads[i].held||SuspendThread(threads[i].h)==(DWORD)-1)return FALSE;
        threads[i].held=TRUE;
    }return TRUE;
}
static BOOL releaseothers(void) {
    DWORD i,n;for(i=0;i<64;i++)if(threads[i].held) {
        n=ResumeThread(threads[i].h);if(n==(DWORD)-1||n==0)return FALSE;threads[i].held=FALSE;
    }return TRUE;
}
static BOOL arm(void) {
    DWORD i,iat[2]={IAT_LOAD597,IAT_PROC597};
    for(i=0;i<2;i++) {
        if(!readmem(iat[i],&bp[i].address,4)||!readmem(bp[i].address,&bp[i].original,1)||bp[i].original==0xcc)return FALSE;
        if(i&&bp[i].address==bp[0].address)return FALSE;
        if(!bytewrite(bp[i].address,0xcc))return FALSE;
        bp[i].armed=TRUE;event("ARM",i,iat[i],bp[i].address);
    }return TRUE;
}
static BOOL request(DWORD which,DWORD tid,CONTEXT *ctx) {
    DWORD stack[3],name,i;char hex[513],s[680];BYTE c;const char digits[]="0123456789abcdef";
    if(!readmem(ctx->Esp,stack,which?12:8))return FALSE;
    name=stack[which?2:1];
    if(which&&name<=65535) {wsprintfA(s,"ORD %08lx %08lx %08lx %08lx\r\n",tid,stack[0],stack[1],name);line(s);return !failed;}
    for(i=0;i<256;i++) {
        if(name+i<name||!readmem(name+i,&c,1))return FALSE;
        if(!c)break;
        hex[i*2]=digits[c>>4];hex[i*2+1]=digits[c&15];
    }
    if(i==256)return FALSE;
    hex[i*2]=0;wsprintfA(s,"%s %08lx %08lx %08lx %s\r\n",which?"PROC":"LOAD",tid,stack[0],which?stack[1]:0,hex);line(s);return !failed;
}
static BOOL ownedbreak(DEBUG_EVENT *e,DWORD index) {
    CONTEXT c;THREAD *t=thread(e->dwThreadId);
    if(!t||step_id||!bp[index].armed||++requests>4096)return FALSE;
    zero(&c,sizeof(c));c.ContextFlags=CONTEXT_CONTROL;
    if(!GetThreadContext(t->h,&c)||c.Eip!=bp[index].address+1||(c.EFlags&0x100))return FALSE;
    if(!request(index,t->id,&c)||!holdothers(t->id)||!bytewrite(bp[index].address,bp[index].original))return FALSE;
    bp[index].armed=FALSE;c.Eip--;c.EFlags|=0x100;
    if(!SetThreadContext(t->h,&c))return FALSE;
    step_id=t->id;step_bp=index;return TRUE;
}
static BOOL stepped(DEBUG_EVENT *e) {
    THREAD *t=thread(e->dwThreadId);CONTEXT c;
    if(!t||e->dwThreadId!=step_id)return FALSE;
    zero(&c,sizeof(c));c.ContextFlags=CONTEXT_CONTROL;
    if(!GetThreadContext(t->h,&c))return FALSE;
    c.EFlags&=~0x100;
    if(!SetThreadContext(t->h,&c)||!bytewrite(bp[step_bp].address,0xcc))return FALSE;
    bp[step_bp].armed=TRUE;step_id=0;return releaseothers();
}
void WINAPI mainCRTStartup(void) {
    STARTUPINFOA si;PROCESS_INFORMATION pi;DEBUG_EVENT e;DWORD status,count=0,i,exitcode=99,killat=0;char cmd[]="\"C:\\xwn599-kit\\game\\RCT.EXE\"";HANDLE pidfile;DWORD done;
    logfile=CreateFileA("C:\\xwn599\\trace.txt",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,0,0);
    if(logfile==INVALID_HANDLE_VALUE)ExitProcess(90);
    zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
    if(!CreateProcessA("C:\\xwn599-kit\\game\\RCT.EXE",cmd,0,0,FALSE,DEBUG_ONLY_THIS_PROCESS,0,"C:\\xwn599-kit\\game",&si,&pi)) {event("CREATE_FAIL",GetLastError(),0,0);CloseHandle(logfile);ExitProcess(91);}
    process=pi.hProcess;CloseHandle(pi.hThread);started=GetTickCount();
    pidfile=CreateFileA("C:\\xwn599\\gamepid.bin",GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
    if(pidfile==INVALID_HANDLE_VALUE)failed=TRUE;
    else {if(!WriteFile(pidfile,&pi.dwProcessId,4,&done,0)||done!=4||!FlushFileBuffers(pidfile))failed=TRUE;CloseHandle(pidfile);}
    while(!exited) {
        if(GetTickCount()-started>360000||count>10000)failed=TRUE;
        if(failed&&!killat) {event("TERMINATE",GetLastError(),requests,step_id);TerminateProcess(process,97);killat=GetTickCount();}
        if(killat&&GetTickCount()-killat>5000)break;
        if(!WaitForDebugEvent(&e,100)) {if(GetLastError()!=ERROR_SEM_TIMEOUT)failed=TRUE;continue;}
        count++;status=DBG_CONTINUE;
        switch(e.dwDebugEventCode) {
        case CREATE_PROCESS_DEBUG_EVENT:
            if(e.dwProcessId!=pi.dwProcessId||!addthread(e.dwThreadId,e.u.CreateProcessInfo.hThread))failed=TRUE;
            if(e.u.CreateProcessInfo.hFile)CloseHandle(e.u.CreateProcessInfo.hFile);
            event("IMAGE",(DWORD)e.u.CreateProcessInfo.lpBaseOfImage,e.dwThreadId,0);break;
        case CREATE_THREAD_DEBUG_EVENT:
            if(!addthread(e.dwThreadId,e.u.CreateThread.hThread))failed=TRUE;
            event("THREAD",e.dwThreadId,0,0);break;
        case EXIT_THREAD_DEBUG_EVENT: {
            THREAD *t=thread(e.dwThreadId);if(!t||t->held||step_id==e.dwThreadId)failed=TRUE;
            if(t){t->id=0;t->h=0;}break;
        }
        case LOAD_DLL_DEBUG_EVENT:
            event("DLL",(DWORD)e.u.LoadDll.lpBaseOfDll,0,0);
            if(e.u.LoadDll.hFile)CloseHandle(e.u.LoadDll.hFile);
            break;
        case EXCEPTION_DEBUG_EVENT:
            status=DBG_EXCEPTION_NOT_HANDLED;
            if(!failed&&e.u.Exception.ExceptionRecord.ExceptionCode==EXCEPTION_BREAKPOINT) {
                if(!initial) {initial=TRUE;if(!arm())failed=TRUE;status=DBG_CONTINUE;}
                else for(i=0;i<2;i++)if((DWORD)e.u.Exception.ExceptionRecord.ExceptionAddress==bp[i].address) {if(!ownedbreak(&e,i))failed=TRUE;status=DBG_CONTINUE;break;}
            }else if(!failed&&e.u.Exception.ExceptionRecord.ExceptionCode==EXCEPTION_SINGLE_STEP&&step_id) {
                if(!stepped(&e))failed=TRUE;
                status=DBG_CONTINUE;
            }
            if(status==DBG_EXCEPTION_NOT_HANDLED)event("EXCEPTION",e.u.Exception.ExceptionRecord.ExceptionCode,e.u.Exception.dwFirstChance,e.dwThreadId);
            break;
        case EXIT_PROCESS_DEBUG_EVENT:exitcode=e.u.ExitProcess.dwExitCode;exited=TRUE;break;
        case RIP_EVENT:failed=TRUE;break;
        default:break;
        }
        if(!ContinueDebugEvent(e.dwProcessId,e.dwThreadId,status))failed=TRUE;
    }
    event("END",exitcode,requests,failed?1:0);
    FlushFileBuffers(logfile);CloseHandle(logfile);CloseHandle(process);
    ExitProcess(!failed&&exited&&initial&&requests&&exitcode==0?0:1);
}
