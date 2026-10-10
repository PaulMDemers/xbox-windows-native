/* SPDX-License-Identifier: MIT -- disposable resource-only test endpoint. */
static BOOL exercise_power(void)
{
    HDEVINFO set;SP_DEVICE_INTERFACE_DATA iface;SP_DEVINFO_DATA dev;
    static BYTE buffer[2048];PSP_DEVICE_INTERFACE_DETAIL_DATA_A detail=(void*)buffer;
    HANDLE file;DWORD needed,bytes,request[2],reply[3],i,j;BOOL ok,valid=TRUE;
    set=SetupDiGetClassDevsA(&TelemetryGuid,NULL,NULL,DIGCF_PRESENT|DIGCF_DEVICEINTERFACE);
    if(set==INVALID_HANDLE_VALUE)return FALSE;
    clear_bytes(&iface,sizeof(iface));iface.cbSize=sizeof(iface);
    clear_bytes(&dev,sizeof(dev));dev.cbSize=sizeof(dev);detail->cbSize=sizeof(*detail);
    if(!SetupDiEnumDeviceInterfaces(set,NULL,&TelemetryGuid,0,&iface) ||
       !SetupDiGetDeviceInterfaceDetailA(set,&iface,detail,sizeof(buffer),&needed,&dev)){
        SetupDiDestroyDeviceInfoList(set);return FALSE;
    }
    file=CreateFileA(detail->DevicePath,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    SetupDiDestroyDeviceInfoList(set);if(file==INVALID_HANDLE_VALUE)return FALSE;
    for(i=0;i<3;++i){
        for(j=0;j<2;++j){
            request[0]=1;request[1]=j?1:4; /* D0 after every D3, including failure. */
            bytes=0;clear_bytes(reply,sizeof(reply));
            ok=DeviceIoControl(file,CTL_CODE(FILE_DEVICE_UNKNOWN,0x809,METHOD_BUFFERED,FILE_READ_ACCESS),request,sizeof(request),reply,sizeof(reply),&bytes,NULL);
            number("power_round=",i);number("power_target=",request[1]);number("power_ioctl_ok=",ok);number("power_ioctl_error=",ok?0:GetLastError());number("power_bytes=",bytes);
            if(ok){number("power_completed_target=",reply[0]);number("power_status=",reply[1]);number("power_gate=",reply[2]);}
            if(!ok || bytes!=12 || reply[0]!=request[1] || reply[1] || reply[2]!=(j?1U:0U))valid=FALSE;
        }
        if(!valid)break;
    }
    CloseHandle(file);return valid;
}
