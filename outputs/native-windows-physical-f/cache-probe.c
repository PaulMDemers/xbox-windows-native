/* Owned emulator regression: cached append, mapped writes and truncate. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static BYTE Data[131073], Check[131073];
static char Report[4096];
static DWORD Used, Failures;
static HANDLE Log;
static void line(const char *s) {
    DWORD n;
    while (*s && Used < sizeof(Report)-2) Report[Used++]=*s++;
    SetFilePointer(Log,0,NULL,FILE_BEGIN);
    WriteFile(Log,Report,sizeof(Report),&n,NULL); FlushFileBuffers(Log);
}
static void value(const char *s,DWORD v) {
    char b[20]; unsigned n=sizeof(b); b[--n]=0;b[--n]='\n';b[--n]='\r';
    do {b[--n]='0'+v%10;v/=10;} while(v);line(s);line(b+n);
}
static BOOL fail(const char *s) { DWORD e=GetLastError();Failures++;line(s);value(" error=",e);return FALSE; }
static BYTE pattern(DWORD i,DWORD salt) {return (BYTE)(i*37+(i>>8)+salt);}
static BOOL verify(HANDLE f,DWORD length,DWORD salt) {
    DWORD n,i;
    if(SetFilePointer(f,0,NULL,FILE_BEGIN)!=0 || !ReadFile(f,Check,length,&n,NULL) || n!=length)return fail("read");
    for(i=0;i<n;i++)if(Check[i]!=pattern(i,salt)){Failures++;value("mismatch offset=",i);return FALSE;}
    return TRUE;
}
static BOOL mapped(DWORD length,DWORD cut,BOOL flush,DWORD salt) {
    HANDLE f,m;BYTE *v;DWORD i;BOOL ok=FALSE;
    f=CreateFileA("C:\\xwn-cache-map.tmp",GENERIC_READ|GENERIC_WRITE,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
    if(f==INVALID_HANDLE_VALUE)return fail("create mapped");
    m=CreateFileMappingA(f,NULL,PAGE_READWRITE,0,length,NULL);
    if(!m){fail("section");goto done;}
    v=MapViewOfFile(m,FILE_MAP_WRITE,0,0,length);
    if(!v){fail("map");CloseHandle(m);goto done;}
    for(i=0;i<length;i++)v[i]=pattern(i,salt);
    if(flush && !FlushViewOfFile(v,length))fail("flush view");
    UnmapViewOfFile(v);CloseHandle(m);
    if(SetFilePointer(f,cut,NULL,FILE_BEGIN)!=cut || !SetEndOfFile(f)){fail("truncate");goto done;}
    if(!FlushFileBuffers(f)){fail("flush truncated");goto done;}
    CloseHandle(f);
    f=CreateFileA("C:\\xwn-cache-map.tmp",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    if(f==INVALID_HANDLE_VALUE)return fail("reopen mapped");
    if(GetFileSize(f,NULL)!=cut){fail("truncated size");goto done;}
    ok=verify(f,cut,salt);
done:CloseHandle(f);return ok;
}
static BOOL append(void) {
    DWORD i,n,off=0,len;HANDLE f;
    f=CreateFileA("C:\\xwn-cache-append.tmp",GENERIC_READ|GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(f==INVALID_HANDLE_VALUE)return fail("create append");
    for(i=0;i<sizeof(Data);i++)Data[i]=pattern(i,0x65);
    while(off<sizeof(Data)) {
        len=(off%2001)+17;if(len>sizeof(Data)-off)len=sizeof(Data)-off;
        if(!WriteFile(f,Data+off,len,&n,NULL)||n!=len){fail("append");CloseHandle(f);return FALSE;}
        off+=len;
    }
    if(!FlushFileBuffers(f)){fail("flush append");CloseHandle(f);return FALSE;}
    CloseHandle(f);f=CreateFileA("C:\\xwn-cache-append.tmp",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    if(f==INVALID_HANDLE_VALUE)return fail("reopen append");
    i=verify(f,sizeof(Data),0x65);CloseHandle(f);return (BOOL)i;
}
#ifdef XWN_CACHE_STRESS
/* Keep each pending buffer alive. Force cache pressure with asynchronous
 * cached writes while 16 MiB remains resident in this test process. */
