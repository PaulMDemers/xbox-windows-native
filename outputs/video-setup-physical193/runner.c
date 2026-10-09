/* Five unchanged v8 probes after observed setup idle; unchanged guarded restart. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include "restart_gate.h"
#include "setup_gate.h"
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static WAIT_INSTALL WaitInstall;
static HANDLE Log;
static void record(const char *s) {
    DWORD n=0,w;while(s[n])n++;
    if(!WriteFile(Log,s,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(3);
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
    if(!n||n>=sizeof(base)-32)ExitProcess(2);
    while(n&&base[n-1]!='\\')n--;
    if(!n)ExitProcess(2);
    base[n-1]=0;
    wsprintfA(path,"%s\\attempt.log",base);
    Log=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
    record("ATTEMPT_ONCE\r\n");
    WaitInstall=(WAIT_INSTALL)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");
    if(!WaitInstall){record("FAIL_INSTALL_EXPORT\r\n");ExitProcess(12);}
    record("WAITING_FOR_SETUP_IDLE\r\n");
    status=(DWORD)xwn_wait_setup_idle(NULL,query_install,now_tick,pause_poll,gate_record,300000,5000,250);
    if(status){CloseHandle(Log);ExitProcess(status==1?15:16);}
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
