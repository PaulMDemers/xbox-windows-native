/* MIT. Known requests, independent result assertions, two calling threads. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
typedef DWORD (__cdecl *PROBE)(DWORD,DWORD);
static HANDLE output;
static volatile LONG failures;
static void record(const char *s) {
    DWORD n,w; n=lstrlenA(s);
    if(!WriteFile(output,s,n,&w,0)||w!=n) InterlockedIncrement(&failures);
}
static DWORD WINAPI worker(LPVOID unused) {
    HMODULE h; FARPROC a,b; DWORD i,expected; (void)unused;
    h=LoadLibraryA("C:\\xwn601-kit\\fixture.dll");
    if(!h) {InterlockedIncrement(&failures);return 1;}
    for(i=0;i<4;i++) {
        a=GetProcAddress(h,"probe601"); b=GetProcAddress(h,(LPCSTR)7);
        expected=((i+i)^0x601abcdeu)+i*(i+1)/2;
        if(!a||a!=b||((PROBE)a)(i,i)!=expected) InterlockedIncrement(&failures);
    }
    if(GetProcAddress(h,"missing601")||GetProcAddress(h,(LPCSTR)8)) InterlockedIncrement(&failures);
    /* Keep fixture loaded: recorder retains code breakpoints until process exit. */
    return 0;
}
#include "graphics.h"
void WINAPI mainCRTStartup(void) {
    HANDLE t; DWORD id,w; HMODULE h; FARPROC f;
    BOOL control=lstrcmpA(GetCommandLineA(),"subject601 control")==0;
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOOPENFILEERRORBOX);
    output=CreateFileA(control?"C:\\xwn601\\control.txt":"C:\\xwn601\\subject.txt",GENERIC_WRITE,0,0,CREATE_NEW,0,0);
    if(output==INVALID_HANDLE_VALUE) ExitProcess(91);
    record("SUBJECT601 begin\r\n");
    h=LoadLibraryA("user32.dll"); f=h?GetProcAddress(h,"MessageBeep"):0;
    if(!h||!f) InterlockedIncrement(&failures);
    if(h&&!FreeLibrary(h)) InterlockedIncrement(&failures);
    h=LoadLibraryA("xwn601-does-not-exist.dll");
    if(h) {InterlockedIncrement(&failures);FreeLibrary(h);}
    t=CreateThread(0,0,worker,0,0,&id);
    if(!t) InterlockedIncrement(&failures);
    worker(0);
    if(t) {w=WaitForSingleObject(t,10000);if(w!=WAIT_OBJECT_0) InterlockedIncrement(&failures);CloseHandle(t);}
    if(!graphics601())InterlockedIncrement(&failures);
    record(failures?"SUBJECT601 FAIL\r\n":"SUBJECT601 PASS\r\n");
    FlushFileBuffers(output);CloseHandle(output);ExitProcess(failures?1:0);
}
