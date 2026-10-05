/* Emulator-only replacement/lifetime test. Leaves deterministic files for cold audit. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <winioctl.h>
#define ROOT "C:\\xwnlife\\"
static HANDLE Log;
static BYTE Buffer[4096];
static DWORD Checks;
static void text(const char *s) { DWORD n; WriteFile(Log,s,lstrlenA(s),&n,0); FlushFileBuffers(Log); }
static void number(const char *s,DWORD v) {
 char b[16]; DWORD p=15; b[p]=0; do {b[--p]=(char)('0'+v%10);v/=10;}while(v);
 text(s);text(b+p);text("\r\n");
}
static void require(BOOL ok,const char *s) {
 ++Checks; if(!ok) {DWORD e=GetLastError();text("FAIL: ");text(s);text("\r\n");number("error=",e);CloseHandle(Log);ExitProcess(1);}
}
static BYTE pattern(DWORD offset,DWORD seed) {return (BYTE)((offset*37u)^(offset>>8)^seed);}
static void verify(const char *p,DWORD size,DWORD seed) {
 DWORD at=0,n,i,k; HANDLE f=CreateFileA(p,GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,0);
 require(f!=INVALID_HANDLE_VALUE,"open verify");require(GetFileSize(f,0)==size,"size");
 while(at<size) {k=size-at;if(k>sizeof(Buffer))k=sizeof(Buffer);require(ReadFile(f,Buffer,k,&n,0)&&n==k,"read");
 for(i=0;i<k;i++){require(Buffer[i]==pattern(at+i,seed),"data mismatch");}at+=k;}
 require(CloseHandle(f),"close read");
}
static void named(char *p,const char *kind,DWORD i) {
 lstrcpyA(p,ROOT);lstrcatA(p,kind);lstrcatA(p,"00.bin");
 {DWORD at=lstrlenA(p)-6;p[at]=(char)('0'+i/10);p[at+1]=(char)('0'+i%10);}
}
void WINAPI mainCRTStartup(void) {
 DWORD i;char path[80];
 Log=CreateFileA("C:\\xwn-life-reboot.log",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,0,0);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
 text("LIFE-REBOOT-BEGIN\r\n");
 verify(ROOT "pending.bin",131073,32);verify(ROOT "mapped.bin",131073,42);
 for(i=0;i<32;i++){named(path,"target",i);verify(path,131073,100+i);named(path,"reuse",i);verify(path,131073,300+i);}
 text("LIFE-REBOOT-VERIFY-PASS\r\n");CloseHandle(Log);ExitProcess(0);
}
