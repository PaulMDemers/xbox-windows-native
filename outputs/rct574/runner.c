/* SPDX-License-Identifier: MIT
 * Bounded RCT launch on the owned Windows fixture, then registry restoration
 * and normal restart. Native input/capture control; no game patch.
 */
#define _WIN32_WINNT 0x0500
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>
static HANDLE logh;
static DWORD gamepid;
static const char root[]="SOFTWARE\\Fish Technology Group";
static const char sub[]="RollerCoaster Tycoon Setup";
static const char game[]="C:\\xwn574-kit\\game";
typedef struct { DWORD exists,type,size; BYTE data[512]; } VALUE;
static void zero(void*p,DWORD n){BYTE*b=p;while(n--)*b++=0;}
static BOOL bytes(HANDLE h,const void*p,DWORD n){DWORD done=0;return WriteFile(h,p,n,&done,0)&&done==n&&FlushFileBuffers(h);}
static void number(const char*k,DWORD v){char s[160];wsprintfA(s,"%s=%lu\r\n",k,v);bytes(logh,s,lstrlenA(s));}
static BOOL readvalue(HKEY k,const char*n,VALUE*v){LONG r;zero(v,sizeof(*v));v->size=sizeof(v->data);r=RegQueryValueExA(k,n,0,&v->type,v->data,&v->size);if(r==ERROR_FILE_NOT_FOUND){v->size=0;return TRUE;}v->exists=r==ERROR_SUCCESS;return r==ERROR_SUCCESS;}
static BOOL restore(HKEY k,const char*n,VALUE*v){LONG r;if(v->exists)return RegSetValueExA(k,n,0,v->type,v->data,v->size)==ERROR_SUCCESS;r=RegDeleteValueA(k,n);return r==ERROR_SUCCESS||r==ERROR_FILE_NOT_FOUND;}
static void modules(void){HANDLE h;MODULEENTRY32 m;BOOL more;char s[512];h=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,gamepid);if(h==INVALID_HANDLE_VALUE){number("modules_error",GetLastError());return;}zero(&m,sizeof(m));m.dwSize=sizeof(m);more=Module32First(h,&m);while(more){wsprintfA(s,"module=%s size=%lu\r\n",m.szModule,m.modBaseSize);bytes(logh,s,lstrlenA(s));more=Module32Next(h,&m);}number("modules_end",GetLastError());CloseHandle(h);}
static BOOL CALLBACK windows(HWND w,LPARAM closeit){DWORD pid;char s[640],t[200],c[100];RECT r;POINT pt={0,0},cursor={0,0};GetWindowThreadProcessId(w,&pid);if(pid!=gamepid)return TRUE;GetWindowTextA(w,t,sizeof(t));GetClassNameA(w,c,sizeof(c));zero(&r,sizeof(r));GetClientRect(w,&r);ClientToScreen(w,&pt);GetCursorPos(&cursor);wsprintfA(s,"window visible=%lu focus=%lu client=%ld,%ld,%ld,%ld cursor=%ld,%ld screen=%d,%d class=%s title=%s\r\n",(DWORD)IsWindowVisible(w),(DWORD)(GetForegroundWindow()==w),pt.x,pt.y,r.right,r.bottom,cursor.x,cursor.y,GetSystemMetrics(SM_CXSCREEN),GetSystemMetrics(SM_CYSCREEN),c,t);bytes(logh,s,lstrlenA(s));if(closeit)PostMessageA(w,WM_CLOSE,0,0);return TRUE;}
#include "input.h"
void WINAPI mainCRTStartup(void){
 HKEY parent=0,key=0;DWORD pd=0,kd=0,language=0,code=99,wait=WAIT_FAILED;VALUE oldpath,oldlang,oldsetup;HANDLE backup,token;BOOL changed=FALSE,restored=TRUE,priv=FALSE;STARTUPINFOA si;PROCESS_INFORMATION pi;TOKEN_PRIVILEGES tp;char cmd[]="\"C:\\xwn574-kit\\game\\RCT.EXE\"";
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
 if(!CreateDirectoryA("C:\\xwn574",0))ExitProcess(90);
 logh=CreateFileA("C:\\xwn574\\runner.txt",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(logh==INVALID_HANDLE_VALUE)ExitProcess(91);
 number("schema",574);number("start_tick",GetTickCount());
 initialwidth=GetSystemMetrics(SM_CXSCREEN);initialheight=GetSystemMetrics(SM_CYSCREEN);number("initial_width",initialwidth);number("initial_height",initialheight);
 if(RegCreateKeyExA(HKEY_LOCAL_MACHINE,root,0,0,0,KEY_READ|KEY_WRITE,0,&parent,&pd)!=ERROR_SUCCESS)goto end;
 if(RegCreateKeyExA(parent,sub,0,0,0,KEY_READ|KEY_WRITE,0,&key,&kd)!=ERROR_SUCCESS)goto cleanup;
 number("parent_disposition",pd);number("key_disposition",kd);
 if(!readvalue(key,"Path",&oldpath)||!readvalue(key,"Language",&oldlang)||!readvalue(key,"SetupPath",&oldsetup)){number("backup_read_failed",1);goto cleanup;}
 backup=CreateFileA("C:\\xwn574\\registry.bin",GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
 if(backup==INVALID_HANDLE_VALUE)goto cleanup;
 restored=bytes(backup,&oldpath,sizeof(oldpath))&&bytes(backup,&oldlang,sizeof(oldlang))&&bytes(backup,&oldsetup,sizeof(oldsetup));CloseHandle(backup);if(!restored){restored=TRUE;number("backup_write_failed",1);goto cleanup;}
 changed=TRUE;
 if(RegSetValueExA(key,"SetupPath",0,REG_SZ,(const BYTE*)game,sizeof(game))!=ERROR_SUCCESS){number("setup_path_set_failed",1);goto cleanup;}
 if(RegSetValueExA(key,"Path",0,REG_SZ,(const BYTE*)game,sizeof(game))!=ERROR_SUCCESS||RegSetValueExA(key,"Language",0,REG_DWORD,(const BYTE*)&language,sizeof(language))!=ERROR_SUCCESS){number("registry_set_failed",1);goto cleanup;}
 if(!SetCurrentDirectoryA(game)){number("cwd_error",GetLastError());goto cleanup;}
 zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
 if(!CreateProcessA("C:\\xwn574-kit\\game\\RCT.EXE",cmd,0,0,FALSE,0,0,game,&si,&pi)){number("create_error",GetLastError());goto cleanup;}
 CloseHandle(pi.hThread);gamepid=pi.dwProcessId;number("game_pid",gamepid);
 number("input_sequence_submitted",runinputs());releaseinputs();
 modules();EnumWindows(windows,0);wait=WaitForSingleObject(pi.hProcess,0);
 number("wait",wait);
 if(wait!=WAIT_OBJECT_0){number("close_requested",1);EnumWindows(windows,1);wait=WaitForSingleObject(pi.hProcess,10000);if(wait!=WAIT_OBJECT_0){number("forced_terminate",TerminateProcess(pi.hProcess,98));WaitForSingleObject(pi.hProcess,5000);}}
 if(GetExitCodeProcess(pi.hProcess,&code)){number("game_exit",code);}
 CloseHandle(pi.hProcess);number("desktop_restored",GetSystemMetrics(SM_CXSCREEN)==initialwidth&&GetSystemMetrics(SM_CYSCREEN)==initialheight);
cleanup:
 if(key){if(changed){restored=restore(key,"Path",&oldpath);restored=restore(key,"Language",&oldlang)&&restored;restored=restore(key,"SetupPath",&oldsetup)&&restored;}RegCloseKey(key);}
 if(parent){if(kd==REG_CREATED_NEW_KEY)restored=(RegDeleteKeyA(parent,sub)==ERROR_SUCCESS)&&restored;RegCloseKey(parent);}
 if(pd==REG_CREATED_NEW_KEY)restored=(RegDeleteKeyA(HKEY_LOCAL_MACHINE,root)==ERROR_SUCCESS)&&restored;
end:
 number("registry_restored",restored);number("end_tick",GetTickCount());
 if(restored&&OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){
  zero(&tp,sizeof(tp));tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
  if(LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){SetLastError(0);priv=AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)&&GetLastError()==0;}CloseHandle(token);
 }
 number("restart_privilege",priv);number("restart_requested",priv&&ExitWindowsEx(EWX_REBOOT,0));CloseHandle(logh);ExitProcess(code);
}
