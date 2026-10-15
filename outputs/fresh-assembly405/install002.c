/* Genuine NT5 PnP installation for the one pinned ACI ID. SPDX-License-Identifier: MIT */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <setupapi.h>
#include <cfgmgr32.h>
typedef BOOL (WINAPI *UPDATE_DRIVER)(HWND,LPCSTR,LPCSTR,DWORD,PBOOL);
typedef CONFIGRET (WINAPI *DEV_STATUS)(PULONG,PULONG,DEVINST,ULONG);
static const char *HardwareId="PCI\\VEN_10DE&DEV_01B1&SUBSYS_00000000&REV_B1";
static HANDLE Log;
static const char *InfName="xwnaci207.inf", *ExpectedService="xwnaci207";
static void line(const char *tag,const char *value) {
    char text[768];DWORD n,w;n=wsprintfA(text,"%s %s\r\n",tag,value);
    if(n>=sizeof(text)||!WriteFile(Log,text,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);
}
static void number(const char *tag,DWORD value){char text[24];wsprintfA(text,"%lu",value);line(tag,text);}
static void fail(const char *tag,DWORD code){number(tag,code);ExitProcess(1);}
static HDEVINFO target(SP_DEVINFO_DATA *chosen) {
    HDEVINFO set;SP_DEVINFO_DATA info;DWORD index,found=0,type,required,n,at;char ids[1024],instance[256];
    set=SetupDiGetClassDevsA(NULL,"PCI",NULL,DIGCF_PRESENT|DIGCF_ALLCLASSES);
    if(set==INVALID_HANDLE_VALUE)fail("FAIL_DEVICE_SET",GetLastError());
    for(index=0;;index++) {
        info.cbSize=sizeof(info);
        if(!SetupDiEnumDeviceInfo(set,index,&info)) {
            if(GetLastError()!=ERROR_NO_MORE_ITEMS)fail("FAIL_ENUMERATE",GetLastError());break;
        }
        if(!SetupDiGetDeviceRegistryPropertyA(set,&info,SPDRP_HARDWAREID,&type,(PBYTE)ids,sizeof(ids),&required))continue;
        if(type!=REG_MULTI_SZ||required<2||required>sizeof(ids)||ids[required-1]||ids[required-2])fail("FAIL_MALFORMED_ID",index);
        for(at=0;at<required-1&&ids[at];at+=n+1) {
            for(n=0;at+n<required&&ids[at+n];n++){}
            if(at+n>=required)fail("FAIL_ID_BOUND",index);
            if(!lstrcmpiA(ids+at,HardwareId)) {
                *chosen=info;found++;
                if(!SetupDiGetDeviceInstanceIdA(set,&info,instance,sizeof(instance),&required))fail("FAIL_INSTANCE",GetLastError());
                line("TARGET_INSTANCE",instance);break;
            }
        }
    }
    number("EXACT_TARGET_COUNT",found);if(found!=1)fail("FAIL_TARGET_COUNT",found);
    return set;
}
void WINAPI mainCRTStartup(void) {
    char base[MAX_PATH],path[MAX_PATH],system[MAX_PATH],service[128];DWORD n,type,required,error;
    HDEVINFO set;SP_DEVINFO_DATA device;UPDATE_DRIVER update;DEV_STATUS status;HMODULE module;BOOL reboot=FALSE,result;
    ULONG flags=0,problem=0;CONFIGRET cr;
    { const char *cmd=GetCommandLineA(); DWORD size=lstrlenA(cmd);
      if(size>=8 && !lstrcmpiA(cmd+size-8," network")) {
        HardwareId="PCI\\VEN_10DE&DEV_01C3"; InfName="nvnetnt5.inf"; ExpectedService="nvnetnt5";
      }
    }
    n=GetModuleFileNameA(NULL,base,sizeof(base));if(!n||n>=sizeof(base)-48)ExitProcess(90);
    while(n&&base[n-1]!='\\')n--;if(!n)ExitProcess(90);base[n-1]=0;
    wsprintfA(path,"%s\\install207.log",base);
    Log=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
    line("INSTALL207_BEGIN",HardwareId);
    n=GetSystemDirectoryA(system,sizeof(system));if(!n||n>=sizeof(system)-24)fail("FAIL_SYSTEM_PATH",n);
    wsprintfA(path,"%s\\newdev.dll",system);module=LoadLibraryA(path);if(!module)fail("FAIL_NEWDEV_LOAD",GetLastError());
    update=(UPDATE_DRIVER)GetProcAddress(module,"UpdateDriverForPlugAndPlayDevicesA");
    wsprintfA(path,"%s\\cfgmgr32.dll",system);module=LoadLibraryA(path);if(!module)fail("FAIL_CFGMGR_LOAD",GetLastError());
    status=(DEV_STATUS)GetProcAddress(module,"CM_Get_DevNode_Status");
    if(!update||!status)fail("FAIL_REQUIRED_EXPORT",GetLastError());
    set=target(&device);
    if(SetupDiGetDeviceRegistryPropertyA(set,&device,SPDRP_SERVICE,&type,(PBYTE)service,sizeof(service),&required)) {
        if(type!=REG_SZ||!required||required>sizeof(service)||service[required-1])fail("FAIL_SERVICE_STRING",required);
        line("BEFORE_SERVICE",service);
    }
    SetupDiDestroyDeviceInfoList(set);
    wsprintfA(path,"%s\\%s",base,InfName);line("INF_PATH",path);
    number("INSTALL_FLAGS",1); /* documented force-selection, no invented silent flag */
    result=update(NULL,HardwareId,path,1,&reboot);error=result?0:GetLastError();
    number("UPDATE_RESULT",result);number("UPDATE_ERROR",error);number("REBOOT_REQUIRED",reboot);
    if(!result)fail("FAIL_UPDATE",error);
    set=target(&device);
    if(!SetupDiGetDeviceRegistryPropertyA(set,&device,SPDRP_SERVICE,&type,(PBYTE)service,sizeof(service),&required))fail("FAIL_SERVICE_QUERY",GetLastError());
    if(type!=REG_SZ||!required||required>sizeof(service)||service[required-1])fail("FAIL_SERVICE_STRING",required);
    line("AFTER_SERVICE",service);if(lstrcmpiA(service,ExpectedService))fail("FAIL_WRONG_SERVICE",0);
    cr=status(&flags,&problem,device.DevInst,0);number("DEVNODE_STATUS_RESULT",cr);number("DEVNODE_FLAGS",flags);number("DEVNODE_PROBLEM",problem);
    if(cr!=CR_SUCCESS)fail("FAIL_DEVNODE_QUERY",cr);
    if((flags&DN_HAS_PROBLEM)&&!reboot)fail("FAIL_DEVNODE_PROBLEM",problem);
    SetupDiDestroyDeviceInfoList(set);number("INSTALL207_END",0);CloseHandle(Log);ExitProcess(0);
}
