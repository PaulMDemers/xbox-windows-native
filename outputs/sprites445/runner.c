/* SPDX-License-Identifier: MIT
 * Owned NT5 fixture only. Six isolated processes, exact exit receipts, normal restart.
 * Not a public installer or an executable to run on the development host.
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
static HANDLE log_file;
static DEVMODEA original_mode,requested_mode;
static int mode_changed;
static const char *const args[]={"default index8 r04di","hel index8 r04si","default rgb565 r04d6","hel rgb565 r04s6","default rgb32 r04d3","hel rgb32 r04s3"};
static const char *const names[]={"r04di","r04si","r04d6","r04s6","r04d3","r04s3"};
static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static BOOL write_all(HANDLE h,const char *s){DWORD n=(DWORD)lstrlenA(s),w=0;return WriteFile(h,s,n,&w,0)&&w==n&&FlushFileBuffers(h);}
static void number(const char *s,DWORD n){char b[160];wsprintfA(b,"%s=%lu\r\n",s,n);if(!write_all(log_file,b))ExitProcess(97);}
void WINAPI mainCRTStartup(void){DWORD i,code=0,completed=0;HANDLE token;TOKEN_PRIVILEGES tp;BOOL priv=FALSE;
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    if(!CreateDirectoryA("C:\\xwn445",0))ExitProcess(91);
    log_file=CreateFileA("C:\\xwn445\\runner.txt",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
    if(log_file==INVALID_HANDLE_VALUE)ExitProcess(92);
    number("schema",445);number("pid",GetCurrentProcessId());number("start_tick",GetTickCount());
    if(!CopyFileA("A:\\SPRITES.EXE","C:\\xwn445\\sprites.exe",TRUE)){number("copy_error",GetLastError());goto done;}
    if(!SetCurrentDirectoryA("C:\\xwn445")){number("cwd_error",GetLastError());goto done;}
    zero(&original_mode,sizeof(original_mode));original_mode.dmSize=sizeof(original_mode);
    if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&original_mode)){number("mode_query_failed",1);goto done;}
    number("mode_original_bits",original_mode.dmBitsPerPel);number("mode_original_width",original_mode.dmPelsWidth);number("mode_original_height",original_mode.dmPelsHeight);
    requested_mode=original_mode;requested_mode.dmBitsPerPel=32;requested_mode.dmFields=DM_BITSPERPEL|DM_PELSWIDTH|DM_PELSHEIGHT;
    {LONG status=ChangeDisplaySettingsA(&requested_mode,CDS_TEST);number("mode_test_status",(DWORD)status);if(status!=DISP_CHANGE_SUCCESSFUL)goto done;
     status=ChangeDisplaySettingsA(&requested_mode,0);number("mode_apply_status",(DWORD)status);if(status!=DISP_CHANGE_SUCCESSFUL)goto done;mode_changed=1;}
    zero(&requested_mode,sizeof(requested_mode));requested_mode.dmSize=sizeof(requested_mode);
    if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&requested_mode)){number("mode_after_query_failed",1);goto done;}
    number("mode_active_bits",requested_mode.dmBitsPerPel);number("mode_active_width",requested_mode.dmPelsWidth);number("mode_active_height",requested_mode.dmPelsHeight);
    if(requested_mode.dmBitsPerPel!=32||requested_mode.dmPelsWidth!=original_mode.dmPelsWidth||requested_mode.dmPelsHeight!=original_mode.dmPelsHeight){number("mode_active_mismatch",1);goto done;}
    for(i=0;i<6;i++){
        STARTUPINFOA si;PROCESS_INFORMATION pi;char command[256],key[64],path[128],text[40];HANDLE receipt;DWORD wait;
        zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
        wsprintfA(command,"C:\\xwn445\\sprites.exe %s",args[i]);
        wsprintfA(key,"case%lu_start_tick",i);number(key,GetTickCount());
        if(!CreateProcessA("C:\\xwn445\\sprites.exe",command,0,0,FALSE,0,0,"C:\\xwn445",&si,&pi)){
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
        wsprintfA(path,"C:\\xwn445\\%s.exit",names[i]);receipt=CreateFileA(path,GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
        if(receipt==INVALID_HANDLE_VALUE){number("receipt_error",GetLastError());break;}
        wsprintfA(text,"%lu\r\n",code);if(!write_all(receipt,text)){CloseHandle(receipt);number("receipt_write_error",1);break;}
        CloseHandle(receipt);completed++;
    }
done:
    if(mode_changed){LONG status=ChangeDisplaySettingsA(&original_mode,0);number("mode_restore_status",(DWORD)status);
      zero(&requested_mode,sizeof(requested_mode));requested_mode.dmSize=sizeof(requested_mode);
      number("mode_restored",status==DISP_CHANGE_SUCCESSFUL&&EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&requested_mode)&&requested_mode.dmBitsPerPel==original_mode.dmBitsPerPel&&requested_mode.dmPelsWidth==original_mode.dmPelsWidth&&requested_mode.dmPelsHeight==original_mode.dmPelsHeight);}
    number("completed_cases",completed);number("end_tick",GetTickCount());
    if(OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){
        zero(&tp,sizeof(tp));tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
        if(LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){
            SetLastError(0);priv=AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)&&GetLastError()==0;
        }
        CloseHandle(token);
    }
    number("restart_privilege",priv);number("restart_request",priv&&ExitWindowsEx(EWX_REBOOT,0));
    CloseHandle(log_file);ExitProcess(completed==6?0:1);
}
