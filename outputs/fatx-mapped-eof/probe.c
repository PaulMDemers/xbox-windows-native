/* NT5 real mapped-file EOF and persisted WriteFile regression. No CRT. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static const DWORD Sizes[]={1,2,511,512,513,4095,4096,4097,8191,8192,8193,65535,65536,65537,131071,131072,131073};
static HANDLE Log;
static DWORD Failures;
static BYTE Buffer[997];
static void record(const char *s,DWORD a,DWORD b,DWORD c) {
    char line[200];DWORD n,w;
    n=(DWORD)wsprintfA(line,"%s %lu %lu %lu\r\n",s,a,b,c);
    if(!WriteFile(Log,line,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(91);
    WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),line,n,&w,NULL);
}
static void fatal(const char *s) {record(s,GetLastError(),0,0);ExitProcess(92);}
static BYTE expected(DWORD offset,DWORD index,DWORD round) {return (BYTE)(offset*13+index*17+round*29);}
static void check(const char *path,DWORD index,DWORD round,const char *label) {
    DWORD size=Sizes[index],i,read,offset=0,bad=0,tail=0,first=0;
    HANDLE file=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL),mapping;
    const BYTE *view;
    if(file==INVALID_HANDLE_VALUE)fatal("FAIL_OPEN");
    if(GetFileSize(file,NULL)!=size){SetLastError(ERROR_INVALID_DATA);fatal("FAIL_SIZE");}
    mapping=CreateFileMappingA(file,NULL,PAGE_READONLY,0,0,NULL);
    if(!mapping)fatal("FAIL_MAPPING");
    view=(const BYTE*)MapViewOfFile(mapping,FILE_MAP_READ,0,0,0);
    if(!view)fatal("FAIL_VIEW");
    for(i=0;i<size;i++)if(view[i]!=expected(i,index,round))bad++;
    /* Only the remainder of the final mapped page, never a page past EOF. */
    for(i=size;i<((size+4095)&~4095UL);i++)if(view[i]){if(!tail)first=view[i];tail++;}
    record(label,index,bad,tail);record("TAIL_FIRST",index,first,size);
    if(bad||tail)Failures++;
    if(!UnmapViewOfFile(view)||!CloseHandle(mapping))fatal("FAIL_UNMAP");
    while(offset<size){
        DWORD ask=size-offset;if(ask>sizeof(Buffer))ask=sizeof(Buffer);
        if(!ReadFile(file,Buffer,ask,&read,NULL)||read!=ask)fatal("FAIL_READ");
        for(i=0;i<read;i++)if(Buffer[i]!=expected(offset+i,index,round)){SetLastError(ERROR_INVALID_DATA);fatal("FAIL_CONTENT");}
        offset+=read;
    }
    if(!ReadFile(file,Buffer,1,&read,NULL)||read!=0)fatal("FAIL_EOF");
    if(!CloseHandle(file))fatal("FAIL_CLOSE");
}
static void writefile(const char *path,DWORD index,DWORD round) {
    DWORD offset=0,i,written,n,size=Sizes[index];
    HANDLE file=CreateFileA(path,GENERIC_WRITE,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
    if(file==INVALID_HANDLE_VALUE)fatal("FAIL_CREATE");
    while(offset<size){
        n=size-offset;if(n>sizeof(Buffer))n=sizeof(Buffer);
        for(i=0;i<n;i++)Buffer[i]=expected(offset+i,index,round);
        if(!WriteFile(file,Buffer,n,&written,NULL)||written!=n)fatal("FAIL_WRITE");
        offset+=written;
    }
    if(!FlushFileBuffers(file)||!CloseHandle(file))fatal("FAIL_FLUSH");
}
void WINAPI mainCRTStartup(void) {
    DWORD i,round;char path[MAX_PATH];HANDLE token;TOKEN_PRIVILEGES tp;
    Log=CreateFileA("C:\\xwneof01\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
    record("ATTEMPT_ONCE",17,8,997);
    for(i=0;i<17;i++){
        wsprintfA(path,"C:\\xwneof01\\input%02lu.bin",i);check(path,i,0,"INPUT");
    }
    for(round=1;round<=8;round++){
        record("ROUND",round,0,0);
        for(i=0;i<17;i++){
            wsprintfA(path,"C:\\xwneof01\\output%02lu.bin",i);
            writefile(path,i,round);check(path,i,round,"OUTPUT");
        }
    }
    record("COMPLETE",Failures,17,8);
    /* Even an expected old-driver tail mismatch must get a normal shutdown. */
    Sleep(120000);
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))fatal("FAIL_TOKEN");
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))fatal("FAIL_LOOKUP");
    SetLastError(ERROR_SUCCESS);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)fatal("FAIL_PRIVILEGE");
    CloseHandle(token);record("NORMAL_RESTART_REQUEST",0,0,0);
    if(!ExitWindowsEx(EWX_REBOOT,0))fatal("FAIL_RESTART");
    CloseHandle(Log);ExitProcess(0);
}
