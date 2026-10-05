/* Bounded emulator-only memory pressure while a human-equivalent Paint save runs. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static BYTE *Blocks[16];
static HANDLE Log;
static char Text[2048];
static DWORD Used;
static void line(const char *s,DWORD v) {
    char digits[16];DWORD n=0,w;
    while(*s && Used<sizeof(Text)-32)Text[Used++]=*s++;
    do {digits[n++]=(char)('0'+v%10);v/=10;}while(v);
    while(n)Text[Used++]=digits[--n];Text[Used++]='\r';Text[Used++]='\n';
    SetFilePointer(Log,0,NULL,FILE_BEGIN);WriteFile(Log,Text,Used,&w,NULL);FlushFileBuffers(Log);
}
void WINAPI mainCRTStartup(void) {
    DWORD i,j,start,round=0,count=0;MEMORYSTATUS mem;
    Log=CreateFileA("C:\\xwnpaint\\pressure.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
    line("delay_seconds=",20);Sleep(20000);
    mem.dwLength=sizeof(mem);GlobalMemoryStatus(&mem);line("available_before=",mem.dwAvailPhys);
    for(i=0;i<16;i++) {
        Blocks[i]=VirtualAlloc(NULL,1024*1024,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
        if(!Blocks[i]){line("allocation_error=",GetLastError());break;}
        for(j=0;j<1024*1024;j+=4096)Blocks[i][j]=(BYTE)i;
        count++;
    }
    line("allocated_mib=",count);GlobalMemoryStatus(&mem);line("available_holding=",mem.dwAvailPhys);
    start=GetTickCount();
    while(GetTickCount()-start<180000) {
        for(i=0;i<count;i++)for(j=0;j<1024*1024;j+=4096)Blocks[i][j]++;
        round++;Sleep(200);
    }
    for(i=0;i<count;i++)VirtualFree(Blocks[i],0,MEM_RELEASE);
    line("rounds=",round);line("complete=",1);CloseHandle(Log);ExitProcess(0);
}
