/* Ordinary serial append/flush diagnostic in an owned emulator fixture only. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static HANDLE Log;
static BYTE Seed[270225],Append[4097],Readback[274322];
static const DWORD Offsets[]={401,3985,65425,270225};
static const DWORD Lengths[]={110,111,112,219,221,4097};
static DWORD checksum(const BYTE *b,DWORD n){DWORD h=2166136261u,i;for(i=0;i<n;i++)h=(h^b[i])*16777619u;return h;}
static void report(const char *name,DWORD a,DWORD b,DWORD c,DWORD d,DWORD e,DWORD f){char s[220];DWORD n,len;wsprintfA(s,"%s %lu %lu %lu %lu %lu %lu\r\n",name,a,b,c,d,e,f);len=lstrlenA(s);if(!WriteFile(Log,s,len,&n,NULL)||n!=len||!FlushFileBuffers(Log))Sleep(INFINITE);}
static int fail(DWORD id,DWORD stage){DWORD e=GetLastError();report("FAIL",id,stage,e,0,0,0);return 0;}
static int failclosed(HANDLE h,DWORD id,DWORD stage){DWORD e=GetLastError();CloseHandle(h);SetLastError(e);return fail(id,stage);}
static BYTE prefix(DWORD i,DWORD id){return (BYTE)(33+(i*13+id*3)%90);}
static BYTE appended(DWORD i,DWORD id,DWORD size){return i==size-2?13:i==size-1?10:(BYTE)(32+(i*7+id)%95);}
static int testcase(DWORD id,DWORD mode,DWORD offset,DWORD size){
 char path[80];HANDLE h;DWORD i,n,before,after,total=offset+size,flags=mode==2?FILE_FLAG_WRITE_THROUGH:FILE_ATTRIBUTE_NORMAL;
 wsprintfA(path,"C:\\xwnap01\\t%03lu.bin",id);
 for(i=0;i<offset;i++)Seed[i]=prefix(i,id);
 for(i=0;i<size;i++)Append[i]=appended(i,id,size);
 before=checksum(Seed,offset);
 h=CreateFileA(path,GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,flags,NULL);
 if(h==INVALID_HANDLE_VALUE)return fail(id,1);
 if(!WriteFile(h,Seed,offset,&n,NULL)){return failclosed(h,id,2);}
 after=checksum(Seed,offset);report("SEED",id,offset,n,before,after,mode);
 if(n!=offset||after!=before){return failclosed(h,id,3);}
 if(!FlushFileBuffers(h)){return failclosed(h,id,4);}
 if(mode){
  if(!CloseHandle(h))return fail(id,5);
  h=CreateFileA(path,mode==3?FILE_APPEND_DATA:GENERIC_WRITE,FILE_SHARE_READ,NULL,OPEN_EXISTING,flags,NULL);
  if(h==INVALID_HANDLE_VALUE)return fail(id,6);
 }
 if(mode!=3 && SetFilePointer(h,0,NULL,FILE_END)!=offset){return failclosed(h,id,7);}
 before=checksum(Append,size);
 if(!WriteFile(h,Append,size,&n,NULL)){return failclosed(h,id,8);}
 after=checksum(Append,size);report("APPEND",id,size,n,before,after,mode);
 if(n!=size||before!=after){return failclosed(h,id,9);}
 for(i=0;i<offset;i++)if(Seed[i]!=prefix(i,id)){return failclosed(h,id,10);}
 for(i=0;i<size;i++)if(Append[i]!=appended(i,id,size)){return failclosed(h,id,11);}
 if(mode==3){
  if(!CloseHandle(h))return fail(id,17);
  h=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
  if(h==INVALID_HANDLE_VALUE)return fail(id,18);
 }
 if(!FlushFileBuffers(h)){return failclosed(h,id,12);}
 if(!CloseHandle(h))return fail(id,13);
 h=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(h==INVALID_HANDLE_VALUE)return fail(id,14);
 if(GetFileSize(h,NULL)!=total || !ReadFile(h,Readback,total,&n,NULL)||n!=total){return failclosed(h,id,15);}
 if(!CloseHandle(h))return fail(id,16);
 for(i=0;i<total;i++)if(Readback[i]!=(i<offset?prefix(i,id):appended(i-offset,id,size))){report("MISMATCH",id,i,Readback[i],i<offset?prefix(i,id):appended(i-offset,id,size),0,0);return 0;}
 report("CASE",id,mode,offset,size,total,checksum(Readback,total));return 1;
}
void WINAPI mainCRTStartup(void){
 DWORD id=0,mode,o,l,started,status;HANDLE token;TOKEN_PRIVILEGES tp;HMODULE setup;WAIT_INSTALL wait;int ok=1;
 if(!CreateDirectoryA("C:\\xwnap01",NULL))ExitProcess(80);
 Log=CreateFileA("C:\\xwnap01\\probe.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(81);
 report("ATTEMPT_ONCE",96,4,6,4,0,0);started=GetTickCount();
 for(mode=0;mode<4 && ok;mode++)for(o=0;o<4 && ok;o++)for(l=0;l<6 && ok;l++){ok=testcase(id,mode,Offsets[o],Lengths[l]);if(ok)id++;}
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
