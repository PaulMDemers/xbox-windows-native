/* MIT. Known requests, independent result assertions, two calling threads. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
typedef DWORD (__cdecl *PROBE)(DWORD);
static HANDLE output;
static volatile LONG failures;
static void record(const char *s) {
    DWORD n,w; n=lstrlenA(s);
    if(!WriteFile(output,s,n,&w,0)||w!=n) InterlockedIncrement(&failures);
}
static DWORD WINAPI worker(LPVOID unused) {
    HMODULE h; FARPROC a,b; DWORD i; (void)unused;
    h=LoadLibraryA("C:\\xwn597-kit\\fixture.dll");
    if(!h) {InterlockedIncrement(&failures);return 1;}
    for(i=0;i<4;i++) {
        a=GetProcAddress(h,"probe597"); b=GetProcAddress(h,(LPCSTR)7);
        if(!a||a!=b||((PROBE)a)(i)!=(i^0x597abcde)) InterlockedIncrement(&failures);
    }
    if(GetProcAddress(h,"missing597")||GetProcAddress(h,(LPCSTR)8)) InterlockedIncrement(&failures);
    if(!FreeLibrary(h)) InterlockedIncrement(&failures);
    return 0;
}
void WINAPI mainCRTStartup(void) {
    HANDLE t; DWORD id,w; HMODULE h; FARPROC f;
    BOOL control=lstrcmpA(GetCommandLineA(),"subject597 control")==0;
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOOPENFILEERRORBOX);
    output=CreateFileA(control?"C:\\xwn597\\control.txt":"C:\\xwn597\\subject.txt",GENERIC_WRITE,0,0,CREATE_NEW,0,0);
    if(output==INVALID_HANDLE_VALUE) ExitProcess(91);
    record("SUBJECT597 begin\r\n");
    h=LoadLibraryA("user32.dll"); f=h?GetProcAddress(h,"MessageBeep"):0;
    if(!h||!f) InterlockedIncrement(&failures);
    if(h&&!FreeLibrary(h)) InterlockedIncrement(&failures);
    h=LoadLibraryA("xwn597-does-not-exist.dll");
    if(h) {InterlockedIncrement(&failures);FreeLibrary(h);}
    t=CreateThread(0,0,worker,0,0,&id);
    if(!t) InterlockedIncrement(&failures);
    worker(0);
    if(t) {w=WaitForSingleObject(t,10000);if(w!=WAIT_OBJECT_0) InterlockedIncrement(&failures);CloseHandle(t);}
    record(failures?"SUBJECT597 FAIL\r\n":"SUBJECT597 PASS\r\n");
    FlushFileBuffers(output);CloseHandle(output);ExitProcess(failures?1:0);
}
