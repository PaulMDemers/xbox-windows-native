/* Explicit child completion + genuine setup idle + unchanged normal restart gate. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include "../setup-wizard-automation201/restart_gate201.h"
#include "../setup-wizard-automation201/setup_gate201.h"
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static WAIT_INSTALL WaitInstall;
static HANDLE Log;
static void record(void *context,const char *label,uint32_t value) {
    char line[192];DWORD w,n;(void)context;wsprintfA(line,"%s %lu\r\n",label,(DWORD)value);n=lstrlenA(line);
    if(!WriteFile(Log,line,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(91);
}
static uint32_t query(void *context,uint32_t timeout) {(void)context;return WaitInstall(timeout);}
static uint32_t now(void *context) {(void)context;return GetTickCount();}
static void pause_poll(void *context,uint32_t ms) {(void)context;Sleep(ms);}
static int restart(void *context) {(void)context;return ExitWindowsEx(EWX_REBOOT,0)!=0;}
void WINAPI mainCRTStartup(void) {
    char base[MAX_PATH],path[MAX_PATH],command[MAX_PATH];DWORD n,status;
    STARTUPINFOA si={0};PROCESS_INFORMATION pi={0};HANDLE token;TOKEN_PRIVILEGES tp;
    n=GetModuleFileNameA(NULL,base,sizeof(base));if(!n||n>=sizeof(base)-64)ExitProcess(90);
    while(n&&base[n-1]!='\\')n--;
    if(!n)ExitProcess(90);
    base[n-1]=0;
    wsprintfA(path,"%s\\runner207.log",base);
    Log=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
    record(NULL,"RUNNER207",1);
    WaitInstall=(WAIT_INSTALL)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");
    if(!WaitInstall){record(NULL,"FAIL_INSTALL_EXPORT",0);ExitProcess(92);}
    wsprintfA(path,"%s\\wizard.exe",base);wsprintfA(command,"%s /cancel-physical",path);si.cb=sizeof(si);
    if(!CreateProcessA(path,command,NULL,NULL,FALSE,0,NULL,base,&si,&pi)){record(NULL,"FAIL_CREATE_HELPER",GetLastError());ExitProcess(93);}
    CloseHandle(pi.hThread);record(NULL,"HELPER_STARTED",pi.dwProcessId);
    status=WaitForSingleObject(pi.hProcess,150000);record(NULL,"HELPER_JOIN_RESULT",status);
    if(status!=WAIT_OBJECT_0){record(NULL,"RESTART_BLOCKED_HELPER_UNJOINED",status);ExitProcess(94);}
    if(!GetExitCodeProcess(pi.hProcess,&status)){record(NULL,"FAIL_HELPER_EXIT_QUERY",GetLastError());ExitProcess(95);}
    CloseHandle(pi.hProcess);record(NULL,"HELPER_EXIT",status);
    if(status){record(NULL,"RESTART_BLOCKED_HELPER_FAILURE",status);ExitProcess(96);}
    status=xwn_wait_setup_idle(NULL,query,now,pause_poll,record,30000,5000,250);
    if(status){record(NULL,"RESTART_BLOCKED_IDLE_GUARD",status);ExitProcess(97);}
    wsprintfA(path,"%s\\state.exe",base);si.cb=sizeof(si);
    if(!CreateProcessA(path,NULL,NULL,NULL,FALSE,0,NULL,base,&si,&pi)){record(NULL,"FAIL_CREATE_STATE",GetLastError());ExitProcess(107);}
    CloseHandle(pi.hThread);record(NULL,"STATE_STARTED",pi.dwProcessId);
    status=WaitForSingleObject(pi.hProcess,30000);record(NULL,"STATE_JOIN_RESULT",status);
    if(status!=WAIT_OBJECT_0)ExitProcess(108);
    if(!GetExitCodeProcess(pi.hProcess,&status))ExitProcess(109);
    CloseHandle(pi.hProcess);record(NULL,"STATE_EXIT",status);if(status)ExitProcess(110);
    wsprintfA(path,"%s\\probe.exe",base);si.cb=sizeof(si);
    if(!CreateProcessA(path,NULL,NULL,NULL,FALSE,0,NULL,base,&si,&pi)){record(NULL,"FAIL_CREATE_PROBE",GetLastError());ExitProcess(102);}
    CloseHandle(pi.hThread);record(NULL,"PROBE_STARTED",pi.dwProcessId);
    status=WaitForSingleObject(pi.hProcess,180000);record(NULL,"PROBE_JOIN_RESULT",status);
    if(status!=WAIT_OBJECT_0)ExitProcess(103);
    if(!GetExitCodeProcess(pi.hProcess,&status))ExitProcess(104);
    CloseHandle(pi.hProcess);record(NULL,"PROBE_EXIT",status);
    if(status)ExitProcess(105);
    status=xwn_wait_setup_idle(NULL,query,now,pause_poll,record,30000,5000,250);
    if(status)ExitProcess(106);
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(98);
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(99);
    SetLastError(ERROR_SUCCESS);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)ExitProcess(100);
    CloseHandle(token);status=xwn_guarded_restart(NULL,query,restart,record);
    CloseHandle(Log);ExitProcess(status?101:0);
}
