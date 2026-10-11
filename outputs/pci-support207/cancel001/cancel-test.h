/* SPDX-License-Identifier: MIT
 * Genuine NT5 open-handle veto; do not register an earlier user-mode veto.
 * Caller has already checked the exact leaf and acquired SeLoadDriverPrivilege.
 */
static BOOL exercise_cancel(DEVINST instance)
{
    HDEVINFO set;SP_DEVICE_INTERFACE_DATA iface;SP_DEVINFO_DATA dev;
    static BYTE buffer[2048];PSP_DEVICE_INTERFACE_DETAIL_DATA_A detail=(void*)buffer;
    DWORD needed,bytes=0,before[10],after[10];BOOL ok;HANDLE file;
    CONFIGRET cr;PNP_VETO_TYPE veto=PNP_VetoTypeUnknown;WCHAR name[MAX_PATH];char utf8[MAX_PATH*3];
    set=SetupDiGetClassDevsA(&TelemetryGuid,NULL,NULL,DIGCF_PRESENT|DIGCF_DEVICEINTERFACE);
    if(set==INVALID_HANDLE_VALUE)return FALSE;
    clear_bytes(&iface,sizeof(iface));iface.cbSize=sizeof(iface);
    clear_bytes(&dev,sizeof(dev));dev.cbSize=sizeof(dev);detail->cbSize=sizeof(*detail);
    ok=SetupDiEnumDeviceInterfaces(set,NULL,&TelemetryGuid,0,&iface) &&
       SetupDiGetDeviceInterfaceDetailA(set,&iface,detail,sizeof(buffer),&needed,&dev) && dev.DevInst==instance;
    if(!ok){SetupDiDestroyDeviceInfoList(set);return FALSE;}
    file=CreateFileA(detail->DevicePath,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    SetupDiDestroyDeviceInfoList(set);
    if(file==INVALID_HANDLE_VALUE){number("cancel_open_error=",GetLastError());return FALSE;}
    clear_bytes(before,sizeof(before));clear_bytes(after,sizeof(after));
    ok=DeviceIoControl(file,CTL_CODE(FILE_DEVICE_UNKNOWN,0x808,METHOD_BUFFERED,FILE_READ_ACCESS),NULL,0,before,sizeof(before),&bytes,NULL);
    if(!ok || bytes!=sizeof(before)){CloseHandle(file);return FALSE;}
    clear_bytes(name,sizeof(name));
    text("CANCEL_REMOVE_HOLDING_EXACT_INTERFACE_HANDLE\r\n");
    /* Report this intentional veto programmatically; leave unrelated setup UI alone. */
    cr=CM_Query_And_Remove_SubTreeW(instance,&veto,name,MAX_PATH,CM_REMOVE_UI_NOT_OK);
    number("cancel_remove_result=",cr);number("cancel_remove_veto=",veto);
    name[MAX_PATH-1]=0;clear_bytes(utf8,sizeof(utf8));
    if(!WideCharToMultiByte(CP_UTF8,0,name,-1,utf8,sizeof(utf8),NULL,NULL))number("cancel_name_conversion_error=",GetLastError());
    text("cancel_remove_veto_name=");text(utf8);text("\r\n");
    bytes=0;ok=DeviceIoControl(file,CTL_CODE(FILE_DEVICE_UNKNOWN,0x808,METHOD_BUFFERED,FILE_READ_ACCESS),NULL,0,after,sizeof(after),&bytes,NULL);
    number("cancel_existing_handle_ok=",ok);number("cancel_existing_handle_error=",ok?0:GetLastError());
    if(ok){number("cancel_starts_before=",before[5]);number("cancel_starts_after=",after[5]);number("cancel_queries_before=",before[7]);number("cancel_queries_after=",after[7]);}
    CloseHandle(file);text("CANCEL_REMOVE_HANDLE_CLOSED\r\n");
    if(cr!=CR_REMOVE_VETOED || veto!=PNP_VetoOutstandingOpen || !ok || bytes!=sizeof(after) ||
       after[3]!=1 || after[4]!=1 || after[5]!=before[5] || after[6]!=before[6] || after[7]!=before[7]+1 || after[9]!=0)return FALSE;
    if(!query())return FALSE;
    text("CANCEL_REMOVE_RECOVERED\r\n");return TRUE;
}
