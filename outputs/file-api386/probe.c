/* SPDX-License-Identifier: MIT
 * Owned-directory file API and exact-name enumeration discriminator for NT5. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log;
static DWORD Failures;
static BYTE A[16384], B[16384];
static void text(const char *s) {
    DWORD n=0,w=0;
    while(s[n])++n;
    if(!WriteFile(Log,s,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);
}
static void status(const char *tag,BOOL ok,DWORD error) {
    char line[256];
    wsprintfA(line,"%s %lu %lu\r\n",tag,(DWORD)ok,error);text(line);
    if(!ok)++Failures;
}
static BOOL result(const char *tag,BOOL ok) {
    DWORD e=ok?0:GetLastError();status(tag,ok,e);return ok;
}
static BOOL absent(const char *name) {
    DWORD value=GetFileAttributesA(name),e=GetLastError();
    BOOL ok=value==INVALID_FILE_ATTRIBUTES&&e==ERROR_FILE_NOT_FOUND;
    status(name,ok,ok?0:e);return ok;
}
static void enumerate(const char *pattern) {
    WIN32_FIND_DATAA d;HANDLE h;DWORD count=0,e=0;BOOL match=TRUE,more;
    char line[768];
    h=FindFirstFileA(pattern,&d);
    if(h==INVALID_HANDLE_VALUE){status("ENUM_OPEN",FALSE,GetLastError());return;}
    do {
        ++count;
        wsprintfA(line,"ENUM_NAME %s %lu %s\r\n",pattern,count,d.cFileName);text(line);
        if(lstrcmpiA(pattern,d.cFileName)!=0)match=FALSE;
        if(count==32){match=FALSE;e=ERROR_BUFFER_OVERFLOW;break;}
        more=FindNextFileA(h,&d);if(!more)e=GetLastError();
    } while(more);
    result("ENUM_CLOSE",FindClose(h));
    wsprintfA(line,"ENUM_END %s %lu %lu\r\n",pattern,count,e);text(line);
    status("ENUM_EXACT",match&&count==1&&e==ERROR_NO_MORE_FILES,e);
}
static BOOL compare(const char *left,const char *right) {
    HANDLE x,y;DWORD na,nb,i,total=0;BOOL ok=TRUE;
    x=CreateFileA(left,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);
    if(x==INVALID_HANDLE_VALUE){status("COMPARE_LEFT",FALSE,GetLastError());return FALSE;}
    y=CreateFileA(right,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);
    if(y==INVALID_HANDLE_VALUE){status("COMPARE_RIGHT",FALSE,GetLastError());CloseHandle(x);return FALSE;}
    for(;;) {
        if(!ReadFile(x,A,sizeof(A),&na,NULL)||!ReadFile(y,B,sizeof(B),&nb,NULL)){ok=FALSE;break;}
        if(na!=nb){ok=FALSE;break;}
        for(i=0;i<na;++i)if(A[i]!=B[i]){ok=FALSE;break;}
        if(!ok||!na)break;
        total+=na;if(total>8UL*1024UL*1024UL){ok=FALSE;break;}
    }
    result("COMPARE_CLOSE_LEFT",CloseHandle(x));result("COMPARE_CLOSE_RIGHT",CloseHandle(y));
    status(right,ok,ok?0:ERROR_INVALID_DATA);return ok;
}
static BOOL write_new(const char *name,const char *value) {
    HANDLE h;DWORD n=0,w=0;BOOL ok;
    while(value[n])++n;
    h=CreateFileA(name,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(h==INVALID_HANDLE_VALUE){status("CREATE_NEW",FALSE,GetLastError());return FALSE;}
    ok=result("WRITE",WriteFile(h,value,n,&w,NULL));
    if(w!=n){status("WRITE_LENGTH",FALSE,ERROR_WRITE_FAULT);ok=FALSE;}
    if(!result("FLUSH",FlushFileBuffers(h)))ok=FALSE;
    if(!result("CLOSE",CloseHandle(h)))ok=FALSE;
    return ok;
}
void WINAPI mainCRTStartup(void) {
    char dir[MAX_PATH],line[128];DWORD n,i;
    const char *outputs[]={"saved.tmp","saved.bmp","reopened.bmp","note.tmp","note.txt","note-reopened.txt","file-complete.txt"};
    n=GetModuleFileNameA(NULL,dir,sizeof(dir));if(!n||n>=sizeof(dir))ExitProcess(91);
    while(n&&dir[n-1]!='\\')--n;
    if(!n)ExitProcess(92);
    dir[n-1]=0;
    if(!SetCurrentDirectoryA(dir))ExitProcess(93);
    Log=CreateFileA("file-api.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(94);
    text("FILE_API_BEGIN 386\r\n");
    for(i=0;i<sizeof(outputs)/sizeof(outputs[0]);++i)if(!absent(outputs[i]))goto done;
    if(!result("COPY_BMP",CopyFileA("input.bmp","saved.tmp",TRUE)))goto done;
    enumerate("saved.tmp");
    if(!result("MOVE_BMP",MoveFileA("saved.tmp","saved.bmp")))goto done;
    enumerate("saved.bmp");
    if(!absent("saved.tmp"))goto done;
    if(!result("REOPEN_BMP",CopyFileA("saved.bmp","reopened.bmp",TRUE)))goto done;
    if(!compare("input.bmp","saved.bmp")||!compare("input.bmp","reopened.bmp"))goto done;
    if(!write_new("note.tmp","XWN386 text persistence check\r\n"))goto done;
    if(!result("MOVE_NOTE",MoveFileA("note.tmp","note.txt")))goto done;
    if(!absent("note.tmp"))goto done;
    if(!result("REOPEN_NOTE",CopyFileA("note.txt","note-reopened.txt",TRUE)))goto done;
    if(!compare("note.txt","note-reopened.txt"))goto done;
    if(!Failures)write_new("file-complete.txt","COMPLETE\r\n");
done:
    wsprintfA(line,"FILE_API_END %lu\r\n",Failures);text(line);
    CloseHandle(Log);ExitProcess(Failures?1:0);
}
