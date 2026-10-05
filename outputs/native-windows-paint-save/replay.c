/* Bounded BMP-shaped write replay. No driver changes, raw I/O, or automatic reboot. */
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
void WINAPI mainCRTStartup(void) {
    HANDLE f;MEMORYSTATUS mem;DWORD n,off,len,i,flags;char path[]="C:\\xwnpaint\\replay00.bmp";
    Log=CreateFileA("C:\\xwnpaint\\replay.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
    event("DELAY_SECONDS",25);Sleep(25000);
    mem.dwLength=sizeof(mem);GlobalMemoryStatus(&mem);event("AVAILABLE_PHYS",mem.dwAvailPhys);
    event("BEGIN",sizeof(Data));
    f=CreateFileA("C:\\xwnpaint\\scribble.bmp",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    if(f==INVALID_HANDLE_VALUE)fail("FAIL_SOURCE_OPEN");
    if(!ReadFile(f,Data,sizeof(Data),&n,NULL)||n!=sizeof(Data)||GetFileSize(f,NULL)!=sizeof(Data))fail("FAIL_SOURCE_READ");
    CloseHandle(f);
    for(Case=0;Case<16;Case++) {
        path[18]=(char)('0'+Case/10);path[19]=(char)('0'+Case%10);Step=0;
        flags=FILE_ATTRIBUTE_NORMAL|((Case&1)?FILE_FLAG_WRITE_THROUGH:0);
        event("CREATE",flags);f=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,flags,NULL);
        if(f==INVALID_HANDLE_VALUE)fail("FAIL_CREATE");
        off=0;
        while(off<sizeof(Data)) {
            len=off?65536:54;if(len>sizeof(Data)-off)len=sizeof(Data)-off;
            event("WRITE_BEGIN",off);
            if(!WriteFile(f,Data+off,len,&n,NULL)||n!=len)fail("FAIL_WRITE");
            event("WRITE_END",n);off+=n;Step++;
        }
        event("FLUSH_BEGIN",off);if(!FlushFileBuffers(f))fail("FAIL_FLUSH");event("FLUSH_END",off);
        event("CLOSE_BEGIN",off);if(!CloseHandle(f))fail("FAIL_CLOSE");event("CLOSE_END",off);
        f=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
        if(f==INVALID_HANDLE_VALUE)fail("FAIL_REOPEN");
        if(GetFileSize(f,NULL)!=sizeof(Data)||!ReadFile(f,Check,sizeof(Check),&n,NULL)||n!=sizeof(Check))fail("FAIL_READBACK");
        for(i=0;i<n;i++)if(Data[i]!=Check[i]){SetLastError(ERROR_CRC);fail("FAIL_BYTES");}
        CloseHandle(f);event("CASE_PASS",n);
    }
    event("PASS",Case);CloseHandle(Log);ExitProcess(0);
}
