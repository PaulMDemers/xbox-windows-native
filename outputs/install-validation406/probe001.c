/* SPDX-License-Identifier: MIT
 * Native OEM/registry/long-name evidence, followed by real Windows Media Player.
 * No driver, service, dump setting or device-policy changes.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE logFile;
static BYTE data[8192];
static void zero(void *p,DWORD n){volatile BYTE *b=p;while(n--)*b++=0;}
static void number(const char *key,DWORD v){char b[192];DWORD n,w;n=wsprintfA(b,"%s=%lu\r\n",key,v);if(!WriteFile(logFile,b,n,&w,0)||w!=n||!FlushFileBuffers(logFile))ExitProcess(90);}
static BOOL copyShortcut(const WCHAR *to,const char *key){BOOL ok=CopyFileW(L"C:\\XWN406\\floppy.lnk",to,TRUE);number(key,ok?0:GetLastError());return ok;}
void WINAPI mainCRTStartup(void){HKEY key;DWORD typ=0,bytes=sizeof(data),ret;HANDLE h,token;TOKEN_PRIVILEGES tp;STARTUPINFOA si;PROCESS_INFORMATION pi;BOOL priv=FALSE;
    char command[]="\"C:\\Program Files\\Windows Media Player\\mplayer2.exe\" /play /close C:\\XWN406\\ces2001.mpg";
    logFile=CreateFileA("C:\\XWN406\\result.log",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(logFile==INVALID_HANDLE_VALUE)ExitProcess(90);
    number("BEGIN",406);number("OEMCP",GetOEMCP());
    if(GetOEMCP()==437){
        copyShortcut(L"C:\\Documents and Settings\\Default User\\SendTo\\3\x00bd Floppy (A).lnk","DEFAULT_SHORTCUT_COPY_ERROR");
        copyShortcut(L"C:\\Documents and Settings\\Win2K\\SendTo\\3\x00bd Floppy (A).lnk","USER_SHORTCUT_COPY_ERROR");
    }
    h=CreateFileW(L"C:\\XWN406\\abcdefghijklmnopqrstuvwxyz01234567890123456",GENERIC_WRITE,0,0,CREATE_NEW,0,0);
    number("NAME43_CREATE_ERROR",h==INVALID_HANDLE_VALUE?GetLastError():0);if(h!=INVALID_HANDLE_VALUE)CloseHandle(h);
    ret=RegOpenKeyExA(HKEY_LOCAL_MACHINE,"SOFTWARE\\Microsoft\\DRM",0,KEY_QUERY_VALUE,&key);number("DRM_OPEN",ret);
    if(!ret){ret=RegQueryValueExA(key,"DataPath",0,&typ,data,&bytes);number("DRM_QUERY",ret);number("DRM_TYPE",typ);number("DRM_BYTES",bytes);RegCloseKey(key);
        if(!ret){DWORD n;h=CreateFileA("C:\\XWN406\\drm-value.bin",GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(h!=INVALID_HANDLE_VALUE){number("DRM_SAVE",WriteFile(h,data,bytes,&n,0)&&n==bytes&&FlushFileBuffers(h));CloseHandle(h);}}
    }
    zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
    Sleep(10000);ret=CreateProcessA(0,command,0,0,FALSE,0,0,0,&si,&pi);number("WMP_LAUNCH",ret);number("WMP_LAUNCH_ERROR",ret?0:GetLastError());
    if(ret){CloseHandle(pi.hThread);number("WMP_WAIT",WaitForSingleObject(pi.hProcess,270000));if(GetExitCodeProcess(pi.hProcess,&ret))number("WMP_EXIT",ret);CloseHandle(pi.hProcess);}
    number("COMPLETE",406);Sleep(15000);
    if(OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){
        tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
        if(LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){SetLastError(ERROR_SUCCESS);priv=AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)&&GetLastError()==ERROR_SUCCESS;}CloseHandle(token);
    }
    number("NORMAL_RESTART_REQUEST",priv&&ExitWindowsEx(EWX_REBOOT,0));CloseHandle(logFile);ExitProcess(0);
}
