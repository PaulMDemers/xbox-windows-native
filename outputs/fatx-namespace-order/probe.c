/* Owned-emulator concurrency diagnostic: ordinary file I/O and volume flush only. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static HANDLE Log,Start;
static volatile LONG Completed[3],Errors[3];
static BYTE Buffers[2][4097];
static void line(const char *s){DWORD n,len=lstrlenA(s);if(!WriteFile(Log,s,len,&n,NULL)||n!=len||!FlushFileBuffers(Log))Sleep(INFINITE);}
static void report(const char *name,DWORD a,DWORD b,DWORD c){char s[160];wsprintfA(s,"%s %lu %lu %lu\r\n",name,a,b,c);line(s);}
static DWORD WINAPI worker(LPVOID arg){
 DWORD id=(DWORD)arg,i,n,j;HANDLE h;char path[80];
 WaitForSingleObject(Start,INFINITE);
 if(id==2){
  /* Flush an existing volume handle. No raw reads, writes, lock or dismount. */
  h=CreateFileA("\\\\.\\C:",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
  if(h==INVALID_HANDLE_VALUE){Errors[id]=(LONG)GetLastError();return 1;}
  for(i=0;i<500;i++){
   if(!FlushFileBuffers(h)){Errors[id]=(LONG)GetLastError();break;}
   InterlockedIncrement(&Completed[id]);Sleep(1);
  }
  if(!CloseHandle(h)&&!Errors[id])Errors[id]=(LONG)GetLastError();
 }else{
  wsprintfA(path,"C:\\xwncc01\\worker%lu.bin",id);
  for(i=0;i<500;i++){
   for(j=0;j<sizeof(Buffers[id]);j++)Buffers[id][j]=(BYTE)(j*13+id*17+i*29);
   h=CreateFileA(path,GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
   if(h==INVALID_HANDLE_VALUE){Errors[id]=(LONG)GetLastError();break;}
   if(!WriteFile(h,Buffers[id],sizeof(Buffers[id]),&n,NULL)||n!=sizeof(Buffers[id]))Errors[id]=(LONG)(GetLastError()?GetLastError():ERROR_WRITE_FAULT);
   if(!Errors[id]&&!FlushFileBuffers(h))Errors[id]=(LONG)GetLastError();
   if(!CloseHandle(h)&&!Errors[id])Errors[id]=(LONG)GetLastError();
   if(Errors[id])break;
   InterlockedIncrement(&Completed[id]);Sleep(1);
  }
 }
 return Errors[id]?1:0;
}
void WINAPI mainCRTStartup(void){
 HANDLE threads[3],token;DWORD i,status,started;TOKEN_PRIVILEGES tp;HMODULE setup;WAIT_INSTALL wait;
 if(!CreateDirectoryA("C:\\xwncc01",NULL))ExitProcess(80);
 Log=CreateFileA("C:\\xwncc01\\probe.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(81);
 setup=LoadLibraryA("setupapi.dll");wait=setup?(WAIT_INSTALL)GetProcAddress(setup,"CMP_WaitNoPendingInstallEvents"):NULL;
 if(!wait){report("FAIL_PENDING_API",GetLastError(),0,0);ExitProcess(82);}
 report("ATTEMPT_ONCE",3,500,4097);
 Start=CreateEventA(NULL,TRUE,FALSE,NULL);if(!Start){report("FAIL_EVENT",GetLastError(),0,0);ExitProcess(83);}
 for(i=0;i<3;i++){
  threads[i]=CreateThread(NULL,0,worker,(LPVOID)i,0,NULL);
  if(!threads[i]){report("FAIL_THREAD",i,GetLastError(),0);Sleep(INFINITE);}
 }
 started=GetTickCount();SetEvent(Start);
 status=WaitForMultipleObjects(3,threads,TRUE,180000);
 report("WAIT_RESULT",status,GetTickCount()-started,0);
 report("COUNTS",Completed[0],Completed[1],Completed[2]);report("ERRORS",Errors[0],Errors[1],Errors[2]);
 if(status!=WAIT_OBJECT_0){report("HELD_FOR_DIAGNOSIS",status,0,0);Sleep(INFINITE);}
 for(i=0;i<3;i++){CloseHandle(threads[i]);}
 CloseHandle(Start);
 if(Errors[0]||Errors[1]||Errors[2])report("WORKLOAD_FAILED",Errors[0],Errors[1],Errors[2]);
 else report("COMPLETE",Completed[0],Completed[1],Completed[2]);
 status=wait(0);if(status!=WAIT_OBJECT_0){report("RESTART_BLOCKED_PENDING_INSTALL",status,0,0);Sleep(INFINITE);}
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){report("FAIL_TOKEN",GetLastError(),0,0);ExitProcess(84);}
 tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
 if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){report("FAIL_LOOKUP",GetLastError(),0,0);ExitProcess(85);}
 SetLastError(0);if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()){report("FAIL_PRIVILEGE",GetLastError(),0,0);ExitProcess(86);}
 CloseHandle(token);report("NORMAL_RESTART_REQUEST",0,0,0);
 if(!ExitWindowsEx(EWX_REBOOT,0))report("FAIL_RESTART",GetLastError(),0,0);
 CloseHandle(Log);ExitProcess(0);
}
