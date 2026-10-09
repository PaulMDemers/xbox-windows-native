/* NEW actual enabled Cancel control BN_CLICKED notification; actual queue idle required, no device/policy edit. */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>
#include <commctrl.h>
#include "policy.h"
typedef LONG (WINAPI *QUERY_PROCESS)(HANDLE,ULONG,PVOID,ULONG,PULONG);
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static QUERY_PROCESS Query;
static WAIT_INSTALL Wait;
static HANDLE Log;
static DWORD Written,Started,Actions,Mode,Emulator,CurrentPid,CurrentTarget,SeenWindows;
static HANDLE CurrentProcess;
static char OriginalCommand[512],Command[512];
static HWND PendingWindow;
static DWORD PendingPid;
static FILETIME PendingCreation;
static FILETIME CurrentCreation;
static DWORD ActedPid[8];
static FILETIME ActedCreation[8];
static void record(const char *label,DWORD a,DWORD b,DWORD c) {
    char line[192];DWORD n,w=0;wsprintfA(line,"%s %lu %lu %lu\r\n",label,a,b,c);n=lstrlenA(line);
    if(n>1024*1024-Written||!WriteFile(Log,line,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(91);
    Written+=n;
}
static BOOL remote(HANDLE p,DWORD at,void *data,DWORD size) {
    SIZE_T n=0;if(at<0x10000||at>=0x7fff0000||size>0x7fff0000-at)return FALSE;
    return ReadProcessMemory(p,(void *)at,data,size,&n)&&n==size;
}
static BOOL getcommand(HANDLE p,char *result) {
    DWORD info[6]={0},params=0,i;struct {WORD length,max;DWORD buffer;} text;static WCHAR wide[512];
    if(Query(p,0,info,sizeof(info),NULL)<0||info[1]>0x7fff0000-0x10||
       !remote(p,info[1]+0x10,&params,4)||params>0x7fff0000-0x40||
       !remote(p,params+0x40,&text,sizeof(text))||text.length>text.max||(text.length&1)||
       !text.length||text.length>=sizeof(wide)||!remote(p,text.buffer,wide,text.length))return FALSE;
    for(i=0;i<text.length/2;i++){if(!wide[i]||wide[i]>127)return FALSE;result[i]=(char)wide[i];}
    result[i]=0;return TRUE;
}
static BOOL creation(HANDLE p,FILETIME *t) {FILETIME exit,kernel,user;return GetProcessTimes(p,t,&exit,&kernel,&user);}
static BOOL same(FILETIME a,FILETIME b) {return a.dwLowDateTime==b.dwLowDateTime&&a.dwHighDateTime==b.dwHighDateTime;}
static BOOL text(HWND h,char *buf,DWORD cap) {
    DWORD_PTR result=0;buf[0]=0;
    if(!SendMessageTimeoutA(h,WM_GETTEXT,cap,(LPARAM)buf,SMTO_ABORTIFHUNG|SMTO_BLOCK,100,&result))return FALSE;
    buf[cap-1]=0;return result<cap-1;
}
static BOOL inspect(HWND h,struct xwn_window201 *w) {
    static char title[128],cls[32],bt[32],bc[32];HWND b=GetDlgItem(h,IDCANCEL);DWORD pid=0,bpid=0;
    w->tid=GetWindowThreadProcessId(h,&pid);GetWindowThreadProcessId(b,&bpid);
    if(!IsWindow(h)||!IsWindow(b)||GetParent(b)!=h||!GetClassNameA(h,cls,sizeof(cls))||
       !GetClassNameA(b,bc,sizeof(bc))||!text(h,title,sizeof(title))||!text(b,bt,sizeof(bt)))return FALSE;
    w->pid=pid;w->hwnd=(DWORD)h;w->button=(DWORD)b;w->visible=IsWindowVisible(h);w->enabled=IsWindowEnabled(h);
    w->button_visible=IsWindowVisible(b);w->button_enabled=IsWindowEnabled(b);w->button_id=GetDlgCtrlID(b);w->button_pid=bpid;
    w->title=title;w->cls=cls;w->button_text=bt;w->button_class=bc;return TRUE;
}
static BOOL CALLBACK top(HWND h,LPARAM unused) {
    struct xwn_window201 w;DWORD pid=0,i;FILETIME stamp;DWORD_PTR result=0;(void)unused;
    GetWindowThreadProcessId(h,&pid);if(pid!=CurrentPid)return TRUE;
    if(++SeenWindows>256||GetTickCount()-Started>=120000){record("FAIL_WINDOW_BOUND",SeenWindows,0,0);ExitProcess(93);}
    if(!inspect(h,&w)||!xwn_eligible(&w,CurrentPid))return TRUE;
    record("MATCHED_WINDOW",CurrentPid,(DWORD)h,CurrentTarget);
    if(!Mode)return TRUE;
    if(PendingWindow){record("FAIL_DUPLICATE_ELIGIBLE",PendingPid,CurrentPid,0);ExitProcess(94);}
    for(i=0;i<Actions;i++)if(ActedPid[i]==CurrentPid&&same(ActedCreation[i],CurrentCreation)){record("FAIL_DUPLICATE_OWNER",CurrentPid,CurrentTarget,0);ExitProcess(101);}
    record("CANCEL_OWNER",CurrentPid,CurrentCreation.dwLowDateTime,CurrentCreation.dwHighDateTime);
    record("CANCEL_INTENT",CurrentPid,(DWORD)h,CurrentTarget);
    /* Revalidate after durable logging, against the still-open original process object. */
    if(WaitForSingleObject(CurrentProcess,0)!=WAIT_TIMEOUT||!creation(CurrentProcess,&stamp)||!same(stamp,CurrentCreation)||
       !getcommand(CurrentProcess,Command)||!xwn_equal(Command,OriginalCommand)||
       !inspect(h,&w)||!xwn_eligible(&w,CurrentPid)){record("FAIL_REVALIDATION",CurrentPid,0,0);ExitProcess(95);}
    PendingWindow=h;PendingPid=CurrentPid;PendingCreation=stamp;
    if(Actions>=8){record("FAIL_ACTION_BOUND",Actions,0,0);ExitProcess(96);}
    ActedPid[Actions]=CurrentPid;ActedCreation[Actions]=stamp;Actions++;
    if(!SendMessageTimeoutA(h,WM_COMMAND,MAKEWPARAM(IDCANCEL,BN_CLICKED),(LPARAM)w.button,SMTO_ABORTIFHUNG|SMTO_BLOCK,1000,&result)){
        record("FAIL_CANCEL_SEND_UNCERTAIN",PendingPid,GetLastError(),0);ExitProcess(97);
    }
    record("CANCEL_SENT",CurrentPid,(DWORD)h,CurrentTarget);return FALSE;
}
static void poll(void) {
    HANDLE snap;PROCESSENTRY32 e;DWORD count=0;FILETIME stamp;
    if(PendingWindow) {
        HANDLE p=OpenProcess(PROCESS_QUERY_INFORMATION|SYNCHRONIZE,FALSE,PendingPid);
        BOOL old=p&&WaitForSingleObject(p,0)==WAIT_TIMEOUT&&creation(p,&stamp)&&same(stamp,PendingCreation);
        if(p)CloseHandle(p);
        if(old&&IsWindow(PendingWindow)){record("AWAIT_CANCEL_CLOSE",PendingPid,(DWORD)PendingWindow,0);return;}
        record("CANCEL_CLOSED_OWNER",PendingPid,PendingCreation.dwLowDateTime,PendingCreation.dwHighDateTime);
        record("CANCEL_WINDOW_CLOSED",PendingPid,(DWORD)PendingWindow,0);PendingWindow=NULL;
    }
    snap=CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS,0);if(snap==INVALID_HANDLE_VALUE){record("FAIL_SNAPSHOT",GetLastError(),0,0);ExitProcess(98);}
    e.dwSize=sizeof(e);SeenWindows=0;
    if(Process32First(snap,&e))do {
        if(++count>1024){record("FAIL_PROCESS_BOUND",count,0,0);ExitProcess(99);}
        if(!xwn_equal(e.szExeFile,"rundll32.exe"))continue;
        CurrentProcess=OpenProcess(PROCESS_QUERY_INFORMATION|PROCESS_VM_READ|SYNCHRONIZE,FALSE,e.th32ProcessID);
        if(!CurrentProcess)continue;
        if(creation(CurrentProcess,&CurrentCreation)&&getcommand(CurrentProcess,OriginalCommand)) {
            CurrentTarget=xwn_target(OriginalCommand,Emulator);CurrentPid=e.th32ProcessID;
            record("RUNDLL_COMMAND_TARGET",CurrentPid,CurrentTarget,0);
            if(CurrentTarget)EnumWindows(top,0);
        }else record("OWNER_UNREADABLE",e.th32ProcessID,GetLastError(),0);
        CloseHandle(CurrentProcess);CurrentProcess=NULL;
        if(PendingWindow)break;
    }while(Process32Next(snap,&e));
    CloseHandle(snap);
}
void WINAPI mainCRTStartup(void) {
    char path[MAX_PATH],base[MAX_PATH];DWORD n,idle=0,zero=0,state,elapsed;BOOL havezero=FALSE;
    const char *arg=GetCommandLineA();
    /* Arguments are exclusive whole command tails; default observation never sends input. */
    while(*arg&&*arg!=' ')arg++;
    while(*arg==' ')arg++;
    if(xwn_equal(arg,"/observe-emulator")){Mode=0;Emulator=1;}
    else if(xwn_equal(arg,"/cancel-emulator")){Mode=1;Emulator=1;}
    else if(xwn_equal(arg,"/cancel-physical")){Mode=1;Emulator=0;}
    else ExitProcess(90);
    n=GetModuleFileNameA(NULL,base,sizeof(base));if(!n||n>=sizeof(base)-32)ExitProcess(90);
    while(n&&base[n-1]!='\\')n--;
    if(!n)ExitProcess(90);
    base[n]=0;
    wsprintfA(path,"%swizard201.log",base);
    Log=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
    Query=(QUERY_PROCESS)GetProcAddress(GetModuleHandleA("ntdll.dll"),"NtQueryInformationProcess");
    Wait=(WAIT_INSTALL)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");
    if(!Query||!Wait){record("FAIL_EXPORT",0,0,0);ExitProcess(92);}
    Started=GetTickCount();record("START201",Mode,Emulator,120000);
    for(;;) {
        elapsed=GetTickCount()-Started;if(elapsed>=120000){record("TIMEOUT201",Mode,Actions,elapsed);break;}
        state=Wait(0);record("INSTALL_STATE",state,elapsed,Actions);
        if(state==WAIT_FAILED){record("FAIL_INSTALL_QUERY",GetLastError(),0,0);ExitProcess(100);}
        poll();
        if(state==WAIT_OBJECT_0&&!PendingWindow){if(!havezero){zero=GetTickCount();havezero=TRUE;}idle=GetTickCount()-zero;
            if(idle>=5000){record("IDLE201",idle,Actions,GetTickCount()-Started);CloseHandle(Log);ExitProcess(0);}}
        else havezero=FALSE;
        Sleep(250);
    }
    CloseHandle(Log);ExitProcess(15);
}
