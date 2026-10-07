/* NT5 mapped growth/shrink/regrowth: ordinary serial or concurrent volume flush. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static const DWORD Prefixes[]={0,3985,65290,65300,65315,65316,130826,130836,130851,130852,270225};
static const DWORD Chunks[]={220,53,27,49,75,23,45,86,220,185,74,103,141,42,22,51,115,104};
static const char Warning[]="An unsigned or incorrectly signed driver (c:\\xwninf99\\xwnvideo.inf) was installed for Xbox NV2A firmware framebuffer (experimental). Error 0xe000022f: The third-party INF does not contain digital signature information.\r\n";
typedef char WarningMustBe220[(sizeof(Warning)-1==220)?1:-1];
typedef struct {LONG status;DWORD information;} NT5_IO_STATUS;
typedef struct {LARGE_INTEGER allocation,end;DWORD links;BYTE pending,directory;} NT5_STANDARD;
typedef char StandardMustBe24[(sizeof(NT5_STANDARD)==24)?1:-1];
typedef LONG (WINAPI *QUERY_FILE)(HANDLE,NT5_IO_STATUS*,void*,DWORD,DWORD);
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static HANDLE Log,Ready,DirtyReady,Worker;
static QUERY_FILE Query;
static BYTE Buffer[997];
static DWORD Mode,Completed,Shrinks,Checks,Rendezvous;
static volatile LONG Stop,ActiveEpoch,DirtyEpoch,FlushCount,FlushError,Overlaps[44],DirtyOverlaps[44],Aborting;
static void abortTrial(DWORD code) {
    DWORD wait=WAIT_OBJECT_0,n,w;char line[160];
    /* Failure remains failure. Do not kill a live flusher without a bounded join. */
    if(!InterlockedCompareExchange(&Aborting,1,0)) {
        InterlockedExchange(&DirtyEpoch,0);InterlockedExchange(&ActiveEpoch,0);InterlockedExchange(&Stop,1);
        if(Worker)wait=WaitForSingleObject(Worker,60000);
        n=(DWORD)wsprintfA(line,"ABORT_JOIN %lu %lu %lu\r\n",wait,(DWORD)FlushCount,(DWORD)FlushError);
        if(Log&&Log!=INVALID_HANDLE_VALUE){WriteFile(Log,line,n,&w,NULL);FlushFileBuffers(Log);}
        if(Worker&&wait==WAIT_OBJECT_0){CloseHandle(Worker);Worker=NULL;}
    }
    ExitProcess(code);
}
static void record(const char *label,DWORD a,DWORD b,DWORD c) {
    char line[220];DWORD n,w;
    n=(DWORD)wsprintfA(line,"%s %lu %lu %lu\r\n",label,a,b,c);
    if(!WriteFile(Log,line,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))abortTrial(91);
    WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),line,n,&w,NULL);
}
static void fatal(const char *label) {record(label,GetLastError(),Mode,Completed);abortTrial(92);}
static void checkService(const char *label) {
    SC_HANDLE manager,service;SERVICE_STATUS status;DWORD waited=0;
    manager=OpenSCManagerA(NULL,NULL,SC_MANAGER_CONNECT);if(!manager)fatal("FAIL_SCM_OPEN");
    service=OpenServiceA(manager,"HidServ",SERVICE_QUERY_STATUS);if(!service)fatal("FAIL_SERVICE_OPEN");
    for(;;){
        if(!QueryServiceStatus(service,&status))fatal("FAIL_SERVICE_QUERY");
        if(status.dwCurrentState!=SERVICE_START_PENDING||waited>=10000)break;
        Sleep(100);waited+=100;
    }
    record(label,status.dwCurrentState,status.dwWin32ExitCode,status.dwServiceSpecificExitCode);
    if(!CloseServiceHandle(service)||!CloseServiceHandle(manager))fatal("FAIL_SERVICE_CLOSE");
    if(status.dwCurrentState!=SERVICE_RUNNING||status.dwWin32ExitCode||status.dwServiceSpecificExitCode)abortTrial(95);
}
static DWORD rounded(DWORD size) {return (size+65535)&~65535UL;}
static void query(HANDLE file,DWORD end,NT5_STANDARD *s) {
    NT5_IO_STATUS ios;LONG status;ios.status=0;ios.information=0;
    status=Query(file,&ios,s,sizeof(*s),5); /* FileStandardInformation */
    if(status<0||ios.information!=sizeof(*s)) {record("FAIL_QUERY_STATUS",status,ios.status,ios.information);abortTrial(92);}
    if(s->end.HighPart||s->allocation.HighPart||s->end.LowPart!=end||s->allocation.LowPart!=rounded(end)) {
        record("FAIL_QUERY_SIZE",end,s->end.LowPart,s->allocation.LowPart);abortTrial(92);
    }
}
static BYTE expected(DWORD offset,DWORD index,DWORD round) {
    DWORD start=Prefixes[index];
    if(offset>=start&&offset<start+220)return (BYTE)Warning[offset-start];
    return (BYTE)(offset*13+index*17+round*29);
}
static DWORD WINAPI flusher(LPVOID ignored) {
    HANDLE volume;LONG before,after,dirtyBefore,dirtyAfter;DWORD index;(void)ignored;
    volume=CreateFileA("\\\\.\\C:",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    if(volume==INVALID_HANDLE_VALUE){InterlockedExchange(&FlushError,GetLastError());SetEvent(Ready);return 1;}
    SetEvent(Ready);
    while(!InterlockedCompareExchange(&Stop,0,0)) {
        before=InterlockedCompareExchange(&ActiveEpoch,0,0);
        dirtyBefore=InterlockedCompareExchange(&DirtyEpoch,0,0);
        if(!FlushFileBuffers(volume)){InterlockedExchange(&FlushError,GetLastError());break;}
        after=InterlockedCompareExchange(&ActiveEpoch,0,0);InterlockedIncrement(&FlushCount);
        dirtyAfter=InterlockedCompareExchange(&DirtyEpoch,0,0);
        /* A complete flush lies within one uniquely identified append epoch. */
        if(before==after&&(before&1)){
            index=((DWORD)before/2-1)/18;
            if(index<44)InterlockedIncrement(&Overlaps[index]);
            else {InterlockedExchange(&FlushError,ERROR_INVALID_DATA);break;}
        }
        if(dirtyBefore==dirtyAfter&&(dirtyBefore&1)){
            index=((DWORD)dirtyBefore/2-1)/18;
            if(index<44){InterlockedIncrement(&DirtyOverlaps[index]);SetEvent(DirtyReady);}
            else {InterlockedExchange(&FlushError,ERROR_INVALID_DATA);break;}
        }
        Sleep(1);
    }
    if(!CloseHandle(volume)&&!FlushError)InterlockedExchange(&FlushError,GetLastError());
    return FlushError?1:0;
}
static void initial(const char *path,DWORD index,DWORD round) {
    DWORD offset=0,n,i,w;NT5_STANDARD s;
    HANDLE file=CreateFileA(path,GENERIC_READ|GENERIC_WRITE,0,NULL,CREATE_ALWAYS,0,NULL);
    if(file==INVALID_HANDLE_VALUE)fatal("FAIL_CREATE");
    while(offset<Prefixes[index]) {
        n=Prefixes[index]-offset;if(n>sizeof(Buffer))n=sizeof(Buffer);
        for(i=0;i<n;i++)Buffer[i]=expected(offset+i,index,round);
        if(!WriteFile(file,Buffer,n,&w,NULL)||w!=n)fatal("FAIL_PREFIX_WRITE");
        offset+=n;
    }
    query(file,Prefixes[index],&s);
    if(!FlushFileBuffers(file)||!CloseHandle(file))fatal("FAIL_PREFIX_FLUSH");
}
static void append(const char *path,DWORD index,DWORD round,DWORD old,DWORD amount) {
    HANDLE file,mapping;BYTE *view;DWORD i,end=old+amount,wait;NT5_STANDARD mapped,final;
    InterlockedExchange(&ActiveEpoch,(LONG)((Completed+1)*2+1));
    file=CreateFileA(path,GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ,NULL,OPEN_ALWAYS,0,NULL);
    if(file==INVALID_HANDLE_VALUE)fatal("FAIL_APPEND_OPEN");
    if(GetFileSize(file,NULL)!=old){SetLastError(ERROR_INVALID_DATA);fatal("FAIL_OLD_SIZE");}
    mapping=CreateFileMappingA(file,NULL,PAGE_READWRITE,0,end+35,NULL);
    if(!mapping)fatal("FAIL_MAPPING");
    view=(BYTE*)MapViewOfFile(mapping,FILE_MAP_ALL_ACCESS,0,0,0);if(!view)fatal("FAIL_VIEW");
    query(file,end+35,&mapped);
    for(i=0;i<amount;i++)view[old+i]=expected(old+i,index,round);
    if(Mode&&!ResetEvent(DirtyReady))fatal("FAIL_RESET_DIRTY");
    InterlockedExchange(&DirtyEpoch,(LONG)((Completed+1)*2+1));
    if(old==Prefixes[index]) {
        if(Mode) {
            wait=WaitForSingleObject(DirtyReady,10000);
            if(wait!=WAIT_OBJECT_0){record("FAIL_RENDEZVOUS",round,index,wait);abortTrial(94);}
            Rendezvous++;
        } else Sleep(100); /* Serial control has no worker to rendezvous with. */
    } else Sleep(2); /* Remaining17 appends race freely through unmap and shrink. */
    InterlockedExchange(&DirtyEpoch,0);
    if(SetFilePointer(file,(LONG)end,NULL,FILE_BEGIN)!=end)fatal("FAIL_SEEK");
    if(!UnmapViewOfFile(view)||!CloseHandle(mapping))fatal("FAIL_UNMAP");
    if(!SetEndOfFile(file))fatal("FAIL_TRUNCATE");
    query(file,end,&final);
    if(mapped.allocation.LowPart>final.allocation.LowPart)Shrinks++;
    if(!CloseHandle(file))fatal("FAIL_CLOSE");
    InterlockedExchange(&ActiveEpoch,0);Completed++;
}
static void check(const char *path,DWORD index,DWORD round,DWORD size) {
    DWORD offset=0,n,i,got;NT5_STANDARD s;HANDLE file=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);
    if(file==INVALID_HANDLE_VALUE)fatal("FAIL_VERIFY_OPEN");
    query(file,size,&s);
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
    Checks++;
}
void WINAPI mainCRTStartup(void) {
    DWORD index,round,j,old,n,wait,startShrinks,overlap,dirty,totalOverlap=0,totalDirty=0;char path[MAX_PATH],mode;
    HANDLE input,token;TOKEN_PRIVILEGES tp;HMODULE setup,ntdll;WAIT_INSTALL idle;
    Log=CreateFileA("C:\\xwndu01\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)abortTrial(90);
    input=CreateFileA("C:\\xwndu01\\mode.txt",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);
    if(input==INVALID_HANDLE_VALUE||!ReadFile(input,&mode,1,&n,NULL)||n!=1||(mode!='0'&&mode!='1'))fatal("FAIL_MODE");
    CloseHandle(input);Mode=(DWORD)(mode-'0');record("ATTEMPT_ONCE",Mode,11,4);
    setup=LoadLibraryA("setupapi.dll");ntdll=GetModuleHandleA("ntdll.dll");
    if(!setup||!ntdll)fatal("FAIL_MODULE");
    idle=(WAIT_INSTALL)GetProcAddress(setup,"CMP_WaitNoPendingInstallEvents");Query=(QUERY_FILE)GetProcAddress(ntdll,"NtQueryInformationFile");
    if(!idle||!Query)fatal("FAIL_EXPORT");
    wait=idle(120000);record("INSTALL_IDLE_START",wait,0,0);if(wait!=WAIT_OBJECT_0)abortTrial(93);
    checkService("HIDSERV_START");
    if(Mode){
        Ready=CreateEventA(NULL,TRUE,FALSE,NULL);if(!Ready)fatal("FAIL_READY");
        DirtyReady=CreateEventA(NULL,TRUE,FALSE,NULL);if(!DirtyReady)fatal("FAIL_DIRTY_READY");
        Worker=CreateThread(NULL,0,flusher,NULL,0,NULL);if(!Worker)fatal("FAIL_THREAD");
        wait=WaitForSingleObject(Ready,10000);if(wait!=WAIT_OBJECT_0||FlushError){record("FAIL_WORKER_READY",wait,FlushError,0);abortTrial(94);}
    }
    for(round=0;round<4;round++)for(index=0;index<11;index++) {
        wsprintfA(path,"C:\\xwndu01\\case%02lu.bin",index);initial(path,index,round);old=Prefixes[index];startShrinks=Shrinks;
        for(j=0;j<18;j++){
            append(path,index,round,old,Chunks[j]);old+=Chunks[j];
            if(j==0||j==1||j==17)check(path,index,round,old);
        }
        overlap=(DWORD)InterlockedCompareExchange(&Overlaps[round*11+index],0,0);totalOverlap+=overlap;
        dirty=(DWORD)InterlockedCompareExchange(&DirtyOverlaps[round*11+index],0,0);totalDirty+=dirty;
        record("CASE_COMPLETE",round,index,old);record("CASE_SHRINKS",round,index,Shrinks-startShrinks);record("CASE_OVERLAP",round,index,overlap);
        record("CASE_DIRTY_OVERLAP",round,index,dirty);
        if(FlushError){record("FAIL_WORKER",FlushError,0,0);abortTrial(94);}
        if(Mode&&(!overlap||!dirty)){record("FAIL_NO_OVERLAP",round,index,0);abortTrial(94);}
    }
    InterlockedExchange(&Stop,1);wait=Worker?WaitForSingleObject(Worker,60000):WAIT_OBJECT_0;
    record("FLUSH_JOIN",wait,FlushCount,FlushError);
    if(wait!=WAIT_OBJECT_0||FlushError||(Mode&&!FlushCount))abortTrial(94);
    if(Worker){CloseHandle(Worker);Worker=NULL;CloseHandle(Ready);CloseHandle(DirtyReady);}
    record("DIRTY_COVERAGE",Rendezvous,totalDirty,0);
    record("COVERAGE",Shrinks,Checks,totalOverlap);record("COMPLETE",Mode,Completed,44);
    Sleep(60000);wait=idle(120000);record("INSTALL_IDLE_END",wait,0,0);if(wait!=WAIT_OBJECT_0)abortTrial(94);
    checkService("HIDSERV_END");
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))fatal("FAIL_TOKEN");
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))fatal("FAIL_LOOKUP");
    SetLastError(ERROR_SUCCESS);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)fatal("FAIL_PRIVILEGE");
    CloseHandle(token);record("NORMAL_RESTART_REQUEST",0,0,0);
    if(!ExitWindowsEx(EWX_REBOOT,0))fatal("FAIL_RESTART");
    CloseHandle(Log);ExitProcess(0);
}
