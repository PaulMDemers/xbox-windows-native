/* Private NT5 emulator paging-pressure probe; no CRT and no raw disk I/O. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <psapi.h>
#define BYTES (40u * 1024 * 1024)
static HANDLE Log;
static DWORD Failures;
static void line(const char *s) {
 DWORD n; WriteFile(Log,s,lstrlenA(s),&n,NULL); FlushFileBuffers(Log);
 WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),s,lstrlenA(s),&n,NULL);
}
static void number(const char *s,DWORD v) {
 char b[16];unsigned n=sizeof(b);b[--n]=0;b[--n]='\n';b[--n]='\r';
 do {b[--n]='0'+v%10;v/=10;}while(v);line(s);line(b+n);
}
static DWORD pattern(DWORD index,DWORD pass) {
 return (index * 0x9e3779b9u) ^ (pass * 0x85ebca6bu) ^ 0x1234abcdu;
}
static void stats(void) {
 PROCESS_MEMORY_COUNTERS p;MEMORYSTATUS m;
 p.cb=sizeof(p);
 if(GetProcessMemoryInfo(GetCurrentProcess(),&p,sizeof(p))) {
  number("Page faults: ",p.PageFaultCount);number("Working set bytes: ",p.WorkingSetSize);
  number("Committed bytes: ",p.PagefileUsage);
 }
 m.dwLength=sizeof(m);GlobalMemoryStatus(&m);number("Available physical bytes: ",m.dwAvailPhys);
}
void WINAPI mainCRTStartup(void) {
 DWORD *ram,i,pass,started=GetTickCount();
 Log=CreateFileA("C:\\xwn-paging.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
 line("XWN 40 MiB paging-pressure test\r\n");stats();
 ram=VirtualAlloc(NULL,BYTES,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
 if(!ram){number("Allocation failed: ",GetLastError());++Failures;goto done;}
 for(i=0;i<BYTES/4;++i)ram[i]=pattern(i,0);
 for(pass=0;pass<8;++pass) {
  number("Pass: ",pass+1);stats();
  if(!SetProcessWorkingSetSize(GetCurrentProcess(),(SIZE_T)-1,(SIZE_T)-1)) {
   number("Working-set trim failed: ",GetLastError());++Failures;break;
  }
  line("After trim\r\n");stats();Sleep(5000);
  /* A full reverse scan verifies every word, then changes it for the next
   * eviction cycle. This checks retained data, not allocation success alone. */
  for(i=BYTES/4;i--;) {
   if(ram[i]!=pattern(i,pass)) {
    number("Mismatch at word: ",i);number("Expected: ",pattern(i,pass));
    number("Actual: ",ram[i]);++Failures;goto free_ram;
   }
   ram[i]=pattern(i,pass+1);
  }
  line("40 MiB comparison passed\r\n");stats();
 }
 free_ram: VirtualFree(ram,0,MEM_RELEASE);
 done: number("Elapsed milliseconds: ",GetTickCount()-started);number("Failures: ",Failures);
 CloseHandle(Log);ExitProcess(Failures);
}
