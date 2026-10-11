/* SPDX-License-Identifier: MIT
 * One installation, two HID open/read/close cycles, then a guarded normal reboot.
 * Only the disposable emulator's exact 045e:0202 hardware ID is installed.
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <setupapi.h>
#include <hidsdi.h>
#include "setup_gate201.h"
#include "restart_gate201.h"
typedef BOOL (WINAPI *UPDATE)(HWND,LPCSTR,LPCSTR,DWORD,PBOOL);
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static HANDLE Log;
static OVERLAPPED Read;
static BYTE Report[13];
static char Detail[1024];
static void line(const char *s,DWORD value)
{
    char b[180];DWORD n,w;wsprintfA(b,"%s %08lx tick=%lu\r\n",s,value,GetTickCount());n=lstrlenA(b);
    if(!WriteFile(Log,b,n,&w,NULL)||w!=n||!FlushFileBuffers(Log)) ExitProcess(90);
}
static void fatal(const char *s) { line(s,GetLastError());CloseHandle(Log);ExitProcess(91); }
static HANDLE open_hid(void)
{
    GUID guid;HDEVINFO set;SP_DEVICE_INTERFACE_DATA face;DWORD i,need;HANDLE h=INVALID_HANDLE_VALUE;
    HidD_GetHidGuid(&guid);set=SetupDiGetClassDevsA(&guid,NULL,NULL,DIGCF_PRESENT|DIGCF_DEVICEINTERFACE);
    if(set==INVALID_HANDLE_VALUE) fatal("FAIL_HID_ENUM");
    face.cbSize=sizeof(face);
    for(i=0;i<32 && SetupDiEnumDeviceInterfaces(set,NULL,&guid,i,&face);i++) {
        PSP_DEVICE_INTERFACE_DETAIL_DATA_A detail=(PSP_DEVICE_INTERFACE_DETAIL_DATA_A)Detail;
        HIDD_ATTRIBUTES attrs;
        detail->cbSize=sizeof(*detail);
        if(!SetupDiGetDeviceInterfaceDetailA(set,&face,detail,sizeof(Detail),&need,NULL)) continue;
        h=CreateFileA(detail->DevicePath,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,FILE_FLAG_OVERLAPPED,NULL);
        if(h==INVALID_HANDLE_VALUE) continue;
        attrs.Size=sizeof(attrs);
        if(HidD_GetAttributes(h,&attrs) && attrs.VendorID==0x045e && attrs.ProductID==0x0202) break;
        CloseHandle(h);h=INVALID_HANDLE_VALUE;
    }
    SetupDiDestroyDeviceInfoList(set);return h;
}
static WAIT_INSTALL WaitInstall;
static uint32_t setup_query(void *c,uint32_t ms) {(void)c;return WaitInstall(ms);}
static uint32_t setup_clock(void *c) {(void)c;return GetTickCount();}
static void setup_sleep(void *c,uint32_t ms) {(void)c;Sleep(ms);}
static void setup_record(void *c,const char *s,uint32_t v) {(void)c;line(s,v);}
static int setup_restart(void *c) {(void)c;return ExitWindowsEx(EWX_REBOOT,0)!=0;}
void WINAPI mainCRTStartup(void)
{
    HMODULE module;BOOL ok;
    DWORD error,cycle,i,n,result,start;HANDLE h,token;TOKEN_PRIVILEGES tp;
    PHIDP_PREPARSED_DATA pp;HIDP_CAPS caps;
    Log=CreateFileA("C:\\xwnxid\\verify.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE) ExitProcess(89);
    line("VERIFY_EXISTING_DRIVER",1);Sleep(15000);
    Read.hEvent=CreateEventA(NULL,TRUE,FALSE,NULL);if(!Read.hEvent) fatal("FAIL_EVENT");
    start=GetTickCount();
    for(cycle=0;cycle<2;cycle++) {
        h=INVALID_HANDLE_VALUE;
        for(i=0;i<20 && h==INVALID_HANDLE_VALUE;i++) {h=open_hid();if(h==INVALID_HANDLE_VALUE) Sleep(500);}
        if(h==INVALID_HANDLE_VALUE) fatal("FAIL_FIND_XID_HID");
        line("OPEN_CYCLE",cycle);
        if(!HidD_GetPreparsedData(h,&pp)) fatal("FAIL_PREPARSED");
        result=HidP_GetCaps(pp,&caps);line("CAPS_STATUS",result);
        line("USAGE_PAGE",caps.UsagePage);line("USAGE",caps.Usage);line("INPUT_BYTES",caps.InputReportByteLength);
        line("OUTPUT_BYTES",caps.OutputReportByteLength);line("INPUT_BUTTON_CAPS",caps.NumberInputButtonCaps);
        line("INPUT_VALUE_CAPS",caps.NumberInputValueCaps);
        if(result!=HIDP_STATUS_SUCCESS || caps.UsagePage!=1 || caps.Usage!=5 || caps.InputReportByteLength!=13 || caps.OutputReportByteLength!=0) {
            SetLastError(ERROR_INVALID_DATA);fatal("FAIL_CAPS");
        }
        for(i=0;i<100;i++) {
            ResetEvent(Read.hEvent);n=0;SetLastError(0);
            ok=ReadFile(h,Report,sizeof(Report),&n,&Read);error=GetLastError();
            if(!ok && error!=ERROR_IO_PENDING) fatal("FAIL_READ_SUBMIT");
            if(!ok && WaitForSingleObject(Read.hEvent,3000)!=WAIT_OBJECT_0) {
                line("READ_TIMEOUT",i);CancelIo(h);
                if(WaitForSingleObject(Read.hEvent,3000)!=WAIT_OBJECT_0) fatal("FAIL_UNDRAINED_READ");
            }
            if(!GetOverlappedResult(h,&Read,&n,FALSE)) fatal("FAIL_READ_COMPLETE");
            if(n!=13 || Report[0]!=1 || (Report[2]&0xc0)) {SetLastError(ERROR_INVALID_DATA);fatal("FAIL_REPORT_SHAPE");}
            if(i==0 || i==99) {
                unsigned j;char b[96];DWORD at=0,w;
                for(j=0;j<13;j++) {b[at++]="0123456789abcdef"[Report[j]>>4];b[at++]="0123456789abcdef"[Report[j]&15];}
                b[at++]='\r';b[at++]='\n';if(!WriteFile(Log,b,at,&w,NULL)||w!=at) fatal("FAIL_LOG_BYTES");
                for(j=0;j<6;j++) {
                    static const USAGE axes[]={0x30,0x31,0x33,0x34,0x32,0x35};ULONG value;
                    result=HidP_GetUsageValue(HidP_Input,1,0,axes[j],&value,pp,(PCHAR)Report,13);
                    if(result!=HIDP_STATUS_SUCCESS) {SetLastError(result);fatal("FAIL_AXIS_PARSE");}
                    line("AXIS",axes[j]);line("VALUE",value);
                }
            }
            if(GetTickCount()-start>60000) {SetLastError(ERROR_TIMEOUT);fatal("FAIL_REPORT_BUDGET");}
        }
        if(!HidD_FreePreparsedData(pp) || !CloseHandle(h)) fatal("FAIL_CLOSE");
        line("CYCLE_PASS_REPORTS",100);Sleep(500);
    }
    CloseHandle(Read.hEvent);line("HID_READ_PASS",200);
    module=LoadLibraryA("setupapi.dll");
    WaitInstall=module?(WAIT_INSTALL)GetProcAddress(module,"CMP_WaitNoPendingInstallEvents"):NULL;
    if(!WaitInstall) fatal("FAIL_PENDING_API");
    result=xwn_wait_setup_idle(NULL,setup_query,setup_clock,setup_sleep,setup_record,30000,5000,250);
    if(result) {line("RESTART_HELD_SETUP_GUARD",result);CloseHandle(Log);ExitProcess(4);}
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)) fatal("FAIL_TOKEN");
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)) fatal("FAIL_PRIVILEGE_NAME");
    SetLastError(0);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()) fatal("FAIL_PRIVILEGE");
    CloseHandle(token);result=xwn_guarded_restart(NULL,setup_query,setup_restart,setup_record);
    CloseHandle(Log);ExitProcess(result?5:0);
}
