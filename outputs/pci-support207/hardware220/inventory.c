/* SPDX-License-Identifier: MIT
 * NT5 present-PCI and OS resource inventory. No hardware/configuration writes,
 * service installation, dialog actions or automatic restart.
 * CM_*_Handle frees only caller-owned handles, never the configuration itself.
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <setupapi.h>
#include <cfgmgr32.h>
static HANDLE log_file;
static DWORD written;
static BYTE data[4096];
static char encoded[8193];
static void text(const char *s)
{
    DWORD n=lstrlenA(s),done=0;
    if(n>1024*1024-written || !WriteFile(log_file,s,n,&done,NULL) || done!=n)ExitProcess(91);
    written+=n;
}
static void number(const char *key,DWORD value)
{
    char b[16];unsigned i=sizeof(b);b[--i]=0;b[--i]='\n';b[--i]='\r';
    do {b[--i]=(char)('0'+value%10);value/=10;}while(value);
    text(key);text(b+i);
}
static void blob(const BYTE *bytes,DWORD size)
{
    static const char hex[]="0123456789abcdef";DWORD i;
    if(size>sizeof(data))ExitProcess(92);
    for(i=0;i<size;i++){encoded[i*2]=hex[bytes[i]>>4];encoded[i*2+1]=hex[bytes[i]&15];}
    encoded[size*2]=0;text("hex=");text(encoded);text("\r\n");
}
static void resources(DEVINST dev,ULONG flags)
{
    LOG_CONF conf,next_conf;RES_DES previous,next;RESOURCEID type;
    CONFIGRET cr;ULONG size;unsigned c,r;BOOL have_resource;
    number("configuration_type=",flags);
    cr=CM_Get_First_Log_Conf(&conf,dev,flags);number("first_configuration_result=",cr);
    if(cr!=CR_SUCCESS)return;
    for(c=0;c<8;c++){
        number("configuration_index=",c);previous=(RES_DES)conf;have_resource=FALSE;
        for(r=0;r<64;r++){
            type=0;cr=CM_Get_Next_Res_Des(&next,previous,ResType_All,&type,0);
            if(have_resource){number("free_resource_handle=",CM_Free_Res_Des_Handle(previous));have_resource=FALSE;}
            number("next_resource_result=",cr);
            if(cr!=CR_SUCCESS)break;
            previous=next;have_resource=TRUE;
            number("resource_index=",r);number("resource_type=",type);
            size=0;cr=CM_Get_Res_Des_Data_Size(&size,next,0);number("resource_size_result=",cr);number("resource_size=",size);
            if(cr==CR_SUCCESS && size && size<=sizeof(data)){
                cr=CM_Get_Res_Des_Data(next,data,size,0);number("resource_data_result=",cr);
                if(cr==CR_SUCCESS)blob(data,size);
            }
        }
        if(have_resource)number("free_resource_handle=",CM_Free_Res_Des_Handle(previous));
        if(r==64)text("resource_bound_reached=1\r\n");
        cr=CM_Get_Next_Log_Conf(&next_conf,conf,0);
        number("free_configuration_handle=",CM_Free_Log_Conf_Handle(conf));
        number("next_configuration_result=",cr);
        if(cr!=CR_SUCCESS)break;
        conf=next_conf;
    }
    if(c==8){CM_Free_Log_Conf_Handle(conf);text("configuration_bound_reached=1\r\n");}
}
void WINAPI mainCRTStartup(void)
{
    static const DWORD props[]={SPDRP_DEVICEDESC,SPDRP_HARDWAREID,SPDRP_COMPATIBLEIDS,
        SPDRP_CLASSGUID,SPDRP_SERVICE,SPDRP_DRIVER,SPDRP_CONFIGFLAGS,
        SPDRP_LOCATION_INFORMATION,SPDRP_BUSNUMBER,SPDRP_ADDRESS};
    HDEVINFO set;SP_DEVINFO_DATA dev;DWORD i,j,n,type,needed,status,problem;CONFIGRET cr;
    char base[MAX_PATH],path[MAX_PATH],id[512];
    n=GetModuleFileNameA(NULL,base,sizeof(base));if(!n || n>=sizeof(base)-32)ExitProcess(90);
    while(n && base[n-1]!='\\')n--;
    if(!n)ExitProcess(90);
    base[n]=0;
    for(i=0;i<=n;i++)path[i]=base[i];
    {const char *tail="inventory.log";for(i=0;tail[i];i++)path[n+i]=tail[i];path[n+i]=0;}
    log_file=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(log_file==INVALID_HANDLE_VALUE)ExitProcess(90);
    text("XWN_PCI_INVENTORY220 version=1\r\n");
    set=SetupDiGetClassDevsA(NULL,"PCI",NULL,DIGCF_PRESENT|DIGCF_ALLCLASSES);
    if(set==INVALID_HANDLE_VALUE){number("device_set_error=",GetLastError());ExitProcess(93);}
    for(i=0;i<256;i++){
        dev.cbSize=sizeof(dev);
        if(!SetupDiEnumDeviceInfo(set,i,&dev)){number("enumeration_end_error=",GetLastError());break;}
        number("device_index=",i);cr=CM_Get_Device_IDA(dev.DevInst,id,sizeof(id),0);id[511]=0;
        number("device_id_result=",cr);if(cr==CR_SUCCESS){text("device_id=");text(id);text("\r\n");}
        status=problem=0;cr=CM_Get_DevNode_Status(&status,&problem,dev.DevInst,0);
        number("status_result=",cr);number("status=",status);number("problem=",problem);
        for(j=0;j<sizeof(props)/sizeof(props[0]);j++){
            type=needed=0;number("property=",props[j]);
            if(SetupDiGetDeviceRegistryPropertyA(set,&dev,props[j],&type,data,sizeof(data),&needed)){
                number("property_type=",type);number("property_bytes=",needed);blob(data,needed);
            }else number("property_error=",GetLastError());
        }
        resources(dev.DevInst,ALLOC_LOG_CONF);resources(dev.DevInst,BOOT_LOG_CONF);
        if(!FlushFileBuffers(log_file))ExitProcess(94);
    }
    if(i==256)text("device_bound_reached=1\r\n");
    SetupDiDestroyDeviceInfoList(set);number("devices=",i);
    text("NO_PCI_SMBUS_AC97_WRITES\r\nNO_INSTALL_OR_DIALOG_ACTION\r\nCOMPLETE220\r\n");
    if(!FlushFileBuffers(log_file))ExitProcess(94);
    CloseHandle(log_file);ExitProcess(0);
}
