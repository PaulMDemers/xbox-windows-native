/* SPDX-License-Identifier: MIT
 * Emulator repeat-boot telemetry and guarded normal restart. No dialog actions.
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
static void clear_bytes(void *p,DWORD n) { volatile BYTE *b=p; while(n--)*b++=0; }
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
static void guarded_restart(void);
void WINAPI mainCRTStartup(void)
{
    HDEVINFO set; SP_DEVICE_INTERFACE_DATA iface; SP_DEVINFO_DATA dev;
    BYTE buffer[2048]; PSP_DEVICE_INTERFACE_DETAIL_DATA_A detail=(void*)buffer;
    HANDLE file; DWORD needed,bytes,i,status=0,problem=0,attempt,error,cm,valid=1; response out;
    char path[]="C:\\xwnpci207\\cycle-00.log";
    const request cases[]={{1,0x10,4},{1,0x4c,0},{1,0x4c,1},{1,0x54,0},{1,0x10,0x11},{1,0x10,4}};
    for(attempt=0;attempt<32;++attempt) {
        DWORD length=lstrlenA(path);path[length-6]=(char)('0'+attempt/10);path[length-5]=(char)('0'+attempt%10);
        log_handle=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
        if(log_handle!=INVALID_HANDLE_VALUE)break;
        error=GetLastError();if(error!=ERROR_FILE_EXISTS && error!=ERROR_ALREADY_EXISTS)ExitProcess(20);
    }
    if(log_handle==INVALID_HANDLE_VALUE) ExitProcess(20);
    text("XWN_PCI207_BEGIN version=1\r\n");
    number("log_index=",attempt);
    set=SetupDiGetClassDevsA(&TelemetryGuid,NULL,NULL,DIGCF_PRESENT|DIGCF_DEVICEINTERFACE);
    if(set==INVALID_HANDLE_VALUE) { number("enumeration_error=",GetLastError()); ExitProcess(21); }
    clear_bytes(&iface,sizeof(iface)); iface.cbSize=sizeof(iface);
    if(!SetupDiEnumDeviceInterfaces(set,NULL,&TelemetryGuid,0,&iface)) { number("interface_error=",GetLastError()); ExitProcess(22); }
    detail->cbSize=sizeof(*detail); clear_bytes(&dev,sizeof(dev)); dev.cbSize=sizeof(dev);
    if(!SetupDiGetDeviceInterfaceDetailA(set,&iface,detail,sizeof(buffer),&needed,&dev)) { number("detail_error=",GetLastError()); ExitProcess(23); }
    file=CreateFileA(detail->DevicePath,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    if(file==INVALID_HANDLE_VALUE) { number("open_error=",GetLastError()); ExitProcess(24); }
    cm=CM_Get_DevNode_Status(&status,&problem,dev.DevInst,0);number("cm_result=",cm);
    if(cm || problem || !(status&8))valid=0;
    number("devnode_status=",status); number("devnode_problem=",problem);
    for(i=0;i<sizeof(cases)/sizeof(cases[0]);++i) {
        BOOL ok;
        clear_bytes(&out,sizeof(out)); bytes=0;
        ok=DeviceIoControl(file,IOCTL_TELEMETRY,(void*)&cases[i],sizeof(request),&out,sizeof(out),&bytes,NULL);
        error=ok?0:GetLastError();
        if(i==3 || i==4) { if(ok || error!=ERROR_INVALID_PARAMETER || bytes)valid=0; }
        else if(!ok || bytes!=24 || out.version!=1 || out.result || out.data!=((i==1 || i==2)?50:6))valid=0;
        number("case=",i); number("transport_ok=",ok); number("error=",ok?0:GetLastError()); number("bytes=",bytes);
        if(ok) { number("version=",out.version); number("result=",out.result); number("polls=",out.polls); number("attempts=",out.attempts); number("status=",out.status); number("data=",out.data); }
    }
    CloseHandle(file); SetupDiDestroyDeviceInfoList(set);
    text("XWN_PCI207_END\r\n");number("telemetry_valid=",valid);
    if(!valid)ExitProcess(30);
    guarded_restart();CloseHandle(log_handle);ExitProcess(0);
}
static void guarded_restart(void)
{
    typedef DWORD (WINAPI *wait_install)(DWORD);
    wait_install wait;HANDLE token;TOKEN_PRIVILEGES tp;DWORD state,start,idle=0;
    BOOL have_idle=FALSE,ok;
    wait=(wait_install)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");
    if(!wait){number("setup_lookup_error=",GetLastError());ExitProcess(31);}
    /* Require five continuous seconds idle, bounded by thirty seconds. */
    start=GetTickCount();
    for(;;) {
        state=wait(0);
        if(state!=WAIT_OBJECT_0 && state!=WAIT_TIMEOUT){number("setup_query_failure=",state);ExitProcess(32);}
        if(state==WAIT_OBJECT_0) {
            if(!have_idle){idle=GetTickCount();have_idle=TRUE;}
            if(GetTickCount()-idle>=5000)break;
        } else have_idle=FALSE;
        if(GetTickCount()-start>=30000){number("restart_blocked_pending_install=",state);ExitProcess(33);}
        Sleep(250);
    }
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(34);
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(35);
    SetLastError(ERROR_SUCCESS);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)ExitProcess(36);
    CloseHandle(token);
    state=wait(0);number("pre_restart_install_state=",state);
    if(state!=WAIT_OBJECT_0){number("restart_blocked_recheck=",state);ExitProcess(37);}
    text("normal_restart_request\r\n");ok=ExitWindowsEx(EWX_REBOOT,0);
    number("normal_restart_accepted=",ok);if(!ok)number("restart_error=",GetLastError());
}
