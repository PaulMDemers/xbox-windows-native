"""Read-only started-device/module proof and joined post-install playback runner."""
import pathlib
k=pathlib.Path(__file__).resolve().parent
def write(name,s):
    p=k/name;assert not p.exists();p.write_text(s)
prefix=(k/'install.c').read_text().split('void WINAPI mainCRTStartup(void)')[0]
main=r'''
typedef BOOL (WINAPI *ENUM_DRIVERS)(LPVOID*,DWORD,LPDWORD);
typedef DWORD (WINAPI *DRIVER_NAME)(LPVOID,LPSTR,DWORD);
void WINAPI mainCRTStartup(void) {
    char base[MAX_PATH],path[MAX_PATH],system[MAX_PATH],service[128],name[MAX_PATH];
    DWORD n,type,required,bytes,index,current=0,legacy=0;ULONG flags=0,problem=0;CONFIGRET cr;
    HDEVINFO set;SP_DEVINFO_DATA device;DEV_STATUS status;HMODULE module;ENUM_DRIVERS enumerate;DRIVER_NAME driverName;
    static LPVOID drivers[512];
    n=GetModuleFileNameA(NULL,base,sizeof(base));if(!n||n>=sizeof(base)-48)ExitProcess(90);
    while(n&&base[n-1]!='\')n--;if(!n)ExitProcess(90);base[n-1]=0;
    wsprintfA(path,"%s\state207.log",base);
    Log=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
    line("STATE207_BEGIN",HardwareId);
    n=GetSystemDirectoryA(system,sizeof(system));if(!n||n>=sizeof(system)-24)fail("FAIL_SYSTEM_PATH",n);
    wsprintfA(path,"%s\cfgmgr32.dll",system);module=LoadLibraryA(path);if(!module)fail("FAIL_CFGMGR_LOAD",GetLastError());
    status=(DEV_STATUS)GetProcAddress(module,"CM_Get_DevNode_Status");
    wsprintfA(path,"%s\psapi.dll",system);module=LoadLibraryA(path);if(!module)fail("FAIL_PSAPI_LOAD",GetLastError());
    enumerate=(ENUM_DRIVERS)GetProcAddress(module,"EnumDeviceDrivers");driverName=(DRIVER_NAME)GetProcAddress(module,"GetDeviceDriverBaseNameA");
    if(!status||!enumerate||!driverName)fail("FAIL_REQUIRED_EXPORT",GetLastError());
    set=target(&device);
    if(!SetupDiGetDeviceRegistryPropertyA(set,&device,SPDRP_SERVICE,&type,(PBYTE)service,sizeof(service),&required))fail("FAIL_SERVICE_QUERY",GetLastError());
    if(type!=REG_SZ||!required||required>sizeof(service)||service[required-1])fail("FAIL_SERVICE_STRING",required);
    line("ACTUAL_SERVICE",service);if(lstrcmpiA(service,"xwnaci207"))fail("FAIL_WRONG_SERVICE",0);
    cr=status(&flags,&problem,device.DevInst,0);number("DEVNODE_STATUS_RESULT",cr);number("DEVNODE_FLAGS",flags);number("DEVNODE_PROBLEM",problem);
    if(cr!=CR_SUCCESS||!(flags&DN_STARTED)||(flags&DN_HAS_PROBLEM))fail("FAIL_NOT_STARTED",problem);
    SetupDiDestroyDeviceInfoList(set);
    if(!enumerate(drivers,sizeof(drivers),&bytes))fail("FAIL_ENUM_DRIVERS",GetLastError());
    if(bytes>sizeof(drivers)||bytes%sizeof(drivers[0]))fail("FAIL_MODULE_ARRAY",bytes);
    number("MODULE_COUNT",bytes/sizeof(drivers[0]));
    for(index=0;index<bytes/sizeof(drivers[0]);index++) {
        n=driverName(drivers[index],name,sizeof(name));if(!n||n>=sizeof(name))fail("FAIL_DRIVER_NAME",GetLastError());
        if(!lstrcmpiA(name,"xwnaci207.sys")){current++;line("TARGET_MODULE",name);}
        if(!lstrcmpiA(name,"ac97xnt5.sys")){legacy++;line("LEGACY_MODULE",name);}
    }
    number("TARGET_MODULE_COUNT",current);number("LEGACY_MODULE_COUNT",legacy);
    if(current!=1||legacy)fail("FAIL_MODULE_IDENTITY",current);
    number("STATE207_END",0);CloseHandle(Log);ExitProcess(0);
}
'''
write('state.c',prefix+main.replace(chr(92),chr(92)*2))
s=(k/'probe.c').read_text().replace('if(!waveOutGetNumDevs())','if(waveOutGetNumDevs()!=1)').replace('FAIL_NO_DEVICE','FAIL_DEVICE_COUNT')
write('probe-installed.c',s)
s=(k/'runner.c').read_text();anchor='    wsprintfA(path,"%s\\\\probe.exe",base);si.cb=sizeof(si);'
assert s.count(anchor)==1
block=r'''    wsprintfA(path,"%s\state.exe",base);si.cb=sizeof(si);
    if(!CreateProcessA(path,NULL,NULL,NULL,FALSE,0,NULL,base,&si,&pi)){record(NULL,"FAIL_CREATE_STATE",GetLastError());ExitProcess(107);}
    CloseHandle(pi.hThread);record(NULL,"STATE_STARTED",pi.dwProcessId);
    status=WaitForSingleObject(pi.hProcess,30000);record(NULL,"STATE_JOIN_RESULT",status);
    if(status!=WAIT_OBJECT_0)ExitProcess(108);
    if(!GetExitCodeProcess(pi.hProcess,&status))ExitProcess(109);
    CloseHandle(pi.hProcess);record(NULL,"STATE_EXIT",status);if(status)ExitProcess(110);
'''
write('installed-runner.c',s.replace(anchor,block.replace(chr(92),chr(92)*2)+anchor))
