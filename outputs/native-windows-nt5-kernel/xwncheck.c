/* Private native Windows 2000 desktop endurance probe; no CRT required. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log;
static DWORD Failures;
static void line(const char *s) {
 DWORD n; WriteFile(Log,s,lstrlenA(s),&n,NULL); FlushFileBuffers(Log);
 WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),s,lstrlenA(s),&n,NULL);
}
static void number(const char *s,DWORD v) {
 char b[16]; unsigned n=sizeof(b); b[--n]=0;b[--n]='\n';b[--n]='\r';
 do {b[--n]='0'+v%10;v/=10;} while(v);line(s);line(b+n);
}
static void fail(const char *s) {++Failures;line(s);number("Win32 error: ",GetLastError());}
static DWORD NotePid, NoteWindows;
static BOOL CALLBACK check_window(HWND w,LPARAM ignored) {
 DWORD pid,result;char title[256];GetWindowThreadProcessId(w,&pid);
 if(pid!=NotePid || !IsWindowVisible(w))return TRUE;
 ++NoteWindows;GetWindowTextA(w,title,sizeof(title));line("Notepad window: ");line(title);line("\r\n");
 if(!SendMessageTimeoutA(w,WM_NULL,0,0,SMTO_ABORTIFHUNG,2000,&result))fail("GUI response failed\r\n");
 else line("GUI response passed\r\n");
 PostMessageA(w,WM_CLOSE,0,0);return TRUE;
}
void WINAPI mainCRTStartup(void) {
 MEMORYSTATUS memory;OSVERSIONINFOA version;HANDLE f;BYTE *buffer,*ram;DWORD block,i,n,started,wait;BOOL okay=TRUE;
 STARTUPINFOA si;PROCESS_INFORMATION pi;char command[]="C:\\WINNT\\system32\\notepad.exe C:\\xwn-check.log";
 Log=CreateFileA("C:\\xwn-check.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
 line("XWN native Windows endurance probe\r\n");
 version.dwOSVersionInfoSize=sizeof(version);GetVersionExA(&version);
 number("OS major: ",version.dwMajorVersion);number("OS minor: ",version.dwMinorVersion);number("OS build: ",version.dwBuildNumber);
 memory.dwLength=sizeof(memory);GlobalMemoryStatus(&memory);number("Physical bytes: ",memory.dwTotalPhys);number("Available bytes before: ",memory.dwAvailPhys);
 buffer=VirtualAlloc(NULL,65536,MEM_COMMIT,PAGE_READWRITE);ram=VirtualAlloc(NULL,8*1024*1024,MEM_COMMIT,PAGE_READWRITE);
 if(!buffer || !ram) {fail("Memory allocation failed\r\n");goto done;}
 for(i=0;i<8*1024*1024;++i)ram[i]=(BYTE)(i*13+(i>>12));
 started=GetTickCount();
 f=CreateFileA("C:\\xwn-disk-test.bin",GENERIC_WRITE,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
 if(f==INVALID_HANDLE_VALUE) {fail("Disk create failed\r\n");goto done;}
 for(block=0;block<64;++block) {
  for(i=0;i<65536;++i)buffer[i]=(BYTE)((i*17+block*29)^0xa5);
  if(!WriteFile(f,buffer,65536,&n,NULL)||n!=65536){fail("Disk write failed\r\n");okay=FALSE;break;}
 }
 if(!FlushFileBuffers(f)){fail("Disk flush failed\r\n");okay=FALSE;}CloseHandle(f);
 f=CreateFileA("C:\\xwn-disk-test.bin",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE){fail("Disk reopen failed\r\n");goto done;}
 for(block=0;okay && block<64;++block) {
  if(!ReadFile(f,buffer,65536,&n,NULL)||n!=65536){fail("Disk read failed\r\n");okay=FALSE;break;}
  for(i=0;i<65536;++i)if(buffer[i]!=(BYTE)((i*17+block*29)^0xa5)){fail("Disk comparison failed\r\n");okay=FALSE;break;}
 }
 CloseHandle(f);if(okay){line("4 MiB write/flush/reopen/read comparison passed\r\n");DeleteFileA("C:\\xwn-disk-test.bin");}
 number("Disk test milliseconds: ",GetTickCount()-started);
 for(i=0;i<sizeof(si);++i)((BYTE*)&si)[i]=0;si.cb=sizeof(si);
 if(CreateProcessA(NULL,command,NULL,NULL,FALSE,0,NULL,NULL,&si,&pi)) {
  NotePid=pi.dwProcessId;wait=WaitForInputIdle(pi.hProcess,10000);number("Notepad input-idle result: ",wait);if(wait)fail("Notepad input-idle failed\r\n");
  Sleep(10000);EnumWindows(check_window,0);if(!NoteWindows)fail("Notepad window not found\r\n");CloseHandle(pi.hThread);CloseHandle(pi.hProcess);
 } else fail("Notepad launch failed\r\n");
 for(block=0;block<20;++block) {
  Sleep(5000);
  for(i=0;i<8*1024*1024;++i)if(ram[i]!=(BYTE)(i*13+(i>>12))){fail("Memory comparison failed\r\n");goto done;}
  number("Memory pass: ",block+1);number("Uptime milliseconds: ",GetTickCount());
 }
 line("8 MiB memory retention passed across 20 intervals\r\n");
 done:
 if(buffer)VirtualFree(buffer,0,MEM_RELEASE);if(ram)VirtualFree(ram,0,MEM_RELEASE);
 memory.dwLength=sizeof(memory);GlobalMemoryStatus(&memory);number("Available bytes after: ",memory.dwAvailPhys);
 number("Failures: ",Failures);CloseHandle(Log);ExitProcess(Failures);
}
