/* SPDX-License-Identifier: MIT -- OS-generated rebalance; no fabricated IRPs. */
static BOOL rebalance_call(HANDLE file,DWORD action,DWORD *v)
{
    DWORD req[2]={1,action},bytes=0;BOOL ok;
    clear_bytes(v,48);ok=DeviceIoControl(file,CTL_CODE(FILE_DEVICE_UNKNOWN,0x80b,METHOD_BUFFERED,FILE_READ_ACCESS),req,sizeof(req),v,48,&bytes,NULL);
    if(!ok)number("rebalance_ioctl_error=",GetLastError());
    return ok && bytes==48 && v[0]==1;
}
static BOOL exercise_rebalance(DEVINST instance)
{
    HDEVINFO set;SP_DEVICE_INTERFACE_DATA iface;SP_DEVINFO_DATA dev;
    static BYTE buffer[2048];PSP_DEVICE_INTERFACE_DETAIL_DATA_A detail=(void*)buffer;
    HANDLE file;DWORD needed,phase,start,before[12],v[12],cleanup[12],i;BOOL ok=FALSE,ready;char mode_text[4];DWORD mode;
    const char *labels[]={"rb_version=","rb_pending=","rb_state_queries=","rb_query_stops=","rb_cancel_stops=","rb_stops=","rb_starts=","rb_started=","rb_powered=","rb_query_gate=","rb_veto_armed=","rb_queries="};
    clear_bytes(mode_text,sizeof(mode_text));
    if(GetEnvironmentVariableA("XWN_REBALANCE_MODE",mode_text,sizeof(mode_text))!=1 || mode_text[0]<'0' || mode_text[0]>'2')return FALSE;
    mode=(DWORD)(mode_text[0]-'0');number("rebalance_mode=",mode);mark("rebalance_begin");
    if(!mode){text("REBALANCE_SKIP_CONTROL\r\n");Sleep(10000);mark("rebalance_end");return query();}
    set=SetupDiGetClassDevsA(&TelemetryGuid,NULL,NULL,DIGCF_PRESENT|DIGCF_DEVICEINTERFACE);
    if(set==INVALID_HANDLE_VALUE)return FALSE;
    clear_bytes(&iface,sizeof(iface));iface.cbSize=sizeof(iface);
    clear_bytes(&dev,sizeof(dev));dev.cbSize=sizeof(dev);detail->cbSize=sizeof(*detail);
    ready=SetupDiEnumDeviceInterfaces(set,NULL,&TelemetryGuid,0,&iface) && SetupDiGetDeviceInterfaceDetailA(set,&iface,detail,sizeof(buffer),&needed,&dev) && dev.DevInst==instance;
    if(!ready){SetupDiDestroyDeviceInfoList(set);return FALSE;}
    file=CreateFileA(detail->DevicePath,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    SetupDiDestroyDeviceInfoList(set);if(file==INVALID_HANDLE_VALUE)return FALSE;
    for(phase=mode-1;phase<mode;++phase){
        if(!rebalance_call(file,0,before))goto done;
        number("rebalance_phase=",phase);text(phase?"REBALANCE_ONESHOT_VETO_REQUEST\r\n":"REBALANCE_ALLOW_REQUEST\r\n");
        if(!rebalance_call(file,phase?1:2,v))goto done;
        start=GetTickCount();ready=FALSE;
        do{
            Sleep(100);if(!rebalance_call(file,0,v))goto done;
            ready=v[2]>before[2] && v[3]>before[3] && v[7]==1 && v[8]==1 && v[9]==0 && !v[1] && !v[10];
            if(phase)ready=ready && v[4]>before[4] && v[5]==before[5] && v[6]==before[6];
            else ready=ready && v[5]>before[5] && v[6]>before[6];
        }while(!ready && GetTickCount()-start<10000);
        for(i=0;i<12;++i)number(labels[i],v[i]);
        if(!ready){text("REBALANCE_HELD_MISSING_EXPECTED_IRPS\r\n");goto done;}
        if(!query())goto done;
        text(phase?"REBALANCE_CANCEL_RECOVERED\r\n":"REBALANCE_STOP_RECOVERED\r\n");
    }
    ok=TRUE;
done:
    /* Withdraw one-shot diagnostic flags even if expected IRPs never arrived. */
    number("rebalance_disarm_ok=",rebalance_call(file,3,cleanup));
    CloseHandle(file);mark("rebalance_operation_end");Sleep(10000);mark("rebalance_end");return ok;
}
