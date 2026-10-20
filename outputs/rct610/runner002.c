/* MIT. Two fresh subject processes; bounded waits; normal Windows restart. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE logh;
static void zero(void *p,DWORD n) {BYTE *b=p;while(n--)*b++=0;}
static void row(const char *s,DWORD v) {char b[200];DWORD n,w;wsprintfA(b,"%s=%lu\r\n",s,v);n=lstrlenA(b);if(!WriteFile(logh,b,n,&w,0)||n!=w||!FlushFileBuffers(logh))ExitProcess(98);}
static BOOL run(const char *path,char *cmd,const char *label,DWORD timeout) {
    STARTUPINFOA si;PROCESS_INFORMATION pi;DWORD wait,code=99;BOOL ok;
    zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
    if(!CreateProcessA(path,cmd,0,0,FALSE,0,0,"C:\\xwn610-kit",&si,&pi)) {row("create_error",GetLastError());return FALSE;}
    wait=WaitForSingleObject(pi.hProcess,timeout);row(label,wait);
    if(wait!=WAIT_OBJECT_0) {row("owned_terminate",TerminateProcess(pi.hProcess,96));WaitForSingleObject(pi.hProcess,5000);}
    ok=GetExitCodeProcess(pi.hProcess,&code);row("exit_code",code);
    CloseHandle(pi.hThread);CloseHandle(pi.hProcess);return wait==WAIT_OBJECT_0&&ok&&code==0;
}
void WINAPI mainCRTStartup(void) {
    HANDLE token;TOKEN_PRIVILEGES tp;BOOL a,b;char control[]="subject610 control",trace[]="trace610";
    if(!CreateDirectoryA("C:\\xwn610",0))ExitProcess(90);
    logh=CreateFileA("C:\\xwn610\\runner.txt",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
    if(logh==INVALID_HANDLE_VALUE)ExitProcess(91);
    row("start",GetTickCount());
    a=run("C:\\xwn610-kit\\subject.exe",control,"control_wait",15000);
    b=run("C:\\xwn610-kit\\trace.exe",trace,"trace_wait",75000);
    row("control_ok",a);row("trace_ok",b);row("finish",GetTickCount());
    zero(&tp,sizeof(tp));tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(92);
    if(!LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(93);
    SetLastError(0);if(!AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)||GetLastError())ExitProcess(94);CloseHandle(token);
    row("restart_request",1);CloseHandle(logh);
    if(!ExitWindowsEx(EWX_REBOOT,0))ExitProcess(95);
    ExitProcess(a&&b?0:1);
}
