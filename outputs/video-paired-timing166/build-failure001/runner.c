/* Five independent invocations of the unchanged v3 probe; one normal restart. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log;
static void record(const char *s) {
    DWORD n=0,w;while(s[n])n++;
    if(!WriteFile(Log,s,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(3);
}
void WINAPI mainCRTStartup(void) {
    char base[MAX_PATH],path[MAX_PATH],command[MAX_PATH],line[64];DWORD n,i,status;
    HANDLE token;TOKEN_PRIVILEGES tp;
    n=GetModuleFileNameA(NULL,base,sizeof(base));
    if(!n||n>=sizeof(base)-32)ExitProcess(2);
    while(n&&base[n-1]!='\\')n--;
    if(!n)ExitProcess(2);base[n-1]=0;
    wsprintfA(path,"%s\\attempt.log",base);
    Log=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
    record("ATTEMPT_ONCE\r\n");
    for(i=0;i<5;i++) {
        STARTUPINFOA si={0};PROCESS_INFORMATION pi={0};
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
        Sleep(1000);
    }
    Sleep(30000);
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(8);
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(9);
    SetLastError(ERROR_SUCCESS);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)ExitProcess(10);
    CloseHandle(token);record("NORMAL_RESTART_REQUEST\r\n");
    if(!ExitWindowsEx(EWX_REBOOT,0)){record("FAIL_RESTART\r\n");ExitProcess(11);}
    CloseHandle(Log);ExitProcess(0);
}