static BOOL pressure(void) {
    BYTE *mem,*buffers;HANDLE f;OVERLAPPED ov[16];DWORD batch,j,i,n,total=32*1024*1024;
    BOOL ok=TRUE;DWORD issued=0;
    mem=VirtualAlloc(NULL,16*1024*1024,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
    buffers=VirtualAlloc(NULL,16*65536,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
    if(!mem||!buffers)return fail("pressure allocation");
    for(i=0;i<16*1024*1024;i+=4096)mem[i]=(BYTE)(i>>12);
    f=CreateFileA("C:\\xwn-cache-pressure.tmp",GENERIC_READ|GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_OVERLAPPED,NULL);
    if(f==INVALID_HANDLE_VALUE){fail("pressure create");ok=FALSE;goto release;}
    for(i=0;i<sizeof(ov);i++)((volatile BYTE *)ov)[i]=0;
    for(j=0;j<16;j++){ov[j].hEvent=CreateEventA(NULL,TRUE,FALSE,NULL);if(!ov[j].hEvent){fail("event");ok=FALSE;goto close;}}
    for(batch=0;batch<total/(16*65536);batch++) {
        issued=0;
        for(j=0;j<16;j++) {
            ov[j].Offset=(batch*16+j)*65536;ResetEvent(ov[j].hEvent);
            for(i=0;i<65536;i++)buffers[j*65536+i]=pattern(ov[j].Offset+i,0x77);
            if(!WriteFile(f,buffers+j*65536,65536,&n,&ov[j])&&GetLastError()!=ERROR_IO_PENDING){fail("async write");ok=FALSE;break;}
            issued++;
        }
        for(j=0;j<issued;j++)if(!GetOverlappedResult(f,&ov[j],&n,TRUE)||n!=65536){fail("async completion");ok=FALSE;}
        if(!ok)break;
        for(i=0;i<16*1024*1024;i+=4096)mem[i]^=1;
        if(batch%8==0)value("pressure batch=",batch);
    }
    if(!FlushFileBuffers(f)){fail("pressure flush");ok=FALSE;}
close:
    CloseHandle(f);
    for(j=0;j<16;j++)if(ov[j].hEvent)CloseHandle(ov[j].hEvent);
    if(ok) {
        f=CreateFileA("C:\\xwn-cache-pressure.tmp",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
        if(f==INVALID_HANDLE_VALUE){fail("pressure reopen");ok=FALSE;goto release;}
        for(batch=0;batch<total/65536;batch++) {
            if(!ReadFile(f,buffers,65536,&n,NULL)||n!=65536){fail("pressure read");ok=FALSE;break;}
            for(i=0;i<65536;i++)if(buffers[i]!=pattern(batch*65536+i,0x77)){value("pressure mismatch=",batch*65536+i);Failures++;ok=FALSE;break;}
            if(!ok)break;
        }
        CloseHandle(f);
    }
release:VirtualFree(mem,0,MEM_RELEASE);VirtualFree(buffers,0,MEM_RELEASE);return ok;
}
#endif
void WINAPI mainCRTStartup(void) {
    DWORD i,spc,bps,free,total;HANDLE t;TOKEN_PRIVILEGES tp;
    static const DWORD sizes[]={4097,65535,65536,65537,131073};
    SetConsoleTitleA("XWN emulator cache regression");
    if(!GetDiskFreeSpaceA("C:\\",&spc,&bps,&free,&total)||spc!=128||bps!=512||total!=3693243)ExitProcess(90);
    Log=CreateFileA("C:\\xwn-report-v2.txt",GENERIC_WRITE,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(91);
    for(i=0;i<sizeof(Report);i++)Report[i]=' ';
    line("XWN-CACHE-START\r\n");
    if(!append())goto finish;
    line("cached append passed\r\n");
#ifdef XWN_CACHE_LONG
    for(i=0;i<300;i++) {
        value("map=",i);
#else
    for(i=0;i<30;i++) {
        value("mapped case=",i);
#endif
        if(!mapped(sizes[i%5],i%3==0?2577:(i%3==1?1:0),i%2,(i+0x31)))goto finish;
    }
    line("mapped truncate passed\r\n");
#ifdef XWN_CACHE_STRESS
    if(!pressure())goto finish;
    line("async pressure passed\r\n");
#endif
    Sleep(15000);
finish:
    value("failures=",Failures);line(Failures?"XWN-CACHE-FAIL\r\n":"XWN-CACHE-PASS\r\n");CloseHandle(Log);
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&t)||!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(92);
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;SetLastError(0);
    if(!AdjustTokenPrivileges(t,FALSE,&tp,0,NULL,NULL)||GetLastError())ExitProcess(93);
    CloseHandle(t);Sleep(5000);ExitWindowsEx(EWX_REBOOT,0);ExitProcess(Failures);
}
