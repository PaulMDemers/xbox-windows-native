/* SPDX-License-Identifier: MIT
 * Native NT5 probe. No dialog actions, policy edits, driver install or restart.
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <winioctl.h>
#include <setupapi.h>
#include <cfgmgr32.h>
static const GUID TelemetryGuid = {0x4cecfd27,0x4cde,0x4cc9,{0xa2,0x92,0xd5,0xcf,0x42,0x3e,0x57,0x07}};
#define IOCTL_TELEMETRY CTL_CODE(FILE_DEVICE_UNKNOWN,0x807,METHOD_BUFFERED,FILE_READ_ACCESS)
typedef struct request { DWORD version,address,command; } request;
typedef struct response { DWORD version,result,polls,attempts,status,data; } response;
static HANDLE log_handle;
static void text(const char *s)
{
    DWORD n;
    WriteFile(log_handle,s,lstrlenA(s),&n,NULL); FlushFileBuffers(log_handle);
}
static void number(const char *name,DWORD v)
{
    char b[16]; unsigned i=sizeof(b);
    b[--i]=0; b[--i]='\n'; b[--i]='\r';
    do { b[--i]=(char)('0'+v%10); v/=10; } while(v);
    text(name); text(b+i);
}
void WINAPI mainCRTStartup(void)
{
    HDEVINFO set; SP_DEVICE_INTERFACE_DATA iface; SP_DEVINFO_DATA dev;
    BYTE buffer[2048]; PSP_DEVICE_INTERFACE_DETAIL_DATA_A detail=(void*)buffer;
    HANDLE file; DWORD needed,bytes,i,status=0,problem=0; response out;
    const request cases[]={{1,0x10,4},{1,0x4c,0},{1,0x4c,1},{1,0x54,0},{1,0x10,0x11},{1,0x10,4}};
    log_handle=CreateFileA("C:\\xwnpci207\\probe.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(log_handle==INVALID_HANDLE_VALUE) ExitProcess(20);
    text("XWN_PCI207_BEGIN version=1\r\n");
    set=SetupDiGetClassDevsA(&TelemetryGuid,NULL,NULL,DIGCF_PRESENT|DIGCF_DEVICEINTERFACE);
    if(set==INVALID_HANDLE_VALUE) { number("enumeration_error=",GetLastError()); ExitProcess(21); }
    ZeroMemory(&iface,sizeof(iface)); iface.cbSize=sizeof(iface);
    if(!SetupDiEnumDeviceInterfaces(set,NULL,&TelemetryGuid,0,&iface)) { number("interface_error=",GetLastError()); ExitProcess(22); }
    detail->cbSize=sizeof(*detail); ZeroMemory(&dev,sizeof(dev)); dev.cbSize=sizeof(dev);
    if(!SetupDiGetDeviceInterfaceDetailA(set,&iface,detail,sizeof(buffer),&needed,&dev)) { number("detail_error=",GetLastError()); ExitProcess(23); }
    file=CreateFileA(detail->DevicePath,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    if(file==INVALID_HANDLE_VALUE) { number("open_error=",GetLastError()); ExitProcess(24); }
    number("cm_result=",CM_Get_DevNode_Status(&status,&problem,dev.DevInst,0));
    number("devnode_status=",status); number("devnode_problem=",problem);
    for(i=0;i<sizeof(cases)/sizeof(cases[0]);++i) {
        BOOL ok;
        ZeroMemory(&out,sizeof(out)); bytes=0;
        ok=DeviceIoControl(file,IOCTL_TELEMETRY,(void*)&cases[i],sizeof(request),&out,sizeof(out),&bytes,NULL);
        number("case=",i); number("transport_ok=",ok); number("error=",ok?0:GetLastError()); number("bytes=",bytes);
        if(ok) { number("version=",out.version); number("result=",out.result); number("polls=",out.polls); number("attempts=",out.attempts); number("status=",out.status); number("data=",out.data); }
    }
    CloseHandle(file); SetupDiDestroyDeviceInfoList(set);
    text("XWN_PCI207_END\r\n"); CloseHandle(log_handle); ExitProcess(0);
}
