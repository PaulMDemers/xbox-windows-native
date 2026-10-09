/* NT5 read-only installer/window/device/volume observer. No UI activation or restart. */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>
#include <setupapi.h>
#include <cfgmgr32.h>

typedef LONG (WINAPI *QueryProcess)(HANDLE,ULONG,PVOID,ULONG,PULONG);
typedef DWORD (WINAPI *WaitInstall)(DWORD);
static QueryProcess Query;
static WaitInstall Wait;
static HANDLE Log;
static DWORD Written,Started,SampleStart,WindowCount,InstallerCount,Installers[32];
static const char Hex[]="0123456789abcdef";
static void write(const char *s) {
    DWORD n=(DWORD)lstrlenA(s),w=0;
    if(n>4UL*1024*1024-Written||!WriteFile(Log,s,n,&w,NULL)||n!=w)ExitProcess(91);
    Written+=n;
}
static void record(const char *label,DWORD a,DWORD b,DWORD c) {
    char s[256];wsprintfA(s,"%s %lu %lu %lu\r\n",label,a,b,c);write(s);
}
static void blob(const char *label,DWORD owner,DWORD typ,const void *data,DWORD length) {
    const BYTE *bytes=(const BYTE *)data;char s[192],pair[3];DWORD i;
    wsprintfA(s,"%s %lu %lu %lu ",label,owner,typ,length);write(s);
    pair[2]=0;
    for(i=0;i<length;i++){pair[0]=Hex[bytes[i]>>4];pair[1]=Hex[bytes[i]&15];write(pair);}
    write("\r\n");
}
static BOOL readremote(HANDLE p,DWORD at,void *data,DWORD size) {
    SIZE_T n=0;
    if(at<0x10000||at>=0x7fff0000||size>0x7fff0000-at)return FALSE;
    return ReadProcessMemory(p,(void *)at,data,size,&n)&&n==size;
}
static void command(DWORD pid) {
    HANDLE p=OpenProcess(PROCESS_QUERY_INFORMATION|PROCESS_VM_READ,FALSE,pid);
    DWORD info[6],params=0;struct {WORD length,max;DWORD buffer;} text;WCHAR wide[1024];LONG status;
    if(!p){record("PROCESS_UNREADABLE",pid,GetLastError(),0);return;}
    status=Query(p,0,info,sizeof(info),NULL);
    if(status<0||!readremote(p,info[1]+0x10,&params,4)||!readremote(p,params+0x40,&text,sizeof(text))||
       text.length>text.max||(text.length&1)||text.length>sizeof(wide)||!readremote(p,text.buffer,wide,text.length))
        record("COMMAND_UNREADABLE",pid,(DWORD)status,GetLastError());
    else blob("COMMAND_UTF16",pid,0,wide,text.length);
    CloseHandle(p);
}
static BOOL budget(void){return WindowCount<256&&GetTickCount()-SampleStart<10000;}
static void describe(HWND h,const char *label) {
    char text[512],cls[80],s[320];DWORD pid=0,error;DWORD_PTR result=0;LRESULT ok;
    text[0]=cls[0]=0;GetWindowThreadProcessId(h,&pid);GetClassNameA(h,cls,sizeof(cls));SetLastError(0);
    ok=SendMessageTimeoutA(h,WM_GETTEXT,sizeof(text),(LPARAM)text,SMTO_ABORTIFHUNG|SMTO_BLOCK,100,&result);
    error=GetLastError();text[511]=cls[79]=0;
    wsprintfA(s,"%s %lu %lu %lu %ld %u %u %u %lu\r\n",label,pid,(DWORD)h,(DWORD)GetParent(h),
        (LONG)GetDlgCtrlID(h),IsWindowVisible(h),IsWindowEnabled(h),ok!=0,error);write(s);
    blob("WINDOW_CLASS",(DWORD)h,0,cls,(DWORD)lstrlenA(cls));blob("WINDOW_TEXT",(DWORD)h,0,text,(DWORD)lstrlenA(text));WindowCount++;
}
static BOOL CALLBACK child(HWND h,LPARAM unused){(void)unused;if(!budget())return FALSE;describe(h,"CHILD");return TRUE;}
static BOOL CALLBACK top(HWND h,LPARAM unused) {
    DWORD pid=0,i;(void)unused;if(!budget())return FALSE;GetWindowThreadProcessId(h,&pid);
    for(i=0;i<InstallerCount;i++)if(pid==Installers[i]){describe(h,"TOP");EnumChildWindows(h,child,0);break;}
    return TRUE;
}
static void processes(void) {
    HANDLE snap=CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS,0);PROCESSENTRY32 e;DWORD count=0;
    InstallerCount=WindowCount=0;
    if(snap==INVALID_HANDLE_VALUE){record("SNAPSHOT_FAILED",GetLastError(),0,0);return;}
    e.dwSize=sizeof(e);
    if(Process32First(snap,&e))do {
        if(++count>1024){record("PROCESS_BUDGET_EXHAUSTED",count,0,0);break;}
        if(!lstrcmpiA(e.szExeFile,"rundll32.exe")||!lstrcmpiA(e.szExeFile,"services.exe")||
           !lstrcmpiA(e.szExeFile,"explorer.exe")||!lstrcmpiA(e.szExeFile,"cmd.exe")){
            record("PROCESS",e.th32ProcessID,e.th32ParentProcessID,0);
            blob("PROCESS_IMAGE",e.th32ProcessID,0,e.szExeFile,(DWORD)lstrlenA(e.szExeFile));command(e.th32ProcessID);
            if(!lstrcmpiA(e.szExeFile,"rundll32.exe")){
                if(InstallerCount<32)Installers[InstallerCount++]=e.th32ProcessID;
                else record("INSTALLER_BUDGET_EXHAUSTED",e.th32ProcessID,0,0);
            }
        }
    }while(Process32Next(snap,&e));
    CloseHandle(snap);SampleStart=GetTickCount();EnumWindows(top,0);
    record("WINDOW_SAMPLE_END",WindowCount,GetTickCount()-SampleStart,!budget());
}
static void devices(void) {
    static const DWORD props[]={SPDRP_DEVICEDESC,SPDRP_HARDWAREID,SPDRP_CLASSGUID,SPDRP_SERVICE,SPDRP_DRIVER,SPDRP_CONFIGFLAGS};
    HDEVINFO set=SetupDiGetClassDevsA(NULL,NULL,NULL,DIGCF_PRESENT|DIGCF_ALLCLASSES);
    SP_DEVINFO_DATA info;DWORD i,j,type,required,status=0,problem=0;CONFIGRET result;char id[512];BYTE data[4096];
    if(set==INVALID_HANDLE_VALUE){record("DEVICE_SET_FAILED",GetLastError(),0,0);return;}
    for(i=0;i<256;i++){
        info.cbSize=sizeof(info);
        if(!SetupDiEnumDeviceInfo(set,i,&info)){
            DWORD error=GetLastError();record("DEVICE_ENUM_END",i,error,0);break;
        }
        result=CM_Get_Device_IDA(info.DevInst,id,sizeof(id),0);id[511]=0;
        if(result==CR_SUCCESS)blob("DEVICE_ID",i,info.DevInst,id,(DWORD)lstrlenA(id));
        else record("DEVICE_ID_FAILED",i,result,0);
        status=problem=0;result=CM_Get_DevNode_Status(&status,&problem,info.DevInst,0);
        record("DEVICE_STATUS",i,status,problem);record("DEVICE_STATUS_RESULT",i,result,info.DevInst);
        for(j=0;j<sizeof(props)/sizeof(props[0]);j++){
            type=required=0;
            if(SetupDiGetDeviceRegistryPropertyA(set,&info,props[j],&type,data,sizeof(data),&required)){
                if(required<=sizeof(data)){
                    record("DEVICE_PROPERTY",i,props[j],type);blob("PROPERTY_BYTES",i,props[j],data,required);
                }else record("PROPERTY_OVERSIZE",i,props[j],required);
            }else record("PROPERTY_UNAVAILABLE",i,props[j],GetLastError());
        }
    }
    if(i==256)record("DEVICE_BUDGET_EXHAUSTED",i,0,0);
    SetupDiDestroyDeviceInfoList(set);
}
static void disks(void) {
    DWORD mask=GetLogicalDrives(),i,spc,bps,freec,totalc;ULARGE_INTEGER avail,total,freeb;
    char root[]="C:\\",device[]="C:",target[1024],s[400];
    for(i=2;i<26;i++)if(mask&(1UL<<i)){
        root[0]=device[0]=(char)('A'+i);record("DRIVE",i,GetDriveTypeA(root),0);
        if(QueryDosDeviceA(device,target,sizeof(target)))blob("DRIVE_TARGET",i,0,target,(DWORD)lstrlenA(target));
        else record("TARGET_FAILED",i,GetLastError(),0);
        if(GetDiskFreeSpaceExA(root,&avail,&total,&freeb)){
            wsprintfA(s,"BYTES %lu %08lx%08lx %08lx%08lx %08lx%08lx\r\n",i,avail.HighPart,avail.LowPart,
                total.HighPart,total.LowPart,freeb.HighPart,freeb.LowPart);write(s);
        }else record("SPACE_EX_FAILED",i,GetLastError(),0);
        if(GetDiskFreeSpaceA(root,&spc,&bps,&freec,&totalc)){
            wsprintfA(s,"CLUSTERS %lu %lu %lu %lu %lu\r\n",i,spc,bps,freec,totalc);write(s);
        }else record("SPACE_FAILED",i,GetLastError(),0);
    }
}
void WINAPI mainCRTStartup(void) {
    char base[MAX_PATH],path[MAX_PATH];DWORD n,i,elapsed;
    n=GetModuleFileNameA(NULL,base,sizeof(base));if(!n||n>=sizeof(base)-32)ExitProcess(90);
    while(n&&base[n-1]!='\\')n--;if(!n)ExitProcess(90);base[n]=0;
    wsprintfA(path,"%sobserver.log",base);
    Log=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
    Query=(QueryProcess)GetProcAddress(GetModuleHandleA("ntdll.dll"),"NtQueryInformationProcess");
    Wait=(WaitInstall)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");
    if(!Query||!Wait){record("FAIL_DYNAMIC_EXPORT",GetLastError(),Query!=NULL,Wait!=NULL);ExitProcess(92);}
    Started=GetTickCount();record("XWN_DEVICE_OBSERVER",188,5,30000);
    for(i=0;i<5;i++){
        elapsed=GetTickCount()-Started;if(elapsed<i*30000)Sleep(i*30000-elapsed);
        record("SAMPLE",i,GetTickCount()-Started,GetCurrentProcessId());
        record("INSTALL_STATE_BEGIN",i,Wait(0),0);processes();devices();disks();
        record("INSTALL_STATE_END",i,Wait(0),0);record("SAMPLE_COMPLETE",i,GetTickCount()-Started,0);
        if(!FlushFileBuffers(Log))ExitProcess(93);
    }
    record("COMPLETE",5,GetTickCount()-Started,0);write("NO_RESTART_OR_DEVICE_ACTION 0 0 0\r\n");
    if(!FlushFileBuffers(Log))ExitProcess(93);CloseHandle(Log);ExitProcess(0);
}
