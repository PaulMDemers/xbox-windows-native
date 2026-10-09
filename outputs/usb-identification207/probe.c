/* Original NT5 USB evidence collector. No installer, reset, pipe, or registry writes. */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winioctl.h>
#include <setupapi.h>
#include <cfgmgr32.h>
#include <usbioctl.h>
#include <stddef.h>
typedef char ConnectionAbi[(offsetof(USB_NODE_CONNECTION_INFORMATION,PipeList)==35)?1:-1];
typedef char RequestAbi[(sizeof(USB_DESCRIPTOR_REQUEST)==12)?1:-1];

static const GUID HubGuid={0xf18a0e88,0xc30c,0x11d0,{0x88,0x15,0x00,0xa0,0xc9,0x06,0xbe,0xd8}};
static HANDLE Log;
static DWORD Written,Started,RequestId,Failures;
static BYTE Buffer[8192],Detail[2048],Props[4096];
static OVERLAPPED Pending;
static char Line[1024];
static const char Hex[]="0123456789abcdef";

static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static void write(const char *s){DWORD n=lstrlenA(s),w=0;
    if(n>4*1024*1024-Written||!WriteFile(Log,s,n,&w,NULL)||w!=n)ExitProcess(91);
    Written+=n;
}
static void rec(const char *label,DWORD a,DWORD b,DWORD c){
    wsprintfA(Line,"%s %lu %lu %lu\r\n",label,a,b,c);write(Line);
}
static void blob(const char *label,DWORD owner,DWORD kind,const void *data,DWORD n){
    const BYTE *b=data;DWORD i,j;char hex[257];
    if(n>8192)ExitProcess(92);
    wsprintfA(Line,"%s %lu %lu %lu ",label,owner,kind,n);write(Line);
    for(i=0;i<n;){for(j=0;j<128&&i<n;j++,i++){hex[2*j]=Hex[b[i]>>4];hex[2*j+1]=Hex[b[i]&15];}
        hex[2*j]=0;write(hex);}
    write("\r\n");
}
/* Issue and cancel on the SAME thread (NT5 CancelIo contract). Static request
 * storage remains alive until completion. A failed drain aborts the process;
 * it never frees/reuses an outstanding OVERLAPPED or starts another request. */
