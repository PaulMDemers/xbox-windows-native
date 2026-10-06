/* Ordinary subsequent-boot check: idle, check pending installation, normal restart. No UI actions. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log;
static void record(const char *s,DWORD value) {
 char line[160];DWORD n,w;
 n=(DWORD)wsprintfA(line,"%s %lu\r\n",s,value);
 if(!WriteFile(Log,line,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(91);
}
static void fatal(const char *s){record(s,GetLastError());ExitProcess(92);}
void WINAPI mainCRTStartup(void) {
 DWORD start,pending;HANDLE token;TOKEN_PRIVILEGES tp;
 HMODULE setup;typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);WAIT_INSTALL waitInstall;
 Log=CreateFileA("C:\\xwnidle\\repeat.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
 setup=LoadLibraryA("setupapi.dll");
 waitInstall=setup?(WAIT_INSTALL)GetProcAddress(setup,"CMP_WaitNoPendingInstallEvents"):NULL;
 if(!waitInstall)fatal("FAIL_PENDING_API");
 record("ATTEMPT_ONCE",120000);start=GetTickCount();
 Sleep(120000);record("IDLE_COMPLETE_MS",GetTickCount()-start);
 pending=waitInstall(0);
 if(pending!=WAIT_OBJECT_0){record("RESTART_BLOCKED_PENDING_INSTALL",pending);CloseHandle(Log);ExitProcess(93);}
 record("INSTALL_QUEUE_IDLE_BEFORE_RESTART",pending);
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))fatal("FAIL_TOKEN");
 tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
 if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))fatal("FAIL_LOOKUP");
 SetLastError(ERROR_SUCCESS);
 if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)fatal("FAIL_PRIVILEGE");
 CloseHandle(token);record("NORMAL_RESTART_REQUEST",0);
 if(!ExitWindowsEx(EWX_REBOOT,0))fatal("FAIL_RESTART");
 CloseHandle(Log);ExitProcess(0);
}
