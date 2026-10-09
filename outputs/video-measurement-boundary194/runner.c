/* Five unchanged v8 probes with observable setup wait and actual measurement checkpoints. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include "restart_gate.h"
#include "setup_gate.h"
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static WAIT_INSTALL WaitInstall;
static HANDLE Log;
static HANDLE Console;
static void record(const char *s) {
    DWORD n=0,w;while(s[n])n++;
    if(!WriteFile(Log,s,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(3);
    if(Console&&Console!=INVALID_HANDLE_VALUE)WriteFile(Console,s,n,&w,NULL);
}
static void gate_record(void *context,const char *label,uint32_t value);
/* Snapshot the actual system log without changing its sharing or installer policy. */
static void timestamp(const char *label) {
    FILETIME t;char line[128];GetSystemTimeAsFileTime(&t);
    wsprintfA(line,"%s %lu %lu\r\n",label,t.dwLowDateTime,t.dwHighDateTime);record(line);
}
static BYTE CheckpointBuffer[4096];
static void checkpoint(const char *base,const char *name,const char *label) {
    char source[MAX_PATH],dest[MAX_PATH];DWORD n,size,high,status,left,got,wrote;
    HANDLE f,out;
    status=WaitInstall(0);gate_record(NULL,label,status);
    if(status){record("FAIL_CHECKPOINT_SETUP_PENDING\r\n");ExitProcess(18);}
    n=GetWindowsDirectoryA(source,sizeof(source));
    if(!n||n>=sizeof(source)-16){record("FAIL_WINDOWS_DIRECTORY\r\n");ExitProcess(19);}
    wsprintfA(source+n,"\\setupapi.log");
    f=CreateFileA(source,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    if(f==INVALID_HANDLE_VALUE){record("FAIL_SETUP_LOG_OPEN\r\n");ExitProcess(20);}
    high=0;SetLastError(ERROR_SUCCESS);size=GetFileSize(f,&high);status=GetLastError();
    if(status||high||size==INVALID_FILE_SIZE||size>16UL*1024UL*1024UL){record("FAIL_SETUP_LOG_SIZE\r\n");ExitProcess(21);}
    wsprintfA(dest,"%s\\%s",base,name);
    out=CreateFileA(dest,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(out==INVALID_HANDLE_VALUE){record("FAIL_SETUP_LOG_CREATE\r\n");ExitProcess(22);}
    for(left=size;left;) {
        n=left<sizeof(CheckpointBuffer)?left:sizeof(CheckpointBuffer);
        if(!ReadFile(f,CheckpointBuffer,n,&got,NULL)||got!=n){record("FAIL_SETUP_LOG_READ\r\n");ExitProcess(23);}
        if(!WriteFile(out,CheckpointBuffer,n,&wrote,NULL)||wrote!=n){record("FAIL_SETUP_LOG_WRITE\r\n");ExitProcess(24);}
        left-=n;
    }
    if(!ReadFile(f,CheckpointBuffer,1,&got,NULL)||got){record("FAIL_SETUP_LOG_GREW\r\n");ExitProcess(25);}
    high=0;SetLastError(ERROR_SUCCESS);n=GetFileSize(f,&high);status=GetLastError();
    if(status||high||n!=size){record("FAIL_SETUP_LOG_CHANGED_SIZE\r\n");ExitProcess(26);}
    if(!FlushFileBuffers(out)){record("FAIL_SETUP_LOG_FLUSH\r\n");ExitProcess(27);}
    CloseHandle(out);CloseHandle(f);
    status=WaitInstall(0);gate_record(NULL,"INSTALL_AFTER_CHECKPOINT",status);
    if(status){record("FAIL_CHECKPOINT_SETUP_PENDING\r\n");ExitProcess(18);}
    timestamp("CHECKPOINT_TIME");gate_record(NULL,"CHECKPOINT_SOURCE_BYTES",size);
}
static uint32_t query_install(void *context,uint32_t timeout) {(void)context;return WaitInstall(timeout);}
static int request_restart(void *context) {(void)context;return ExitWindowsEx(EWX_REBOOT,0)!=0;}
static void gate_record(void *context,const char *label,uint32_t value) {
    char line[128];(void)context;wsprintfA(line,"%s %lu\r\n",label,(DWORD)value);record(line);
}
static uint32_t now_tick(void *context) {(void)context;return GetTickCount();}
static void pause_poll(void *context,uint32_t ms) {(void)context;Sleep(ms);}
void WINAPI mainCRTStartup(void) {
    char base[MAX_PATH],path[MAX_PATH],command[MAX_PATH],line[64];DWORD n,i,status;
    HANDLE token;TOKEN_PRIVILEGES tp;
    n=GetModuleFileNameA(NULL,base,sizeof(base));
    if(!n||n>=sizeof(base)-64)ExitProcess(2);
    while(n&&base[n-1]!='\\')n--;
    if(!n)ExitProcess(2);
    base[n-1]=0;
    wsprintfA(path,"%s\\attempt.log",base);
    Console=GetStdHandle(STD_OUTPUT_HANDLE);
    Log=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
    record("ATTEMPT_ONCE\r\n");
    WaitInstall=(WAIT_INSTALL)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");
    if(!WaitInstall){record("FAIL_INSTALL_EXPORT\r\n");ExitProcess(12);}
    record("WAITING_FOR_SETUP_IDLE\r\n");
    record("Close known hardware wizards without disabling devices. Leave this window visible.\r\n");
    record("Waiting up to fifteen minutes for five seconds of actual setup idle.\r\n");
    timestamp("SETUP_WAIT_START_TIME");
    status=(DWORD)xwn_wait_setup_idle(NULL,query_install,now_tick,pause_poll,gate_record,900000,5000,250);
    if(status){CloseHandle(Log);ExitProcess(status==1?15:16);}
    checkpoint(base,"setup-before.log","INSTALL_BEFORE_CHECKPOINT");
    timestamp("MEASUREMENT_START_TIME");
    record("MEASUREMENT_BEGIN\r\n");
    for(i=0;i<5;i++) {
        STARTUPINFOA si={0};PROCESS_INFORMATION pi={0};
        status=WaitInstall(0);gate_record(NULL,"INSTALL_BEFORE_SAMPLE",status);
        if(status){record("FAIL_INSTALL_DURING_MEASUREMENT\r\n");CloseHandle(Log);ExitProcess(17);}
        wsprintfA(path,"%s\\sample%lu",base,i);
        if(!CreateDirectoryA(path,NULL)){record("FAIL_DIRECTORY\r\n");ExitProcess(4);}
        wsprintfA(command,"%s\\replay.exe",base);si.cb=sizeof(si);
        if(!CreateProcessA(command,command,NULL,NULL,FALSE,0,NULL,path,&si,&pi)) {
            record("FAIL_CREATE_PROCESS\r\n");ExitProcess(5);
        }
        CloseHandle(pi.hThread);
        if(WaitForSingleObject(pi.hProcess,180000)!=WAIT_OBJECT_0||!GetExitCodeProcess(pi.hProcess,&status)) {
            record("FAIL_WAIT\r\n");ExitProcess(6);
        }
        CloseHandle(pi.hProcess);
        if(status!=0){record("FAIL_REPLAY_EXIT\r\n");ExitProcess(7);}
        wsprintfA(line,"SAMPLE_EXIT_ZERO %lu\r\n",i);record(line);
        status=WaitInstall(0);gate_record(NULL,"INSTALL_AFTER_SAMPLE",status);
        if(status){record("FAIL_INSTALL_DURING_MEASUREMENT\r\n");CloseHandle(Log);ExitProcess(17);}
        Sleep(1000);
    }
    checkpoint(base,"setup-after.log","INSTALL_BEFORE_CHECKPOINT");
    timestamp("MEASUREMENT_END_TIME");
    Sleep(30000);
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(8);
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(9);
    SetLastError(ERROR_SUCCESS);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)ExitProcess(10);
    CloseHandle(token);
    status=(DWORD)xwn_guarded_restart(NULL,query_install,request_restart,gate_record);
    if(status){CloseHandle(Log);ExitProcess(status==1?13:(status==2?14:11));}
    CloseHandle(Log);ExitProcess(0);
}
