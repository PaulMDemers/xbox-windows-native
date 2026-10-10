/* SPDX-License-Identifier: MIT
 * Genuine NT5 PnP restart of the exact resource-only target. No SMBus access.
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <winioctl.h>
#include <setupapi.h>
#include <cfgmgr32.h>
static const GUID TelemetryGuid={0x4cecfd27,0x4cde,0x4cc9,{0xa2,0x92,0xd5,0xcf,0x42,0x3e,0x57,0x07}};
static HANDLE log_handle;
static void clear_bytes(void *p,DWORD n){volatile BYTE *b=p;while(n--)*b++=0;}
static void text(const char *s){DWORD n;WriteFile(log_handle,s,lstrlenA(s),&n,NULL);FlushFileBuffers(log_handle);}
static void number(const char *name,DWORD v){char b[16];unsigned i=sizeof(b);b[--i]=0;b[--i]='\n';b[--i]='\r';do{b[--i]=(char)('0'+v%10);v/=10;}while(v);text(name);text(b+i);}
#include "restart.h"
#include "power-test.h"
static BOOL query(void)
{
    HDEVINFO set;SP_DEVICE_INTERFACE_DATA iface;SP_DEVINFO_DATA dev;
    static BYTE buffer[2048];PSP_DEVICE_INTERFACE_DETAIL_DATA_A detail=(void*)buffer;
    HANDLE file;DWORD needed,bytes=0,v[10],req[3]={1,0x10,4},reply[6],error;BOOL ok;
    const char *names[]={"version=","profile=","port=","started=","powered=","starts=","stops=","queries=","powers=","telemetry_enabled="};unsigned i;
    set=SetupDiGetClassDevsA(&TelemetryGuid,NULL,NULL,DIGCF_PRESENT|DIGCF_DEVICEINTERFACE);
    if(set==INVALID_HANDLE_VALUE)return FALSE;
    clear_bytes(&iface,sizeof(iface));iface.cbSize=sizeof(iface);
    if(!SetupDiEnumDeviceInterfaces(set,NULL,&TelemetryGuid,0,&iface)){number("interface_error=",GetLastError());SetupDiDestroyDeviceInfoList(set);return FALSE;}
    detail->cbSize=sizeof(*detail);clear_bytes(&dev,sizeof(dev));dev.cbSize=sizeof(dev);
    if(!SetupDiGetDeviceInterfaceDetailA(set,&iface,detail,sizeof(buffer),&needed,&dev)){number("detail_error=",GetLastError());SetupDiDestroyDeviceInfoList(set);return FALSE;}
    file=CreateFileA(detail->DevicePath,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    SetupDiDestroyDeviceInfoList(set);
    if(file==INVALID_HANDLE_VALUE){number("open_error=",GetLastError());return FALSE;}
    clear_bytes(v,sizeof(v));ok=DeviceIoControl(file,CTL_CODE(FILE_DEVICE_UNKNOWN,0x808,METHOD_BUFFERED,FILE_READ_ACCESS),NULL,0,v,sizeof(v),&bytes,NULL);
    number("query_ok=",ok);number("query_error=",ok?0:GetLastError());number("query_bytes=",bytes);
    if(ok)for(i=0;i<10;++i)number(names[i],v[i]);
    ok=ok && bytes==sizeof(v) && v[0]==1 && v[1]==2 && v[2]==0xc000 && v[3]==1 && v[4]==1 && v[9]==0;
    bytes=0;
    if(DeviceIoControl(file,CTL_CODE(FILE_DEVICE_UNKNOWN,0x807,METHOD_BUFFERED,FILE_READ_ACCESS),req,sizeof(req),reply,sizeof(reply),&bytes,NULL)){text("UNEXPECTED_TELEMETRY_SUCCESS\r\n");ok=FALSE;}
    else{error=GetLastError();number("telemetry_error=",error);if(error!=ERROR_NOT_SUPPORTED || bytes)ok=FALSE;}
    CloseHandle(file);return ok;
}
#include "remove-test.h"
void WINAPI mainCRTStartup(void)
{
    HDEVINFO set;SP_DEVINFO_DATA dev;SP_PROPCHANGE_PARAMS change;SP_DEVINSTALL_PARAMS_A params;
    DWORD i,type,needed,status,problem,cm,capabilities=0;BOOL found=FALSE,ok;static char ids[2048];
    log_handle=CreateFileA("C:\\xwnpcilife2\\lifecycle.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(log_handle==INVALID_HANDLE_VALUE)ExitProcess(20);
    text("RESOURCE_ONLY_PNP_LIFECYCLE_BEGIN\r\n");
    set=SetupDiGetClassDevsA(NULL,"PCI",NULL,DIGCF_PRESENT|DIGCF_ALLCLASSES);
    if(set==INVALID_HANDLE_VALUE)ExitProcess(21);
    for(i=0;;++i){
        clear_bytes(&dev,sizeof(dev));dev.cbSize=sizeof(dev);
        if(!SetupDiEnumDeviceInfo(set,i,&dev))break;
        clear_bytes(ids,sizeof(ids));
        if(!SetupDiGetDeviceRegistryPropertyA(set,&dev,SPDRP_HARDWAREID,&type,(BYTE*)ids,sizeof(ids),&needed))continue;
        if(lstrcmpiA(ids,"PCI\\VEN_10DE&DEV_01B4&SUBSYS_00000000&REV_B1"))continue;
        found=TRUE;break;
    }
    if(!found)ExitProcess(22);
    status=problem=0;cm=CM_Get_DevNode_Status(&status,&problem,dev.DevInst,0);
    number("cm_result=",cm);number("devnode_status=",status);number("devnode_problem=",problem);
    if(cm || problem || !(status&DN_STARTED) || !query())ExitProcess(23);
    /* All interface handles are closed before asking PnP to stop/restart. */
    clear_bytes(&change,sizeof(change));change.ClassInstallHeader.cbSize=sizeof(change.ClassInstallHeader);
    change.ClassInstallHeader.InstallFunction=DIF_PROPERTYCHANGE;change.StateChange=DICS_PROPCHANGE;change.Scope=DICS_FLAG_CONFIGSPECIFIC;
    text("PNP_RESTART_REQUEST\r\n");
    ok=SetupDiSetClassInstallParamsA(set,&dev,&change.ClassInstallHeader,sizeof(change));
    if(ok)ok=SetupDiCallClassInstaller(DIF_PROPERTYCHANGE,set,&dev);
    number("pnp_restart_ok=",ok);number("pnp_restart_error=",ok?0:GetLastError());
    if(!ok)ExitProcess(24);
    clear_bytes(&params,sizeof(params));params.cbSize=sizeof(params);
    if(!SetupDiGetDeviceInstallParamsA(set,&dev,&params))ExitProcess(25);
    number("install_flags=",params.Flags);
    if(params.Flags&(DI_NEEDREBOOT|DI_NEEDRESTART)){text("PNP_RESTART_DEFERRED\r\n");ExitProcess(26);}
    SetupDiDestroyDeviceInfoList(set);Sleep(1000);
    if(!query())ExitProcess(27);
    if(!exercise_power() || !query())ExitProcess(28);
    /* Read capabilities of the exact instance retained above. */
    if(CM_Get_DevNode_Registry_PropertyA(dev.DevInst,CM_DRP_CAPABILITIES,&type,&capabilities,&(ULONG){sizeof(capabilities)},0)!=CR_SUCCESS)ExitProcess(29);
    if(!exercise_remove(dev.DevInst,capabilities))ExitProcess(29);
    text("RESOURCE_ONLY_PNP_LIFECYCLE_END\r\n");
    guarded_restart();CloseHandle(log_handle);ExitProcess(0);
}
