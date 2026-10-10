#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <winioctl.h>
#include "context.h"
#define IOCTL222 CTL_CODE(FILE_DEVICE_UNKNOWN,0x822,METHOD_BUFFERED,FILE_WRITE_ACCESS)
static HANDLE Log;
static CRITICAL_SECTION LogLock;
static volatile LONG Stop,Failed;
static void record(const char *tag,DWORD a,DWORD b,DWORD c)
{
    char text[160];DWORD length,written;
    length=wsprintfA(text,"%s %lu %lu %lu\r\n",tag,a,b,c);
    EnterCriticalSection(&LogLock);
    if(!WriteFile(Log,text,length,&written,NULL) || written!=length || !FlushFileBuffers(Log))InterlockedExchange(&Failed,1);
    LeaveCriticalSection(&LogLock);
}
static HANDLE open_device(void)
{return CreateFileA("\\\\.\\XwnResident222",GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);}
static int call(HANDLE h,DWORD op,DWORD generation,DWORD status,X222Reply *r)
{
    X222Request q={op,generation};DWORD bytes=0;
    return DeviceIoControl(h,IOCTL222,&q,sizeof(q),r,sizeof(*r),&bytes,NULL) && bytes==sizeof(*r) && r->status==status;
}
static DWORD WINAPI worker(LPVOID arg)
{
    DWORD id=(DWORD)(ULONG_PTR)arg,i=0;HANDLE h=open_device();X222Reply r;
    if(h==INVALID_HANDLE_VALUE)goto failed;
    for(i=0;i<16 && !Stop;i++) {
        DWORD began=GetTickCount(),generation;
        for(;;) {
            X222Request q={X222_ALLOCATE,0};DWORD bytes;
            if(!DeviceIoControl(h,IOCTL222,&q,sizeof(q),&r,sizeof(r),&bytes,NULL) || bytes!=sizeof(r))goto failed;
            if(r.status==X222_OK)break;
            if(r.status!=X222_BUSY || Stop || GetTickCount()-began>10000)goto failed;
            Sleep(1);
        }
        generation=r.generation;
        if(!generation || !r.owned || r.pages[0]<0x100000 || (r.pages[0]&4095) || r.pages[3]>0x03bff000 ||
           r.pages[1]!=r.pages[0]+4096 || r.pages[2]!=r.pages[0]+8192 || r.pages[3]!=r.pages[0]+12288)goto failed;
        record("LEASE",id,generation,r.pages[0]);
        if(!call(h,X222_QUERY,generation,X222_OK,&r) || !call(h,X222_EXPOSE,generation,X222_HOLD,&r) ||
           !call(h,X222_RELEASE,generation,X222_OK,&r))goto failed;
        record("RELEASE",id,generation,r.owned);
    }
    CloseHandle(h);record("WORKER",id,i,0);return i==16?0:1;
failed:
    InterlockedExchange(&Stop,1);InterlockedExchange(&Failed,1);
    if(h!=INVALID_HANDLE_VALUE)CloseHandle(h);
    record("WORKER_FAIL",id,i,GetLastError());return 1;
}
static int joined(DWORD result,DWORD count)
{ return count && result-WAIT_OBJECT_0<count; }
static void fail(const char *why)
{ record(why,GetLastError(),0,0);ExitProcess(91); }
void __stdcall mainCRTStartup(void)
{
    SC_HANDLE scm,svc;HANDLE owner,other,threads[4];X222Reply r;
    DWORD i,generation,exitcode,wait,bytes;X222Request q;
    HANDLE token;TOKEN_PRIVILEGES privileges;
    InitializeCriticalSection(&LogLock);
    Log=CreateFileA("C:\\xwnctx222\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
    record("BEGIN_CPU_OWNER_ONLY",222,16384,0);
    scm=OpenSCManagerA(NULL,NULL,SC_MANAGER_CREATE_SERVICE);if(!scm)fail("SCM_FAIL");
    svc=CreateServiceA(scm,"XwnResident222","Owned emulator resident context222",SERVICE_START,
        SERVICE_KERNEL_DRIVER,SERVICE_DEMAND_START,SERVICE_ERROR_NORMAL,"C:\\xwnctx222\\resident.sys",NULL,NULL,NULL,NULL,NULL);
    if(!svc || !StartServiceA(svc,0,NULL))fail("SERVICE_FAIL");
    CloseServiceHandle(svc);CloseServiceHandle(scm);
    owner=open_device();other=open_device();if(owner==INVALID_HANDLE_VALUE || other==INVALID_HANDLE_VALUE)fail("OPEN_FAIL");
    if(!call(owner,X222_ALLOCATE,0,X222_OK,&r) || r.generation!=1)fail("FIRST_FAIL");
    generation=r.generation;
    q=(X222Request){X222_INFO,0};
    if(DeviceIoControl(other,IOCTL222,&q,sizeof(q)-1,&r,sizeof(r),&bytes,NULL))fail("SHORT_ACCEPTED");
    if(!call(other,X222_QUERY,generation,X222_OWNER,&r) || r.generation || r.pages[0])fail("OWNER_FAIL");
    if(!call(owner,X222_QUERY,generation+1,X222_STALE,&r))fail("STALE_FAIL");
    if(!call(owner,X222_QUERY,generation,X222_OK,&r) || !call(owner,X222_EXPOSE,generation,X222_HOLD,&r))fail("QUERY_FAIL");
    CloseHandle(owner); /* Actual IRP_MJ_CLEANUP must release this pre-GPU lease. */
    if(!call(other,X222_INFO,0,X222_OK,&r) || r.owned || r.allocations!=1 || r.releases!=1 || r.cleanup_releases!=1)fail("CLEANUP_FAIL");
    record("OWNER_STALE_SHORT_CLEANUP",r.allocations,r.releases,r.cleanup_releases);
    for(i=0;i<4;i++){threads[i]=CreateThread(NULL,0,worker,(LPVOID)(ULONG_PTR)i,0,NULL);if(!threads[i])break;}
    if(i!=4) {InterlockedExchange(&Stop,1);InterlockedExchange(&Failed,1);}
    wait=i?WaitForMultipleObjects(i,threads,TRUE,120000):WAIT_FAILED;
    record("WAIT_JOIN",wait,i,0);
    if(!joined(wait,i)) {
        InterlockedExchange(&Stop,1);InterlockedExchange(&Failed,1);
        if(i) {
            wait=WaitForMultipleObjects(i,threads,TRUE,15000);
            record("WAIT_JOIN_RETRY",wait,i,0);
            if(!joined(wait,i))fail("JOIN_FAIL");
        }
    }
    for(DWORD j=0;j<i;j++){if(!GetExitCodeThread(threads[j],&exitcode) || exitcode)InterlockedExchange(&Failed,1);CloseHandle(threads[j]);}
    if(Failed || !call(other,X222_INFO,0,X222_OK,&r) || r.owned || r.allocations!=65 || r.releases!=65 ||
       r.exposure_refusals!=65 || r.cleanup_releases!=1 || r.verified_bytes!=65*3*16384)fail("FINAL_FAIL");
    record("COMPLETE_CPU_OWNER_ONLY",r.allocations,r.releases,r.exposure_refusals);
    record("VERIFIED_JOINED",r.verified_bytes,r.cleanup_releases,4);CloseHandle(other);
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))fail("TOKEN_FAIL");
    privileges.PrivilegeCount=1;privileges.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&privileges.Privileges[0].Luid) || !AdjustTokenPrivileges(token,FALSE,&privileges,0,NULL,NULL) || GetLastError()!=ERROR_SUCCESS)fail("PRIVILEGE_FAIL");
    CloseHandle(token);record("NORMAL_RESTART_REQUEST",222,0,0);
    if(!ExitWindowsEx(EWX_REBOOT,0))fail("RESTART_FAIL");
    ExitProcess(0);
}
