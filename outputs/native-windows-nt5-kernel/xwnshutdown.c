/* Request an ordinary Windows shutdown after diagnostics on a private fixture. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
void WINAPI mainCRTStartup(void)
{
    HANDLE token,log; TOKEN_PRIVILEGES privileges; DWORD error=0,written;
    log=CreateFileA("C:\\xwn-shutdown.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)) error=GetLastError();
    else {
        privileges.PrivilegeCount=1;
        if(!LookupPrivilegeValueA(NULL,"SeShutdownPrivilege",&privileges.Privileges[0].Luid)) error=GetLastError();
        else {
            privileges.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;SetLastError(0);
            if(!AdjustTokenPrivileges(token,FALSE,&privileges,0,NULL,NULL)) error=GetLastError();
            else error=GetLastError();
        }
        CloseHandle(token);
    }
    if(error) {
        const char *s="Shutdown privilege unavailable\r\n";
        WriteFile(log,s,lstrlenA(s),&written,NULL);CloseHandle(log);ExitProcess(error);
    }
    {
        const char *s="Privilege enabled. Requesting orderly shutdown in 30 seconds.\r\n";
        WriteFile(log,s,lstrlenA(s),&written,NULL);FlushFileBuffers(log);CloseHandle(log);
    }
    Sleep(30000);
    if(!ExitWindowsEx(EWX_SHUTDOWN|EWX_FORCE,0)) ExitProcess(GetLastError());
    Sleep(60000);ExitProcess(0);
}
