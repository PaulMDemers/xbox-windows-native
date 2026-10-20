/* SPDX-License-Identifier: MIT
 * Interactive recording launcher. No display switch, input, timer or reboot.
 * Temporary setup values use the already-qualified retail game directory.
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
static const char root[]="SOFTWARE\\Fish Technology Group";
static const char sub[]="RollerCoaster Tycoon Setup";
static const char game[]="C:\\xwn586-kit\\game";
typedef struct { DWORD exists,type,size; BYTE data[512]; } VALUE;
static HANDLE logh=INVALID_HANDLE_VALUE;
static void zero(void*p,DWORD n){BYTE*b=p;while(n--)*b++=0;}
static BOOL bytes(HANDLE h,const void*p,DWORD n){DWORD done=0;return WriteFile(h,p,n,&done,0)&&done==n&&FlushFileBuffers(h);}
static void number(const char*k,DWORD v){char s[128];wsprintfA(s,"%s=%lu\r\n",k,v);bytes(logh,s,lstrlenA(s));}
static BOOL readvalue(HKEY k,const char*n,VALUE*v){LONG r;zero(v,sizeof(*v));v->size=sizeof(v->data);r=RegQueryValueExA(k,n,0,&v->type,v->data,&v->size);if(r==ERROR_FILE_NOT_FOUND){v->size=0;return TRUE;}v->exists=r==ERROR_SUCCESS;return r==ERROR_SUCCESS;}
static BOOL restore(HKEY k,const char*n,VALUE*v){LONG r;if(v->exists)return RegSetValueExA(k,n,0,v->type,v->data,v->size)==ERROR_SUCCESS;r=RegDeleteValueA(k,n);return r==ERROR_SUCCESS||r==ERROR_FILE_NOT_FOUND;}
void WINAPI mainCRTStartup(void){
 HKEY parent=0,key=0;DWORD pd=0,kd=0,language=0,code=99,wait;VALUE oldpath,oldlang,oldsetup;HANDLE backup;BOOL changed=FALSE,restored=TRUE,launched=FALSE;STARTUPINFOA si;PROCESS_INFORMATION pi;char cmd[]="\"C:\\xwn586-kit\\game\\RCT.EXE\"";
 if(!CreateDirectoryA("C:\\xwn624",0)){MessageBoxA(0,"This recording session has already been started. Do not rerun it. Check the session records first.","RCT recording",MB_OK|MB_ICONINFORMATION);ExitProcess(90);}
 logh=CreateFileA("C:\\xwn624\\runner.txt",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(logh==INVALID_HANDLE_VALUE)ExitProcess(91);
 number("schema",624);number("start_tick",GetTickCount());
 if(RegCreateKeyExA(HKEY_LOCAL_MACHINE,root,0,0,0,KEY_READ|KEY_WRITE,0,&parent,&pd)!=ERROR_SUCCESS)goto end;
 if(RegCreateKeyExA(parent,sub,0,0,0,KEY_READ|KEY_WRITE,0,&key,&kd)!=ERROR_SUCCESS)goto cleanup;
 number("parent_disposition",pd);number("key_disposition",kd);
 if(!readvalue(key,"Path",&oldpath)||!readvalue(key,"Language",&oldlang)||!readvalue(key,"SetupPath",&oldsetup)){number("backup_read_failed",1);goto cleanup;}
 backup=CreateFileA("C:\\xwn624\\registry.bin",GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(backup==INVALID_HANDLE_VALUE)goto cleanup;
 restored=bytes(backup,&oldpath,sizeof(oldpath))&&bytes(backup,&oldlang,sizeof(oldlang))&&bytes(backup,&oldsetup,sizeof(oldsetup));CloseHandle(backup);if(!restored){restored=TRUE;number("backup_write_failed",1);goto cleanup;}
 changed=TRUE;
 if(RegSetValueExA(key,"SetupPath",0,REG_SZ,(const BYTE*)game,sizeof(game))!=ERROR_SUCCESS||RegSetValueExA(key,"Path",0,REG_SZ,(const BYTE*)game,sizeof(game))!=ERROR_SUCCESS||RegSetValueExA(key,"Language",0,REG_DWORD,(const BYTE*)&language,sizeof(language))!=ERROR_SUCCESS){number("registry_set_failed",1);goto cleanup;}
 if(!SetCurrentDirectoryA(game)){number("cwd_error",GetLastError());goto cleanup;}
 zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
 if(!CreateProcessA("C:\\xwn586-kit\\game\\RCT.EXE",cmd,0,0,FALSE,0,0,game,&si,&pi)){number("create_error",GetLastError());goto cleanup;}
 launched=TRUE;CloseHandle(pi.hThread);number("game_pid",pi.dwProcessId);
 wait=WaitForSingleObject(pi.hProcess,INFINITE);number("wait",wait);
 if(wait!=WAIT_OBJECT_0){number("wait_error",GetLastError());CloseHandle(pi.hProcess);number("cleanup_deferred_game_state_unknown",1);CloseHandle(logh);ExitProcess(92);}
 if(GetExitCodeProcess(pi.hProcess,&code)){number("game_exit",code);}
 CloseHandle(pi.hProcess);
cleanup:
 if(key){if(changed){restored=restore(key,"Path",&oldpath);restored=restore(key,"Language",&oldlang)&&restored;restored=restore(key,"SetupPath",&oldsetup)&&restored;}RegFlushKey(key);RegCloseKey(key);}
 if(parent){if(kd==REG_CREATED_NEW_KEY)restored=(RegDeleteKeyA(parent,sub)==ERROR_SUCCESS)&&restored;RegFlushKey(parent);RegCloseKey(parent);}
 if(pd==REG_CREATED_NEW_KEY)restored=(RegDeleteKeyA(HKEY_LOCAL_MACHINE,root)==ERROR_SUCCESS)&&restored;
 RegFlushKey(HKEY_LOCAL_MACHINE);
end:
 number("launched",launched);number("registry_restored",restored);number("end_tick",GetTickCount());CloseHandle(logh);
 MessageBoxA(0,restored?(launched?"Game closed and temporary settings restored. Windows will stay running. You may now use Start > Shut Down > Restart.":"The game did not launch. Windows will stay running; check C:\\xwn624\\runner.txt."):"Settings restoration needs review. Leave Windows running and report this message.","RCT recording",MB_OK|(restored?MB_ICONINFORMATION:MB_ICONERROR));
 ExitProcess(restored?code:93);
}
