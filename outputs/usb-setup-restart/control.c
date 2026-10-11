/* SPDX-License-Identifier: MIT
 * Setup-observed phase-two storage/restart control. Never installs, loads or calls an XID driver.
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include "setup_gate201.h"
#include "restart_gate201.h"
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static HANDLE Log;
static WAIT_INSTALL WaitInstall;
static void line(const char *s,DWORD value) {
    char b[180];DWORD n,w;wsprintfA(b,"%s %08lx tick=%lu\r\n",s,value,GetTickCount());n=lstrlenA(b);
    if(!WriteFile(Log,b,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);
}
static void fail(const char *s) {line(s,GetLastError());CloseHandle(Log);ExitProcess(91);}
static uint32_t query(void *c,uint32_t ms) {(void)c;return WaitInstall(ms);}
static uint32_t clock_now(void *c) {(void)c;return GetTickCount();}
static void pause_poll(void *c,uint32_t ms) {(void)c;Sleep(ms);}
static void record(void *c,const char *s,uint32_t v) {(void)c;line(s,v);}
static int restart(void *c) {(void)c;return ExitWindowsEx(EWX_REBOOT,0)!=0;}
static void known_setup(void) {
    STARTUPINFOA si={0};PROCESS_INFORMATION pi={0};DWORD result;
    char command[]="C:\\xwnsetup\\wizard.exe /cancel-emulator";si.cb=sizeof(si);
    line("KNOWN_WIZARD_HELPER_BEGIN",0);
    if(!CreateProcessA("C:\\xwnsetup\\wizard.exe",command,NULL,NULL,FALSE,CREATE_NO_WINDOW,NULL,"C:\\xwnsetup",&si,&pi))fail("FAIL_HELPER_CREATE");
    CloseHandle(pi.hThread);line("HELPER_PID",pi.dwProcessId);
    result=WaitForSingleObject(pi.hProcess,150000);line("HELPER_JOIN",result);
    if(result!=WAIT_OBJECT_0){CloseHandle(pi.hProcess);CloseHandle(Log);ExitProcess(3);}
    if(!GetExitCodeProcess(pi.hProcess,&result))fail("FAIL_HELPER_EXIT_QUERY");
    CloseHandle(pi.hProcess);line("HELPER_EXIT",result);
    if(result){CloseHandle(Log);ExitProcess(4);}
}
static void observe_setup(void) {
    STARTUPINFOA si={0};PROCESS_INFORMATION pi={0};DWORD result;
    char command[]="C:\\xwnsetup\\observer.exe";si.cb=sizeof(si);
    line("OBSERVER_BEGIN",0);
    if(!CreateProcessA("C:\\xwnsetup\\observer.exe",command,NULL,NULL,FALSE,CREATE_NO_WINDOW,NULL,"C:\\xwnsetup",&si,&pi))fail("FAIL_OBSERVER_CREATE");
    CloseHandle(pi.hThread);line("OBSERVER_PID",pi.dwProcessId);
    result=WaitForSingleObject(pi.hProcess,150000);line("OBSERVER_JOIN",result);
    if(result!=WAIT_OBJECT_0){CloseHandle(pi.hProcess);CloseHandle(Log);ExitProcess(7);}
    if(!GetExitCodeProcess(pi.hProcess,&result))fail("FAIL_OBSERVER_EXIT_QUERY");
    CloseHandle(pi.hProcess);line("OBSERVER_EXIT",result);
    if(result){CloseHandle(Log);ExitProcess(8);}
}
static BYTE pattern(DWORD offset,DWORD phase) {return (BYTE)(33+(offset*17+phase*11)%90);}
void WINAPI mainCRTStartup(void) {
    DWORD phase,at,j,n,size,result;char path[MAX_PATH],block[30];const char *arg=GetCommandLineA();
    HANDLE payload,token;TOKEN_PRIVILEGES tp;HMODULE module;
    while(*arg&&*arg!=' ')arg++;
    while(*arg==' ')arg++;
    if(!lstrcmpA(arg,"/first"))phase=1;else if(!lstrcmpA(arg,"/second"))phase=2;else ExitProcess(89);
    wsprintfA(path,"C:\\xwnctl\\status%lu.log",phase);
    Log=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(89);
    line("STORAGE_CONTROL_PHASE",phase);Sleep(15000);
    wsprintfA(path,"C:\\xwnctl\\payload%lu.txt",phase);
    payload=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(payload==INVALID_HANDLE_VALUE)fail("FAIL_PAYLOAD_CREATE");
    line("PAYLOAD_BEGIN",2226);
    for(at=0;at<2226;at+=size) {
        size=2226-at;if(size>sizeof(block))size=sizeof(block);
        for(j=0;j<size;j++)block[j]=(char)pattern(at+j,phase);
        if(!WriteFile(payload,block,size,&n,NULL)||n!=size||!FlushFileBuffers(payload))fail("FAIL_PAYLOAD_WRITE");
        Sleep(40);
    }
    if(!CloseHandle(payload))fail("FAIL_PAYLOAD_CLOSE");
    payload=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);
    if(payload==INVALID_HANDLE_VALUE)fail("FAIL_PAYLOAD_REOPEN");
    for(at=0;at<2226;at+=size) {
        size=2226-at;if(size>sizeof(block))size=sizeof(block);
        if(!ReadFile(payload,block,size,&n,NULL)||n!=size)fail("FAIL_PAYLOAD_READ");
        for(j=0;j<size;j++)if((BYTE)block[j]!=pattern(at+j,phase)){SetLastError(ERROR_INVALID_DATA);fail("FAIL_PAYLOAD_COMPARE");}
    }
    CloseHandle(payload);line("PAYLOAD_GUEST_READBACK_PASS",2226);
    module=LoadLibraryA("setupapi.dll");WaitInstall=module?(WAIT_INSTALL)GetProcAddress(module,"CMP_WaitNoPendingInstallEvents"):NULL;
    if(!WaitInstall)fail("FAIL_PENDING_API");
    observe_setup();known_setup();
    result=xwn_wait_setup_idle(NULL,query,clock_now,pause_poll,record,30000,5000,250);
    if(result){line("RESTART_HELD_SETUP_GUARD",result);CloseHandle(Log);ExitProcess(5);}
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))fail("FAIL_TOKEN");
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))fail("FAIL_PRIVILEGE_NAME");
    SetLastError(0);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError())fail("FAIL_PRIVILEGE");
    CloseHandle(token);result=xwn_guarded_restart(NULL,query,restart,record);
    CloseHandle(Log);ExitProcess(result?6:0);
}
