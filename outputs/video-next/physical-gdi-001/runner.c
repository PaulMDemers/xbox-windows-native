/* One-shot replay launcher: normal reboot only after successful child completion. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log;
static void record(const char *s) {
    DWORD n=0,w;
    while(s[n])n++;
    if(!WriteFile(Log,s,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(3);
    WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),s,n,&w,NULL);
}
void WINAPI mainCRTStartup(void) {
    STARTUPINFOA si={0};PROCESS_INFORMATION pi={0};HANDLE token;
    TOKEN_PRIVILEGES tp;DWORD status;
    char command[]="C:\\xwngdi01\\replay.exe";
    Log=CreateFileA("C:\\xwngdi01\\attempt.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,
                   CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
    record("ATTEMPT_ONCE\r\n");si.cb=sizeof(si);
    if(!CreateProcessA(command,command,NULL,NULL,FALSE,0,NULL,"C:\\xwngdi01",&si,&pi)) {
        record("FAIL_CREATE_PROCESS\r\n");ExitProcess(4);
    }
    CloseHandle(pi.hThread);
    if(WaitForSingleObject(pi.hProcess,INFINITE)!=WAIT_OBJECT_0||
       !GetExitCodeProcess(pi.hProcess,&status)) {
        record("FAIL_WAIT\r\n");ExitProcess(5);
    }
    CloseHandle(pi.hProcess);
    if(status!=0){record("FAIL_REPLAY_EXIT\r\n");ExitProcess(6);}
    record("REPLAY_EXIT_ZERO\r\n");
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)) {
        record("FAIL_TOKEN\r\n");ExitProcess(7);
    }
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)) {
        record("FAIL_LOOKUP\r\n");ExitProcess(8);
    }
    SetLastError(ERROR_SUCCESS);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS) {
        record("FAIL_PRIVILEGE\r\n");ExitProcess(9);
    }
    CloseHandle(token);record("NORMAL_RESTART_REQUEST\r\n");
    if(!ExitWindowsEx(EWX_REBOOT,0)){record("FAIL_RESTART\r\n");ExitProcess(10);}
    CloseHandle(Log);ExitProcess(0);
}

