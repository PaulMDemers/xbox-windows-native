/* One-shot, emulator-only installation. Failure leaves the guest for inspection. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
typedef BOOL (WINAPI *UPDATE)(HWND,LPCSTR,LPCSTR,DWORD,PBOOL);
static HANDLE Log;
static void record(const char *s) {
    DWORD n=0,w;
    while(s[n])n++;
    if(!WriteFile(Log,s,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(3);
}
static void number(DWORD v) {
    char s[]="00000000\r\n"; unsigned i;
    for(i=0;i<8;i++)s[7-i]="0123456789abcdef"[(v>>(4*i))&15];
    record(s);
}
void WINAPI mainCRTStartup(void) {
    HMODULE module; UPDATE update; BOOL reboot=FALSE,ok; DWORD error;
    HANDLE token; TOKEN_PRIVILEGES tp;
    Log=CreateFileA("C:\\xwninf01\\install.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,
                   CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
    record("INSTALL_ATTEMPT_ONCE\r\n");
    module=LoadLibraryA("newdev.dll");
    if(!module){record("FAIL_LOAD_NEWDEV\r\n");number(GetLastError());ExitProcess(4);}
    update=(UPDATE)GetProcAddress(module,"UpdateDriverForPlugAndPlayDevicesA");
    if(!update){record("FAIL_EXPORT\r\n");ExitProcess(5);}
    record("UPDATE_BEGIN\r\n");
    SetLastError(0);
    ok=update(NULL,"PCI\\VEN_10DE&DEV_02A0","C:\\xwninf01\\xboxvnt5.inf",0,&reboot);
    error=GetLastError();
    record(ok?"UPDATE_SUCCESS\r\n":"UPDATE_FAILED\r\n");number(error);
    record("REBOOT_REQUIRED\r\n");number(reboot);
    if(!ok)ExitProcess(6);
    FreeLibrary(module);
    Sleep(30000);
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(7);
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(8);
    SetLastError(ERROR_SUCCESS);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)ExitProcess(9);
    CloseHandle(token);record("NORMAL_RESTART_REQUEST\r\n");
    if(!ExitWindowsEx(EWX_REBOOT,0)){record("FAIL_RESTART\r\n");ExitProcess(10);}
    CloseHandle(Log);ExitProcess(0);
}
