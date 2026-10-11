/* SPDX-License-Identifier: GPL-2.0-or-later
 * Emulator-only observation protocol. Verifies CPU-owned arena contents before
 * and after one bounded host ownership capture. No renderer pixel injection.
 * The immutable258 driver owns one allocation until reboot. No guest GPU access.
 */
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <winioctl.h>
#include "../surface-pattern258/arena.h"

#define IOCTL258 CTL_CODE(FILE_DEVICE_UNKNOWN,0x858,METHOD_BUFFERED,FILE_WRITE_ACCESS)
static X258Reply Reply;
static HANDLE Log;
static volatile LONG Checkpoint;
__declspec(dllexport) __attribute__((noinline)) void __cdecl
X265Checkpoint(DWORD stage,const X258Reply *reply,HANDLE owner)
{
    /* Arguments are runtime attestation inputs, not an ownership grant. */
    (void)reply;(void)owner;InterlockedExchange(&Checkpoint,(LONG)stage);
}
static void record(const char *tag,DWORD a,DWORD b,DWORD c)
{
    char text[160];DWORD n,w;n=wsprintfA(text,"%s %lu %lu %lu\r\n",tag,a,b,c);
    if(!WriteFile(Log,text,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);
}
static void fail(const char *tag){record(tag,GetLastError(),0,0);ExitProcess(91);}
static void call(HANDLE h,DWORD op,DWORD gen,DWORD seed,DWORD expected)
{
    X258Request q={op,gen,seed,0};DWORD n;
    if(!DeviceIoControl(h,IOCTL258,&q,sizeof(q),&Reply,sizeof(Reply),&n,NULL)||
       n!=sizeof(Reply)||Reply.version!=258||Reply.status!=expected)fail("IOCTL_FAILED");
}
static void verify(DWORD mode)
{
    DWORD bad=0,first=X258_BYTES;
    for(DWORD i=0;i<X258_BYTES;i++){
        if(Reply.data[i]!=(unsigned char)((i*37u+(i/16u)*19u+(i/256u)*7u)^(mode*83u))){
            if(!bad)first=i;
            bad++;
        }
    }
    if(bad){record("BYTE_MISMATCH",mode,first,bad);ExitProcess(92);}
    record("EXACT_ARENA_BYTES",mode,X258_BYTES,0);
}
void __stdcall mainCRTStartup(void)
{
    SC_HANDLE scm,svc;HANDLE h;DWORD generation;
    Log=CreateFileA("C:\\xwnled265\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,
        CREATE_NEW,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(93);
    /* The read-only debugger cannot fault a nonresident image-header page in.
     * Keep this ONE diagnostic identity page resident until process termination.
     * No arena/GPU memory is touched and renderer expectations are unchanged. */
    {
        HMODULE image=GetModuleHandleA(NULL);
        if(!image || !VirtualLock((LPVOID)image,4096))fail("HEADER_LOCK_FAILED");
        record("RESIDENT_IDENTITY_HEADER",(DWORD)(ULONG_PTR)image,4096,0);
    }
    scm=OpenSCManagerA(NULL,NULL,SC_MANAGER_CREATE_SERVICE);if(!scm)fail("SCM_FAILED");
    svc=CreateServiceA(scm,"XwnPattern258","XwnPattern258",SERVICE_START|SERVICE_QUERY_STATUS,
        SERVICE_KERNEL_DRIVER,SERVICE_DEMAND_START,SERVICE_ERROR_NORMAL,
        "C:\\xwnpat258\\pattern.sys",NULL,NULL,NULL,NULL,NULL);
    if(!svc)fail("FRESH_SERVICE_REQUIRED");
    if(!StartServiceA(svc,0,NULL))fail("START_FAILED");
    CloseServiceHandle(svc);CloseServiceHandle(scm);
    h=CreateFileA("\\\\.\\XwnPattern258",GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,
        NULL,OPEN_EXISTING,0,NULL);if(h==INVALID_HANDLE_VALUE)fail("OPEN_FAILED");
    call(h,X258_ALLOCATE,0,0,X258_OK);generation=Reply.generation;
    if(generation!=1||Reply.bytes!=X258_BYTES||(Reply.physical&4095)||
       Reply.physical<0x100000||Reply.physical>0x03bfc000)fail("RANGE_FAILED");
    record("ALLOCATED_OBSERVATION_PROTOCOL",generation,Reply.physical,Reply.bytes);
    call(h,X258_READ,generation,0,X258_OK);verify(0);
    /* Host may observe ownership metadata only. Arena contents remain CPU seed0. */
    X265Checkpoint(1,&Reply,h);
    call(h,X258_READ,generation,0,X258_OK);verify(0);
    if(Reply.reads!=2||Reply.writes!=0)fail("COUNTS_FAILED");
    record("CPU_COUNTS",Reply.reads,Reply.writes,0);
    X265Checkpoint(2,&Reply,h);
    call(h,X258_CLOSE,0,0,X258_OK);call(h,X258_READ,generation,0,X258_QUARANTINED);
    if(!Reply.closed)fail("QUARANTINE_FAILED");
    CloseHandle(h);record("COMPLETE_OBSERVATION_PROTOCOL",2*X258_BYTES,0,0);
    CloseHandle(Log);ExitProcess(0);
}
