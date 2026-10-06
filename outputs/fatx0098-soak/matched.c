/* Replay the observed Paint BMP file sequence; separate from the 64KiB baseline.
 * Only CREATE_NEW-owned files are reopened with Paint's OPEN_ALWAYS options.
 * Odd cases omit intermediate logging; no raw I/O or automatic reboot here. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static BYTE Data[442422],Check[442422];
static HANDLE Log;
static DWORD Case,Step;
static void number(char *b,DWORD *at,DWORD value) {
    char digits[12];DWORD n=0;
    do {digits[n++]=(char)('0'+value%10);value/=10;}while(value);
    while(n)b[(*at)++]=digits[--n];
}
static void event(const char *stage,DWORD value) {
    char b[160];DWORD at=0,w,n;
    while(*stage)b[at++]=*stage++;
    b[at++]=' ';number(b,&at,Case);b[at++]=' ';number(b,&at,Step);
    b[at++]=' ';number(b,&at,value);b[at++]=' ';number(b,&at,GetTickCount());
    b[at++]='\r';b[at++]='\n';
    if(!WriteFile(Log,b,at,&w,NULL)||w!=at||!FlushFileBuffers(Log))ExitProcess(3);
    WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),b,at,&n,NULL);
}
static void fail(const char *stage) {event(stage,GetLastError());CloseHandle(Log);ExitProcess(1);}
static void detail(const char *stage,DWORD value) {if(!(Case&1))event(stage,value);}
void WINAPI mainCRTStartup(void) {
    HANDLE f;MEMORYSTATUS mem;DWORD n,off,len,i;SECURITY_ATTRIBUTES sa;
    WCHAR path[MAX_PATH];
    Log=CreateFileA("C:\\xwns98\\matched.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
    event("DELAY_SECONDS",25);Sleep(25000);
    mem.dwLength=sizeof(mem);GlobalMemoryStatus(&mem);event("AVAILABLE_PHYS",mem.dwAvailPhys);
    f=CreateFileA("C:\\xwns98\\scribble.bmp",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    if(f==INVALID_HANDLE_VALUE)fail("FAIL_SOURCE_OPEN");
    if(!ReadFile(f,Data,sizeof(Data),&n,NULL)||n!=sizeof(Data)||GetFileSize(f,NULL)!=sizeof(Data))fail("FAIL_SOURCE_READ");
    if(!CloseHandle(f))fail("FAIL_SOURCE_CLOSE");
    sa.nLength=sizeof(sa);sa.lpSecurityDescriptor=NULL;sa.bInheritHandle=FALSE;
    for(Case=0;Case<16;Case++) {
        wsprintfW(path,L"C:\\xwns98\\match%02lu.bmp",Case);Step=0;
        event("CASE_BEGIN_QUIET",Case&1);
        /* The dialog first creates an empty file; never reuse an older result. */
        f=CreateFileW(path,GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
        if(f==INVALID_HANDLE_VALUE)fail("FAIL_CREATE_NEW");
        if(!CloseHandle(f))fail("FAIL_PRECREATE_CLOSE");
        f=CreateFileW(path,GENERIC_READ|GENERIC_WRITE,0,&sa,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
        if(f==INVALID_HANDLE_VALUE)fail("FAIL_OPEN_ALWAYS");
        off=0;
        while(off<sizeof(Data)) {
            len=off==0?14:(off==14?40:16384);
            if(len>sizeof(Data)-off)fail("FAIL_SHAPE");
            detail("WRITE_BEGIN",off);
            if(!WriteFile(f,Data+off,len,&n,NULL)||n!=len)fail("FAIL_WRITE");
            detail("WRITE_END",n);off+=n;Step++;
            if(off==54 && SetFilePointer(f,0,NULL,FILE_CURRENT)!=54)fail("FAIL_POSITION");
        }
        detail("FLUSH_BEGIN",off);if(!FlushFileBuffers(f))fail("FAIL_FLUSH");detail("FLUSH_END",off);
        detail("EOF_BEGIN",off);if(!SetEndOfFile(f))fail("FAIL_EOF");detail("EOF_END",off);
        if(!CloseHandle(f))fail("FAIL_CLOSE");
        event("SEQUENCE_DONE",Step);
        f=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
        if(f==INVALID_HANDLE_VALUE)fail("FAIL_REOPEN");
        if(GetFileSize(f,NULL)!=sizeof(Data)||!ReadFile(f,Check,sizeof(Check),&n,NULL)||n!=sizeof(Check))fail("FAIL_READBACK");
        for(i=0;i<n;i++)if(Data[i]!=Check[i]){SetLastError(ERROR_CRC);fail("FAIL_BYTES");}
        if(!CloseHandle(f))fail("FAIL_READBACK_CLOSE");
        event("CASE_PASS",n);
    }
    event("PASS",Case);CloseHandle(Log);ExitProcess(0);
}
