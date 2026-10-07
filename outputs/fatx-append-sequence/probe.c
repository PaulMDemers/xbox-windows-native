/* Bounded synchronous log-style append sequence; owned emulator only. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static HANDLE Log;
static BYTE Expected[1048576],Readback[1048576],Append[4097];
static const DWORD Offsets[]={401,3985,65425,270225};
static const DWORD Lengths[]={219,110,111,112,221,4097};
static DWORD update(DWORD h,const BYTE *b,DWORD n){DWORD i;for(i=0;i<n;i++)h=(h^b[i])*16777619u;return h;}
static DWORD checksum(const BYTE *b,DWORD n){return update(2166136261u,b,n);}
static void report(const char *name,DWORD a,DWORD b,DWORD c,DWORD d,DWORD e,DWORD f){char s[220];DWORD n,len;wsprintfA(s,"%s %lu %lu %lu %lu %lu %lu\r\n",name,a,b,c,d,e,f);len=lstrlenA(s);if(!WriteFile(Log,s,len,&n,NULL)||n!=len||!FlushFileBuffers(Log))Sleep(INFINITE);}
static int fail(DWORD id,DWORD stage){DWORD e=GetLastError();report("FAIL",id,stage,e,0,0,0);return 0;}
static int failclosed(HANDLE h,DWORD id,DWORD stage){DWORD e=GetLastError();CloseHandle(h);SetLastError(e);return fail(id,stage);}
static BYTE prefix(DWORD i,DWORD key){return (BYTE)(33+(i*13+key*3)%90);}
static BYTE appended(DWORD i,DWORD key,DWORD step,DWORD size){return i==size-2?13:i==size-1?10:(BYTE)(32+(i*7+key*11+step*17)%95);}
static int testcase(DWORD id,DWORD policy,DWORD reopen,DWORD offset){
 char path[80];HANDLE h;DWORD i,step,n,size,key=id%4,total=offset,before,after;
 DWORD sourceBefore=2166136261u,sourceAfter=2166136261u,flushes=0;
 wsprintfA(path,"C:\\xwnas01\\t%03lu.bin",id);
 for(i=0;i<offset;i++)Expected[i]=prefix(i,key);
 before=checksum(Expected,offset);
 h=CreateFileA(path,GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 if(h==INVALID_HANDLE_VALUE)return fail(id,1);
 if(!WriteFile(h,Expected,offset,&n,NULL))return failclosed(h,id,2);
 after=checksum(Expected,offset);report("SEED",id,offset,n,before,after,0);
 if(n!=offset||before!=after)return failclosed(h,id,3);
 if(!FlushFileBuffers(h))return failclosed(h,id,4);
 /* No diagnostic I/O in this loop: only the selected payload flush policy. */
 for(step=0;step<512;step++){
  if(reopen){
   if(!CloseHandle(h))return fail(id,5);
   h=CreateFileA(path,GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
   if(h==INVALID_HANDLE_VALUE)return fail(id,6);
  }
  if(SetFilePointer(h,0,NULL,FILE_END)!=total)return failclosed(h,id,7);
  size=Lengths[step%6];if(total+size>sizeof(Expected))return failclosed(h,id,8);
  for(i=0;i<size;i++){Append[i]=appended(i,key,step,size);Expected[total+i]=Append[i];}
  sourceBefore=update(sourceBefore,Append,size);
  if(!WriteFile(h,Append,size,&n,NULL)||n!=size)return failclosed(h,id,9);
  sourceAfter=update(sourceAfter,Append,size);
  for(i=0;i<size;i++)if(Append[i]!=appended(i,key,step,size))return failclosed(h,id,10);
  if(policy==0){if(!FlushFileBuffers(h))return failclosed(h,id,11);flushes++;}
  total+=size;
 }
 if(policy==1){if(!FlushFileBuffers(h))return failclosed(h,id,12);flushes++;}
 if(!CloseHandle(h))return fail(id,13);
 report("SOURCE",id,512,total-offset,sourceBefore,sourceAfter,flushes);
 h=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(h==INVALID_HANDLE_VALUE)return fail(id,14);
 if(GetFileSize(h,NULL)!=total||!ReadFile(h,Readback,total,&n,NULL)||n!=total)return failclosed(h,id,15);
 if(!CloseHandle(h))return fail(id,16);
 for(i=0;i<total;i++)if(Readback[i]!=Expected[i]){report("MISMATCH",id,i,Readback[i],Expected[i],0,0);return 0;}
 report("CASE",id,policy,reopen,offset,total,checksum(Readback,total));return 1;
}
void WINAPI mainCRTStartup(void){
 DWORD id=0,policy,reopen,o,started,status;HANDLE token;TOKEN_PRIVILEGES tp;HMODULE setup;WAIT_INSTALL wait;int ok=1;
 if(!CreateDirectoryA("C:\\xwnas01",NULL))ExitProcess(80);
 Log=CreateFileA("C:\\xwnas01\\probe.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(81);
 report("ATTEMPT_ONCE",16,512,4,2,2,0);started=GetTickCount();
 for(policy=0;policy<2&&ok;policy++)for(reopen=0;reopen<2&&ok;reopen++)for(o=0;o<4&&ok;o++){ok=testcase(id,policy,reopen,Offsets[o]);if(ok)id++;}
 report(ok?"COMPLETE":"WORKLOAD_FAILED",id,GetTickCount()-started,0,0,0,0);
 setup=LoadLibraryA("setupapi.dll");wait=setup?(WAIT_INSTALL)GetProcAddress(setup,"CMP_WaitNoPendingInstallEvents"):NULL;
 if(!wait){report("FAIL_PENDING_API",GetLastError(),0,0,0,0,0);Sleep(INFINITE);}
 status=wait(0);if(status!=WAIT_OBJECT_0){report("RESTART_BLOCKED_PENDING_INSTALL",status,0,0,0,0,0);Sleep(INFINITE);}
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){report("FAIL_TOKEN",GetLastError(),0,0,0,0,0);Sleep(INFINITE);}
 tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
 if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){report("FAIL_LOOKUP",GetLastError(),0,0,0,0,0);Sleep(INFINITE);}
 SetLastError(0);if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()){report("FAIL_PRIVILEGE",GetLastError(),0,0,0,0,0);Sleep(INFINITE);}
 CloseHandle(token);report("NORMAL_RESTART_REQUEST",0,0,0,0,0,0);
 if(!ExitWindowsEx(EWX_REBOOT,0))report("FAIL_RESTART",GetLastError(),0,0,0,0,0);
 CloseHandle(Log);ExitProcess(0);
}
