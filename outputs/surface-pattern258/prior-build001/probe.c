/* CPU-only baseline for the dedicated emulator diagnostic arena.
 * No renderer success claim. Checkpoint export provides a future pinned host hook. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <winioctl.h>
#include "arena.h"
#define IOCTL258 CTL_CODE(FILE_DEVICE_UNKNOWN,0x858,METHOD_BUFFERED,FILE_WRITE_ACCESS)
static X258Reply Reply;
static HANDLE Log;
static volatile LONG Checkpoint;
__declspec(dllexport) __attribute__((noinline)) void __cdecl X258Checkpoint(DWORD stage)
{ InterlockedExchange(&Checkpoint,(LONG)stage); }
static void record(const char *tag,DWORD a,DWORD b,DWORD c)
{
 char text[160];DWORD n,w;n=wsprintfA(text,"%s %lu %lu %lu\r\n",tag,a,b,c);
 if(!WriteFile(Log,text,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);
}
static void fail(const char *tag){record(tag,GetLastError(),0,0);ExitProcess(91);}
static void call(HANDLE h,DWORD op,DWORD gen,DWORD seed,DWORD expected)
{
 X258Request q={op,gen,seed,0};DWORD n;
 if(!DeviceIoControl(h,IOCTL258,&q,sizeof(q),&Reply,sizeof(Reply),&n,NULL)||n!=sizeof(Reply)||
    Reply.version!=258||Reply.status!=expected)fail("IOCTL_FAILED");
}
static void verify(DWORD seed)
{
 for(DWORD i=0;i<X258_BYTES;i++) {
  /* Independently spelled reference; do not call the driver's generator. */
  BYTE expected=(BYTE)((37*i+19*(i/16)+7*(i/256))^(83*seed));
  if(Reply.data[i]!=expected){record("BYTE_MISMATCH",i,expected,Reply.data[i]);ExitProcess(92);}
 }
 record("EXACT_CPU_BYTES",seed,X258_BYTES,0);
}
void __stdcall mainCRTStartup(void)
{
 SC_HANDLE scm,svc;HANDLE h;DWORD generation;
 Log=CreateFileA("C:\\xwnpat258\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,
                 FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(93);
 scm=OpenSCManagerA(NULL,NULL,SC_MANAGER_CREATE_SERVICE);if(!scm)fail("SCM_FAILED");
 svc=CreateServiceA(scm,"XwnPattern258","XwnPattern258",SERVICE_START|SERVICE_QUERY_STATUS,
     SERVICE_KERNEL_DRIVER,SERVICE_DEMAND_START,SERVICE_ERROR_NORMAL,"C:\\xwnpat258\\pattern.sys",NULL,NULL,NULL,NULL,NULL);
 if(!svc)fail("FRESH_SERVICE_REQUIRED");
 if(!StartServiceA(svc,0,NULL))fail("START_FAILED");
 CloseServiceHandle(svc);CloseServiceHandle(scm);
 h=CreateFileA("\\\\.\\XwnPattern258",GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
 if(h==INVALID_HANDLE_VALUE)fail("OPEN_FAILED");
 call(h,X258_ALLOCATE,0,0,X258_OK);generation=Reply.generation;
 if(generation!=1 || Reply.bytes!=X258_BYTES || (Reply.physical&4095)||Reply.physical<0x100000||Reply.physical>0x03bfc000)fail("RANGE_FAILED");
 record("ALLOCATED_CPU_ONLY",generation,Reply.physical,Reply.bytes);X258Checkpoint(1);
 call(h,X258_READ,generation,0,X258_OK);verify(0);X258Checkpoint(2);
 call(h,X258_WRITE,generation,1,X258_OK);X258Checkpoint(3);
 call(h,X258_READ,generation,0,X258_OK);verify(1);
 call(h,X258_WRITE,generation,2,X258_OK);call(h,X258_READ,generation,0,X258_OK);verify(2);
 record("CPU_COUNTS",Reply.reads,Reply.writes,0);X258Checkpoint(4);
 call(h,X258_CLOSE,0,0,X258_OK);call(h,X258_READ,generation,0,X258_QUARANTINED);
 if(!Reply.closed)fail("QUARANTINE_FAILED");CloseHandle(h);
 record("COMPLETE_CPU_ONLY",3*X258_BYTES,1,0);CloseHandle(Log);ExitProcess(0);
}
