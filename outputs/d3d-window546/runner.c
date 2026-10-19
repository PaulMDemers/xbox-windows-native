/* SPDX-License-Identifier: MIT
 * Owned NT5 PC fixture only. Two isolated processes, exact exit receipts, normal restart.
 * Not a public installer or an executable to run on the development host.
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
static HANDLE log_file;
static DEVMODEA original;static int changed;
static const char *const args[]={"default r09cd","hel r09cs"};
static const char *const names[]={"r09cd","r09cs"};
static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static BOOL write_all(HANDLE h,const char *s){DWORD n=(DWORD)lstrlenA(s),w=0;return WriteFile(h,s,n,&w,0)&&w==n&&FlushFileBuffers(h);}
static void number(const char *s,DWORD n){char b[160];wsprintfA(b,"%s=%lu\r\n",s,n);if(!write_all(log_file,b))ExitProcess(97);}
void WINAPI mainCRTStartup(void){DWORD i,code=0,completed=0;HANDLE token;TOKEN_PRIVILEGES tp;BOOL priv=FALSE;
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    if(!CreateDirectoryA("C:\\xwn546",0))ExitProcess(91);
    log_file=CreateFileA("C:\\xwn546\\runner.txt",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
    if(log_file==INVALID_HANDLE_VALUE)ExitProcess(92);
    number("schema",546);number("pid",GetCurrentProcessId());number("start_tick",GetTickCount());
    if(!CopyFileA("A:\\D3D.EXE","C:\\xwn546\\d3d.exe",TRUE)){number("copy_error",GetLastError());goto done;}
    if(!SetCurrentDirectoryA("C:\\xwn546")){number("cwd_error",GetLastError());goto done;}
    zero(&original,sizeof(original));original.dmSize=sizeof(original);
    if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&original)){number("mode.query_error",GetLastError());goto done;}
    number("mode.before",original.dmBitsPerPel);
    {DEVMODEA requested=original;LONG result;requested.dmFields=DM_BITSPERPEL;requested.dmBitsPerPel=32;
     result=ChangeDisplaySettingsA(&requested,CDS_TEST);number("mode.test",(DWORD)result);if(result!=DISP_CHANGE_SUCCESSFUL)goto done;
     result=ChangeDisplaySettingsA(&requested,0);number("mode.set",(DWORD)result);if(result!=DISP_CHANGE_SUCCESSFUL)goto done;changed=1;
     zero(&requested,sizeof(requested));requested.dmSize=sizeof(requested);if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&requested))goto done;
     number("mode.after",requested.dmBitsPerPel);if(requested.dmBitsPerPel!=32)goto done;Sleep(1000);}
    for(i=0;i<2;i++){
        STARTUPINFOA si;PROCESS_INFORMATION pi;char command[256],key[64],path[128],text[40];HANDLE receipt;DWORD wait;
        zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
        wsprintfA(command,"C:\\xwn546\\d3d.exe %s",args[i]);
        wsprintfA(key,"case%lu_start_tick",i);number(key,GetTickCount());
        if(!CreateProcessA("C:\\xwn546\\d3d.exe",command,0,0,FALSE,0,0,"C:\\xwn546",&si,&pi)){
            wsprintfA(key,"case%lu_create_error",i);number(key,GetLastError());break;
        }
        CloseHandle(pi.hThread);wsprintfA(key,"case%lu_pid",i);number(key,pi.dwProcessId);
        wait=WaitForSingleObject(pi.hProcess,90000);wsprintfA(key,"case%lu_wait",i);number(key,wait);
        if(wait!=WAIT_OBJECT_0){
            BOOL killed=TerminateProcess(pi.hProcess,98);wsprintfA(key,"case%lu_terminate",i);number(key,killed);
            WaitForSingleObject(pi.hProcess,5000);CloseHandle(pi.hProcess);break;
        }
        if(!GetExitCodeProcess(pi.hProcess,&code)){number("exit_query_error",GetLastError());CloseHandle(pi.hProcess);break;}
        CloseHandle(pi.hProcess);wsprintfA(key,"case%lu_exit",i);number(key,code);
        wsprintfA(path,"C:\\xwn546\\%s.exit",names[i]);receipt=CreateFileA(path,GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
        if(receipt==INVALID_HANDLE_VALUE){number("receipt_error",GetLastError());break;}
        wsprintfA(text,"%lu\r\n",code);if(!write_all(receipt,text)){CloseHandle(receipt);number("receipt_write_error",1);break;}
        CloseHandle(receipt);completed++;
    }
done:
    if(changed){LONG restored=ChangeDisplaySettingsA(&original,0);number("mode.restore",(DWORD)restored);if(restored!=DISP_CHANGE_SUCCESSFUL)completed=0;}
    number("completed_cases",completed);number("end_tick",GetTickCount());
    if(OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){
        zero(&tp,sizeof(tp));tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
        if(LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){
            SetLastError(0);priv=AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)&&GetLastError()==0;
        }
        CloseHandle(token);
    }
    number("restart_privilege",priv);number("restart_request",priv&&ExitWindowsEx(EWX_REBOOT,0));
    CloseHandle(log_file);ExitProcess(completed==2?0:1);
}