static BOOL query(HANDLE h,DWORD code,DWORD in,DWORD out,DWORD *bytes){
    BOOL ok;DWORD error=0,wait,id=++RequestId;
    if(GetTickCount()-Started>120000){rec("BUDGET_EXHAUSTED",id,0,0);ExitProcess(94);}
    zero(&Pending,sizeof(Pending));Pending.hEvent=CreateEventA(NULL,TRUE,FALSE,NULL);
    if(!Pending.hEvent)ExitProcess(95);
    *bytes=0;ok=DeviceIoControl(h,code,Buffer,in,Buffer,out,bytes,&Pending);
    if(!ok){error=GetLastError();if(error==ERROR_IO_PENDING){
        wait=WaitForSingleObject(Pending.hEvent,3000);
        if(wait!=WAIT_OBJECT_0){
            rec("CANCEL",id,wait,CancelIo(h));
            wait=WaitForSingleObject(Pending.hEvent,3000);
            if(wait!=WAIT_OBJECT_0){rec("CANCEL_NOT_DRAINED",id,wait,0);FlushFileBuffers(Log);ExitProcess(96);}
        }
        ok=GetOverlappedResult(h,&Pending,bytes,FALSE);error=ok?0:GetLastError();
    }}
    CloseHandle(Pending.hEvent);
    if(*bytes>out){rec("INVALID_LENGTH",id,*bytes,out);ExitProcess(97);}
    rec("IOCTL",id,code,error);rec("IOCTL_RESULT",id,ok,*bytes);
    if(!ok)Failures++;
    return ok;
}
static void descriptors(HANDLE h,DWORD hub,DWORD port,BYTE configs){
    DWORD config,bytes,total;USB_DESCRIPTOR_REQUEST *r=(void *)Buffer;
    if(configs>8){rec("CONFIG_BUDGET",hub,port,configs);Failures++;return;}
    for(config=0;config<configs;config++){
        zero(Buffer,sizeof(Buffer));r->ConnectionIndex=port;
        r->SetupPacket.bmRequest=0x80;r->SetupPacket.bRequest=6;
        r->SetupPacket.wValue=(WORD)(0x200|config);r->SetupPacket.wLength=9;
        rec("CONFIG_REQUEST",hub,port,config);
        if(!query(h,IOCTL_USB_GET_DESCRIPTOR_FROM_NODE_CONNECTION,sizeof(USB_DESCRIPTOR_REQUEST),
                 sizeof(USB_DESCRIPTOR_REQUEST)+9,&bytes))continue;
        blob("CONFIG_HEADER_RAW",hub,port,Buffer,bytes);
        if(bytes!=sizeof(USB_DESCRIPTOR_REQUEST)+9||Buffer[12]!=9||Buffer[13]!=2){
            rec("CONFIG_HEADER_ERROR",hub,port,bytes);Failures++;continue;}
        total=Buffer[14]|((DWORD)Buffer[15]<<8);
        if(total<9||total>4096){rec("CONFIG_LENGTH_ERROR",hub,port,total);Failures++;continue;}
        zero(Buffer,sizeof(Buffer));r->ConnectionIndex=port;
        r->SetupPacket.bmRequest=0x80;r->SetupPacket.bRequest=6;
        r->SetupPacket.wValue=(WORD)(0x200|config);r->SetupPacket.wLength=(WORD)total;
        if(query(h,IOCTL_USB_GET_DESCRIPTOR_FROM_NODE_CONNECTION,sizeof(USB_DESCRIPTOR_REQUEST),
                 sizeof(USB_DESCRIPTOR_REQUEST)+total,&bytes))
            blob("CONFIG_RAW",hub,port,Buffer,bytes);
    }
}
static void hubs(void){
    HDEVINFO set=SetupDiGetClassDevsA(&HubGuid,NULL,NULL,DIGCF_PRESENT|DIGCF_DEVICEINTERFACE);
    SP_DEVICE_INTERFACE_DATA iface;SP_DEVINFO_DATA dev;DWORD i,port,required,bytes,ports,hub;
    HANDLE h;USB_NODE_INFORMATION *node;USB_NODE_CONNECTION_INFORMATION *conn;
    if(set==INVALID_HANDLE_VALUE){rec("HUB_SET_ERROR",GetLastError(),0,0);Failures++;return;}
    for(i=0;i<32;i++){
        zero(&iface,sizeof(iface));iface.cbSize=sizeof(iface);
        if(!SetupDiEnumDeviceInterfaces(set,NULL,&HubGuid,i,&iface)){
            rec("HUB_ENUM_END",i,GetLastError(),0);break;}
        zero(Detail,sizeof(Detail));((SP_DEVICE_INTERFACE_DETAIL_DATA_A *)Detail)->cbSize=sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA_A);
        zero(&dev,sizeof(dev));dev.cbSize=sizeof(dev);
        if(!SetupDiGetDeviceInterfaceDetailA(set,&iface,(void *)Detail,sizeof(Detail),&required,&dev)){
            rec("HUB_DETAIL_ERROR",i,GetLastError(),required);Failures++;continue;}
        if(required>sizeof(Detail)){rec("HUB_DETAIL_ERROR",i,ERROR_INSUFFICIENT_BUFFER,required);Failures++;continue;}
        hub=dev.DevInst;
        blob("HUB_PATH",hub,i,Detail,required);
        h=CreateFileA(((SP_DEVICE_INTERFACE_DETAIL_DATA_A *)Detail)->DevicePath,GENERIC_WRITE,
            FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,FILE_FLAG_OVERLAPPED,NULL);
        if(h==INVALID_HANDLE_VALUE){rec("HUB_OPEN_ERROR",hub,GetLastError(),0);Failures++;continue;}
        zero(Buffer,sizeof(Buffer));node=(void *)Buffer;node->NodeType=UsbHub;
        if(!query(h,IOCTL_USB_GET_NODE_INFORMATION,sizeof(*node),sizeof(*node),&bytes)||bytes<sizeof(*node)){
            rec("HUB_INFO_ERROR",hub,bytes,0);Failures++;CloseHandle(h);continue;}
        blob("HUB_RAW",hub,0,Buffer,bytes);ports=node->u.HubInformation.HubDescriptor.bNumberOfPorts;
        if(ports>32){rec("PORT_BUDGET",hub,ports,0);Failures++;CloseHandle(h);continue;}
        for(port=1;port<=ports;port++){
            BYTE configs;BOOL isHub;
            zero(Buffer,sizeof(Buffer));conn=(void *)Buffer;conn->ConnectionIndex=port;
            rec("PORT_REQUEST",hub,port,0);
            if(!query(h,IOCTL_USB_GET_NODE_CONNECTION_INFORMATION,sizeof(*conn),sizeof(Buffer),&bytes))continue;
            blob("PORT_RAW",hub,port,Buffer,bytes);
            if(bytes<offsetof(USB_NODE_CONNECTION_INFORMATION,PipeList)){Failures++;continue;}
            if(conn->ConnectionStatus!=DeviceConnected)continue;
            configs=conn->DeviceDescriptor.bNumConfigurations;isHub=conn->DeviceIsHub;
            descriptors(h,hub,port,configs);
            zero(Buffer,sizeof(Buffer));*(DWORD *)Buffer=port;
            if(query(h,IOCTL_USB_GET_NODE_CONNECTION_DRIVERKEY_NAME,sizeof(USB_NODE_CONNECTION_DRIVERKEY_NAME),sizeof(Buffer),&bytes))
                blob("DRIVERKEY_RAW",hub,port,Buffer,bytes);
            if(isHub){zero(Buffer,sizeof(Buffer));*(DWORD *)Buffer=port;
                if(query(h,IOCTL_USB_GET_NODE_CONNECTION_NAME,sizeof(USB_NODE_CONNECTION_NAME),sizeof(Buffer),&bytes))
                    blob("CHILD_HUB_RAW",hub,port,Buffer,bytes);}
        }
        CloseHandle(h);
    }
    if(i==32){rec("HUB_BUDGET",i,0,0);Failures++;}
    SetupDiDestroyDeviceInfoList(set);
}
static void devices(void){
    static const DWORD props[]={SPDRP_DEVICEDESC,SPDRP_HARDWAREID,SPDRP_COMPATIBLEIDS,SPDRP_SERVICE,SPDRP_DRIVER,SPDRP_LOCATION_INFORMATION,SPDRP_CONFIGFLAGS};
    HDEVINFO set=SetupDiGetClassDevsA(NULL,NULL,NULL,DIGCF_PRESENT|DIGCF_ALLCLASSES);
    SP_DEVINFO_DATA d;DWORD i,j,type,required,status,problem;DEVINST parent;CONFIGRET cr;char id[512];
    if(set==INVALID_HANDLE_VALUE){rec("DEVICE_SET_ERROR",GetLastError(),0,0);Failures++;return;}
    for(i=0;i<256;i++){
        zero(&d,sizeof(d));d.cbSize=sizeof(d);
        if(!SetupDiEnumDeviceInfo(set,i,&d)){rec("DEVICE_ENUM_END",i,GetLastError(),0);break;}
        cr=CM_Get_Device_IDA(d.DevInst,id,sizeof(id),0);id[511]=0;
        if(cr==CR_SUCCESS)blob("DEVICE_ID",d.DevInst,i,id,lstrlenA(id));
        else{rec("DEVICE_ID_ERROR",d.DevInst,cr,0);Failures++;}
        status=problem=0;cr=CM_Get_DevNode_Status(&status,&problem,d.DevInst,0);
        rec("DEVICE_STATUS",d.DevInst,status,problem);rec("DEVICE_STATUS_RESULT",d.DevInst,cr,0);
        parent=0;cr=CM_Get_Parent(&parent,d.DevInst,0);rec("DEVICE_PARENT",d.DevInst,cr,parent);
        for(j=0;j<sizeof(props)/sizeof(props[0]);j++){
            required=type=0;
            if(SetupDiGetDeviceRegistryPropertyA(set,&d,props[j],&type,Props,sizeof(Props),&required)&&required<=sizeof(Props)){
                rec("PROPERTY_TYPE",d.DevInst,props[j],type);blob("PROPERTY",d.DevInst,props[j],Props,required);
            }else rec("PROPERTY_UNAVAILABLE",d.DevInst,props[j],GetLastError());
        }
    }
    if(i==256){rec("DEVICE_BUDGET",i,0,0);Failures++;}
    SetupDiDestroyDeviceInfoList(set);
}
void WINAPI mainCRTStartup(void){
    char path[MAX_PATH];DWORD n=GetModuleFileNameA(NULL,path,sizeof(path));
    if(!n||n>=sizeof(path)-16)ExitProcess(90);
    while(n&&path[n-1]!='\\')n--;
    if(!n)ExitProcess(90);
    lstrcpyA(path+n,"usb.log");
    Log=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
    Started=GetTickCount();rec("USB_PROBE_BEGIN",1,GetCurrentProcessId(),0);
    devices();hubs();rec("USB_PROBE_END",RequestId,Failures,GetTickCount()-Started);
    FlushFileBuffers(Log);CloseHandle(Log);ExitProcess(Failures?2:0);
}
