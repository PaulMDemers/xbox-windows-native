/* SPDX-License-Identifier: MIT
 * Explicit installer for the one supported full hardware ID. No UI automation.
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
typedef BOOL (WINAPI *update_driver)(HWND,LPCSTR,LPCSTR,DWORD,PBOOL);
static HANDLE log_handle;
static void text(const char *s) { DWORD n; WriteFile(log_handle,s,lstrlenA(s),&n,NULL); FlushFileBuffers(log_handle); }
static void number(const char *name,DWORD v)
{
    char b[16];unsigned i=sizeof(b);b[--i]=0;b[--i]='\n';b[--i]='\r';
    do { b[--i]=(char)('0'+v%10);v/=10; } while(v);text(name);text(b+i);
}
void WINAPI mainCRTStartup(void)
{
    HMODULE module;update_driver update;BOOL ok,reboot=FALSE;DWORD error;
    log_handle=CreateFileA("C:\\xwnpcican1\\install.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(log_handle==INVALID_HANDLE_VALUE) ExitProcess(20);
    text("XWN_PCI207_INSTALL_BEGIN version=1\r\n");
    module=LoadLibraryA("newdev.dll");
    update=module?(update_driver)GetProcAddress(module,"UpdateDriverForPlugAndPlayDevicesA"):NULL;
    if(!update){number("lookup_error=",GetLastError());ExitProcess(21);}
    text("id=PCI\\VEN_10DE&DEV_01B4&SUBSYS_00000000&REV_B1\r\n");
    ok=update(NULL,"PCI\\VEN_10DE&DEV_01B4&SUBSYS_00000000&REV_B1","C:\\xwnpcican1\\xwnrsc.inf",0,&reboot);
    error=ok?0:GetLastError();number("success=",ok);number("error=",error);number("reboot_required=",reboot);
    text("XWN_PCI207_INSTALL_END\r\n");CloseHandle(log_handle);ExitProcess(ok?0:22);
}
