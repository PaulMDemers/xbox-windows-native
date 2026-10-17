/* SPDX-License-Identifier: MIT
 * Owned NT5 fixture only. Two isolated processes, exact exit receipts, normal restart.
 * Not a public installer or an executable to run on the development host.
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
static HANDLE log_file;
static DEVMODEA original_mode,requested_mode,observed_mode;
static int mode_changed,mode_restored;
static const char *const args[]={"default keyd","hel keys"};
static const char *const names[]={"keyd","keys"};
static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static BOOL write_all(HANDLE h,const char *s){DWORD n=(DWORD)lstrlenA(s),w=0;return WriteFile(h,s,n,&w,0)&&w==n&&FlushFileBuffers(h);}
static void number(const char *s,DWORD n){char b[160];wsprintfA(b,"%s=%lu\r\n",s,n);if(!write_all(log_file,b))ExitProcess(97);}
static void mode_fields(const char *prefix,const DEVMODEA *d){char key[80];
    wsprintfA(key,"%s_bits",prefix);number(key,d->dmBitsPerPel);
    wsprintfA(key,"%s_width",prefix);number(key,d->dmPelsWidth);
    wsprintfA(key,"%s_height",prefix);number(key,d->dmPelsHeight);
    wsprintfA(key,"%s_hz",prefix);number(key,d->dmDisplayFrequency);
    wsprintfA(key,"%s_flags",prefix);number(key,d->dmDisplayFlags);
}
static int enter_mode(void){unsigned n,found=0,index=0;LONG status;
    zero(&original_mode,sizeof(original_mode));original_mode.dmSize=sizeof(original_mode);
    if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&original_mode)){number("mode_query_failed",1);return 0;}
    mode_fields("mode_original",&original_mode);
    if(original_mode.dmPelsWidth!=640||original_mode.dmPelsHeight!=480||original_mode.dmBitsPerPel!=16||original_mode.dmDisplayFrequency!=60||original_mode.dmDisplayFlags!=0){number("mode_original_mismatch",1);return 0;}
    for(n=0;n<4096;n++){
        zero(&observed_mode,sizeof(observed_mode));observed_mode.dmSize=sizeof(observed_mode);
        if(!EnumDisplaySettingsA(0,n,&observed_mode))break;
        if(!found&&observed_mode.dmPelsWidth==640&&observed_mode.dmPelsHeight==480&&observed_mode.dmBitsPerPel==24&&observed_mode.dmDisplayFrequency==60&&observed_mode.dmDisplayFlags==0){requested_mode=observed_mode;found=1;index=n;}
    }
    number("mode_inventory_count",n);number("mode_inventory_complete",n<4096);number("mode_selected",found);
    if(n==4096||!found)return 0;
    number("mode_selected_index",index);mode_fields("mode_requested",&requested_mode);
    requested_mode.dmFields=DM_BITSPERPEL|DM_PELSWIDTH|DM_PELSHEIGHT|DM_DISPLAYFREQUENCY|DM_DISPLAYFLAGS;
    status=ChangeDisplaySettingsA(&requested_mode,CDS_TEST);number("mode_test_status",(DWORD)status);if(status!=DISP_CHANGE_SUCCESSFUL)return 0;
    status=ChangeDisplaySettingsA(&requested_mode,0);number("mode_apply_status",(DWORD)status);if(status!=DISP_CHANGE_SUCCESSFUL)return 0;mode_changed=1;
    zero(&observed_mode,sizeof(observed_mode));observed_mode.dmSize=sizeof(observed_mode);
    if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&observed_mode)){number("mode_active_query_failed",1);return 0;}
    mode_fields("mode_active",&observed_mode);
    if(observed_mode.dmPelsWidth!=640||observed_mode.dmPelsHeight!=480||observed_mode.dmBitsPerPel!=24||observed_mode.dmDisplayFrequency!=60||observed_mode.dmDisplayFlags!=0){number("mode_active_mismatch",1);return 0;}
    return 1;
}
static void leave_mode(void){LONG status;
    number("mode_changed",mode_changed);if(!mode_changed)return;
    original_mode.dmFields=DM_BITSPERPEL|DM_PELSWIDTH|DM_PELSHEIGHT|DM_DISPLAYFREQUENCY|DM_DISPLAYFLAGS;
    status=ChangeDisplaySettingsA(&original_mode,0);number("mode_restore_status",(DWORD)status);
    zero(&observed_mode,sizeof(observed_mode));observed_mode.dmSize=sizeof(observed_mode);
    if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&observed_mode)){number("mode_restore_query_failed",1);return;}
    mode_fields("mode_after_restore",&observed_mode);
    mode_restored=status==DISP_CHANGE_SUCCESSFUL&&observed_mode.dmBitsPerPel==original_mode.dmBitsPerPel&&observed_mode.dmPelsWidth==original_mode.dmPelsWidth&&observed_mode.dmPelsHeight==original_mode.dmPelsHeight&&observed_mode.dmDisplayFrequency==original_mode.dmDisplayFrequency&&observed_mode.dmDisplayFlags==original_mode.dmDisplayFlags;
    number("mode_restored",mode_restored);
}
void WINAPI mainCRTStartup(void){DWORD i,code=0,completed=0;HANDLE token;TOKEN_PRIVILEGES tp;BOOL priv=FALSE;
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    if(!CreateDirectoryA("C:\\xwn447",0))ExitProcess(91);
    log_file=CreateFileA("C:\\xwn447\\runner.txt",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
    if(log_file==INVALID_HANDLE_VALUE)ExitProcess(92);
    number("schema",447);number("pid",GetCurrentProcessId());number("start_tick",GetTickCount());
    if(!CopyFileA("A:\\KEYPROBE.EXE","C:\\xwn447\\keyprobe.exe",TRUE)){number("copy_error",GetLastError());goto done;}
    if(!SetCurrentDirectoryA("C:\\xwn447")){number("cwd_error",GetLastError());goto done;}
    if(!enter_mode())goto done;
    for(i=0;i<2;i++){
        STARTUPINFOA si;PROCESS_INFORMATION pi;char command[256],key[64],path[128],text[40];HANDLE receipt;DWORD wait;
        zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
        wsprintfA(command,"C:\\xwn447\\keyprobe.exe %s",args[i]);
        wsprintfA(key,"case%lu_start_tick",i);number(key,GetTickCount());
        if(!CreateProcessA("C:\\xwn447\\keyprobe.exe",command,0,0,FALSE,0,0,"C:\\xwn447",&si,&pi)){
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
        wsprintfA(path,"C:\\xwn447\\%s.exit",names[i]);receipt=CreateFileA(path,GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
        if(receipt==INVALID_HANDLE_VALUE){number("receipt_error",GetLastError());break;}
        wsprintfA(text,"%lu\r\n",code);if(!write_all(receipt,text)){CloseHandle(receipt);number("receipt_write_error",1);break;}
        CloseHandle(receipt);completed++;
    }
done:
    leave_mode();
    number("completed_cases",completed);number("end_tick",GetTickCount());
    if(OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){
        zero(&tp,sizeof(tp));tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
        if(LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){
            SetLastError(0);priv=AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)&&GetLastError()==0;
        }
        CloseHandle(token);
    }
    number("restart_privilege",priv);number("restart_request",priv&&ExitWindowsEx(EWX_REBOOT,0));
    CloseHandle(log_file);ExitProcess(completed==2&&mode_restored?0:1);
}
