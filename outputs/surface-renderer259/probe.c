/* SPDX-License-Identifier: GPL-2.0-or-later
 * Emulator-only renderer protocol. Requires three real, independently verified
 * host injections; an ordinary/uncontrolled launch must fail its first read.
 * The immutable258 driver owns one allocation until reboot. No guest GPU access.
 */
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <winioctl.h>
#include "../surface-pattern258/arena.h"
#include "expected.h"
#define IOCTL258 CTL_CODE(FILE_DEVICE_UNKNOWN,0x858,METHOD_BUFFERED,FILE_WRITE_ACCESS)
static X258Reply Reply;
static HANDLE Log;
static volatile LONG Checkpoint;
__declspec(dllexport) __attribute__((noinline)) void __cdecl
X259Checkpoint(DWORD stage,const X258Reply *reply,HANDLE owner)
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
        if(Reply.data[i]!=x259_expected(i,mode)){
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
    Log=CreateFileA("C:\\xwnpat259\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,
        CREATE_NEW,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(93);
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
    record("ALLOCATED_RENDERER_PROTOCOL",generation,Reply.physical,Reply.bytes);
    /* Host: attest actual process/driver/owner/four pages, then AGE pattern0.
     * No host data writes into Reply or the arena are allowed to satisfy checks. */
    X259Checkpoint(1,&Reply,h);
    call(h,X258_READ,generation,0,X258_OK);verify(0);
    /* Host: create a fresh dirty test surface carrying GPU pattern1. */
    X259Checkpoint(2,&Reply,h);
    call(h,X258_READ,generation,0,X258_OK);verify(1);
    /* Host: update that same resident texture to GPU pattern2, mark it dirty.
     * This actual CPU store must block for download/eviction, then win. */
    X259Checkpoint(3,&Reply,h);
    call(h,X258_WRITE,generation,1,X258_OK);
    call(h,X258_READ,generation,0,X258_OK);verify(3);
    /* Host: prove callback unlink/free and no remaining arena references before
     * resuming. A second CPU read checks for a late stale download. */
    X259Checkpoint(4,&Reply,h);
    call(h,X258_READ,generation,0,X258_OK);verify(3);
    if(Reply.reads!=4||Reply.writes!=1)fail("COUNTS_FAILED");
    record("CPU_COUNTS",Reply.reads,Reply.writes,0);
    X259Checkpoint(5,&Reply,h);
    call(h,X258_CLOSE,0,0,X258_OK);call(h,X258_READ,generation,0,X258_QUARANTINED);
    if(!Reply.closed)fail("QUARANTINE_FAILED");
    CloseHandle(h);record("COMPLETE_RENDERER_PROTOCOL",4*X258_BYTES,1,0);
    CloseHandle(Log);ExitProcess(0);
}
