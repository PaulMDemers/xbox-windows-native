/* NT5 writable-map append/unmap/truncate regression. No filesystem driver edits. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static const DWORD Prefixes[]={401,511,512,513,3985,4095,4096,4097,65425,65535,65536,65537,270225};
static const DWORD Chunks[]={220,53,27,49,75,23,45,86,220,185,74,103,141,42,22,51,115,104};
static const char Warning[]="An unsigned or incorrectly signed driver (c:\\xwninf99\\xwnvideo.inf) was installed for Xbox NV2A firmware framebuffer (experimental). Error 0xe000022f: The third-party INF does not contain digital signature information.\r\n";
typedef char WarningMustBe220[(sizeof(Warning)-1==220)?1:-1];
static HANDLE Log;
static BYTE Buffer[997];
static DWORD Mode,Completed;
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static void record(const char *label,DWORD a,DWORD b,DWORD c) {
    char line[220];DWORD n,w;
    n=(DWORD)wsprintfA(line,"%s %lu %lu %lu\r\n",label,a,b,c);
    if(!WriteFile(Log,line,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(91);
    WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),line,n,&w,NULL);
}
static void fatal(const char *label) {record(label,GetLastError(),Mode,Completed);ExitProcess(92);}
static BYTE pattern(DWORD offset,DWORD index,DWORD round) {return (BYTE)(offset*13+index*17+round*29);}
static BYTE expected(DWORD offset,DWORD index,DWORD round) {
    DWORD start=Prefixes[index];
    if(offset>=start&&offset<start+220)return (BYTE)Warning[offset-start];
    return pattern(offset,index,round);
}
static void initial(const char *path,DWORD index,DWORD round) {
    DWORD offset=0,n,i,w;
    HANDLE file=CreateFileA(path,GENERIC_WRITE,0,NULL,CREATE_ALWAYS,0,NULL);
    if(file==INVALID_HANDLE_VALUE)fatal("FAIL_CREATE");
    while(offset<Prefixes[index]) {
        n=Prefixes[index]-offset;if(n>sizeof(Buffer))n=sizeof(Buffer);
        for(i=0;i<n;i++)Buffer[i]=pattern(offset+i,index,round);
        if(!WriteFile(file,Buffer,n,&w,NULL)||w!=n)fatal("FAIL_PREFIX_WRITE");
        offset+=n;
    }
    if(!FlushFileBuffers(file)||!CloseHandle(file))fatal("FAIL_PREFIX_FLUSH");
}
static void append(const char *path,DWORD index,DWORD round,DWORD old,DWORD amount) {
    HANDLE file,mapping;BYTE *view;DWORD i,end=old+amount;
    file=CreateFileA(path,GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ,NULL,OPEN_ALWAYS,0,NULL);
    if(file==INVALID_HANDLE_VALUE)fatal("FAIL_APPEND_OPEN");
    if(GetFileSize(file,NULL)!=old){SetLastError(ERROR_INVALID_DATA);fatal("FAIL_OLD_SIZE");}
    /* Actual observed SetupAPI adds a27-byte header allowance plus8 extra bytes. */
    mapping=CreateFileMappingA(file,NULL,PAGE_READWRITE,0,end+35,NULL);
    if(!mapping)fatal("FAIL_MAPPING");
    view=(BYTE*)MapViewOfFile(mapping,FILE_MAP_ALL_ACCESS,0,0,0);
    if(!view)fatal("FAIL_VIEW");
    for(i=0;i<amount;i++)view[old+i]=expected(old+i,index,round);
    if(SetFilePointer(file,(LONG)end,NULL,FILE_BEGIN)!=end)fatal("FAIL_SEEK");
    if(Mode&&(!FlushViewOfFile(view+old,amount)||!FlushFileBuffers(file)))fatal("FAIL_EXPLICIT_FLUSH");
    if(!UnmapViewOfFile(view)||!CloseHandle(mapping))fatal("FAIL_UNMAP");
    if(!SetEndOfFile(file))fatal("FAIL_TRUNCATE");
    if(Mode&&!FlushFileBuffers(file))fatal("FAIL_FINAL_FLUSH");
    if(!CloseHandle(file))fatal("FAIL_CLOSE");
    Completed++;
}
static void check(const char *path,DWORD index,DWORD round,DWORD size) {
    DWORD offset=0,n,i,got;HANDLE file=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);
    if(file==INVALID_HANDLE_VALUE)fatal("FAIL_VERIFY_OPEN");
    if(GetFileSize(file,NULL)!=size){SetLastError(ERROR_INVALID_DATA);fatal("FAIL_FINAL_SIZE");}
    while(offset<size) {
        n=size-offset;if(n>sizeof(Buffer))n=sizeof(Buffer);
        if(!ReadFile(file,Buffer,n,&got,NULL)||got!=n)fatal("FAIL_VERIFY_READ");
        for(i=0;i<n;i++)if(Buffer[i]!=expected(offset+i,index,round)){
            record("MISMATCH",index,offset+i,Buffer[i]);SetLastError(ERROR_INVALID_DATA);fatal("FAIL_BYTES");
        }
        offset+=n;
    }
    if(!ReadFile(file,Buffer,1,&got,NULL)||got)fatal("FAIL_EOF");
    if(!CloseHandle(file))fatal("FAIL_VERIFY_CLOSE");
}
void WINAPI mainCRTStartup(void) {
    DWORD index,round,j,old,n,wait;char path[MAX_PATH],mode;HANDLE input,token;TOKEN_PRIVILEGES tp;HMODULE setup;WAIT_INSTALL idle;
    Log=CreateFileA("C:\\xwnmap01\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
    input=CreateFileA("C:\\xwnmap01\\mode.txt",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);
    if(input==INVALID_HANDLE_VALUE||!ReadFile(input,&mode,1,&n,NULL)||n!=1||(mode!='0'&&mode!='1'))fatal("FAIL_MODE");
    CloseHandle(input);Mode=(DWORD)(mode-'0');record("ATTEMPT_ONCE",Mode,13,4);
    setup=LoadLibraryA("setupapi.dll");if(!setup)fatal("FAIL_SETUPAPI");
    idle=(WAIT_INSTALL)GetProcAddress(setup,"CMP_WaitNoPendingInstallEvents");if(!idle)fatal("FAIL_INSTALL_EXPORT");
    wait=idle(120000);record("INSTALL_IDLE_START",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(93);
    for(round=0;round<4;round++)for(index=0;index<13;index++) {
        wsprintfA(path,"C:\\xwnmap01\\case%02lu.bin",index);initial(path,index,round);old=Prefixes[index];
        for(j=0;j<18;j++){append(path,index,round,old,Chunks[j]);old+=Chunks[j];}
        check(path,index,round,old);record("CASE_COMPLETE",round,index,old);
    }
    record("COMPLETE",Mode,Completed,52);
    Sleep(60000);wait=idle(120000);record("INSTALL_IDLE_END",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(94);
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))fatal("FAIL_TOKEN");
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))fatal("FAIL_LOOKUP");
    SetLastError(ERROR_SUCCESS);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)fatal("FAIL_PRIVILEGE");
    CloseHandle(token);record("NORMAL_RESTART_REQUEST",0,0,0);
    if(!ExitWindowsEx(EWX_REBOOT,0))fatal("FAIL_RESTART");
    CloseHandle(Log);ExitProcess(0);
}
