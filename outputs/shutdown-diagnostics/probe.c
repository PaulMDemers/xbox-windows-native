#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <tlhelp32.h>

static HANDLE Log;
static DWORD Started;
typedef LONG (WINAPI *QueryProcess)(HANDLE,ULONG,PVOID,ULONG,PULONG);
static QueryProcess Query;
static void line(const char *s) {
    DWORD size=lstrlenA(s),n;
    if(!WriteFile(Log,s,size,&n,NULL)||n!=size)ExitProcess(10);
}
static void record(const char *tag,DWORD a,DWORD b,DWORD c) {
    char s[256];wsprintfA(s,"%s %lu %08lx %08lx\r\n",tag,a,b,c);line(s);
}
static BOOL readremote(HANDLE p,DWORD at,void *data,DWORD size) {
    SIZE_T n=0;
    if(at<0x10000||at>=0x7fff0000||size>0x7fff0000-at)return FALSE;
    return ReadProcessMemory(p,(void *)at,data,size,&n)&&n==size;
}
static void command(DWORD pid) {
    HANDLE p=OpenProcess(PROCESS_QUERY_INFORMATION|PROCESS_VM_READ,FALSE,pid);
    DWORD info[6],params=0;struct {WORD length,max;DWORD buffer;} text;
    WCHAR wide[512];char narrow[1024];LONG status;
    if(!p){record("PROCESS_UNREADABLE",pid,GetLastError(),0);return;}
    status=Query(p,0,info,sizeof(info),NULL);
    if(status<0||!readremote(p,info[1]+0x10,&params,4)||
       !readremote(p,params+0x40,&text,sizeof(text))||text.length>text.max||
       (text.length&1)||text.length>1022||!readremote(p,text.buffer,wide,text.length)){
        record("COMMAND_UNREADABLE",pid,(DWORD)status,GetLastError());CloseHandle(p);return;
    }
    wide[text.length/2]=0;
    if(!WideCharToMultiByte(CP_ACP,0,wide,-1,narrow,sizeof(narrow),NULL,NULL)){
        record("COMMAND_ENCODING",pid,GetLastError(),0);
    }else{record("COMMAND_PID",pid,0,0);line(narrow);line("\r\n");}
    CloseHandle(p);
}
static BOOL CALLBACK window(HWND h,LPARAM unused) {
    char title[192],cls[80],s[384];DWORD pid=0;(void)unused;
    if(!IsWindowVisible(h))return TRUE;
    GetWindowThreadProcessId(h,&pid);GetWindowTextA(h,title,sizeof(title));
    GetClassNameA(h,cls,sizeof(cls));title[191]=0;cls[79]=0;
    wsprintfA(s,"WINDOW %lu %08lx %s | %s\r\n",pid,(DWORD)h,cls,title);line(s);
    return TRUE;
}
static void processes(void) {
    PROCESSENTRY32 e;HANDLE s=CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS,0);
    if(s==INVALID_HANDLE_VALUE){record("SNAPSHOT_FAILED",GetLastError(),0,0);return;}
    e.dwSize=sizeof(e);
    if(Process32First(s,&e))do {
        if(!lstrcmpiA(e.szExeFile,"rundll32.exe")||!lstrcmpiA(e.szExeFile,"cmd.exe")||!lstrcmpiA(e.szExeFile,"explorer.exe")){
            char text[320];wsprintfA(text,"PROCESS %lu %lu %s\r\n",e.th32ProcessID,e.th32ParentProcessID,e.szExeFile);line(text);command(e.th32ProcessID);
        }
    }while(Process32Next(s,&e));
    CloseHandle(s);EnumWindows(window,0);
}
static void disks(void) {
    DWORD mask=GetLogicalDrives(),i,spc,bps,freec,totalc;ULARGE_INTEGER avail,total,freeb;
    char root[]="C:\\",device[]="C:",target[1024],s[400];
    for(i=2;i<26;i++)if(mask&(1UL<<i)){
        root[0]=device[0]=(char)('A'+i);
        wsprintfA(s,"DRIVE %s TYPE %lu\r\n",root,GetDriveTypeA(root));line(s);
        if(QueryDosDeviceA(device,target,sizeof(target))){line("TARGET ");line(device);line(" ");line(target);line("\r\n");}
        else record("TARGET_FAILED",i,GetLastError(),0);
        if(GetDiskFreeSpaceExA(root,&avail,&total,&freeb)){
            wsprintfA(s,"BYTES %s AVAILABLE %08lx%08lx TOTAL %08lx%08lx FREE %08lx%08lx\r\n",root,avail.HighPart,avail.LowPart,total.HighPart,total.LowPart,freeb.HighPart,freeb.LowPart);line(s);
        }else record("SPACE_EX_FAILED",i,GetLastError(),0);
        if(GetDiskFreeSpaceA(root,&spc,&bps,&freec,&totalc)){
            wsprintfA(s,"CLUSTERS %s SPC %lu BPS %lu FREE %lu TOTAL %lu\r\n",root,spc,bps,freec,totalc);line(s);
        }else record("SPACE_FAILED",i,GetLastError(),0);
    }
}
void WINAPI mainCRTStartup(void) {
    DWORD round;HANDLE token;TOKEN_PRIVILEGES tp;
    Log=CreateFileA("C:\\xwnsd01\\probe.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(1);
    Query=(QueryProcess)GetProcAddress(GetModuleHandleA("ntdll.dll"),"NtQueryInformationProcess");
    if(!Query){record("NO_QUERY",GetLastError(),0,0);ExitProcess(2);}
    Started=GetTickCount();line("SHUTDOWN_DIAGNOSTIC_V1\r\n");
    for(round=0;round<5;round++){
        record("SAMPLE",round,GetTickCount()-Started,0);disks();processes();
        if(!FlushFileBuffers(Log))ExitProcess(11);
        if(round<4)Sleep(30000);
    }
    record("COMPLETE",5,GetTickCount()-Started,0);
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(3);
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(4);
    SetLastError(0);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError())ExitProcess(5);
    CloseHandle(token);line("NORMAL_RESTART_REQUEST\r\n");if(!FlushFileBuffers(Log))ExitProcess(12);
    if(!ExitWindowsEx(EWX_REBOOT,0)){record("RESTART_FAILED",GetLastError(),0,0);ExitProcess(6);}
    CloseHandle(Log);ExitProcess(0);
}
