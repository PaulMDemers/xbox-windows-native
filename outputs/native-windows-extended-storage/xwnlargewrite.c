/* Bounded high-LBA overwrite/restart check; owned emulator fixtures only. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log;
static BYTE Data[4097],Check[4097];
static void line(const char *s){DWORD n;WriteFile(Log,s,lstrlenA(s),&n,NULL);FlushFileBuffers(Log);}
static void number(const char *s,DWORD v){char b[16];unsigned n=sizeof(b);b[--n]=0;b[--n]='\n';b[--n]='\r';do{b[--n]='0'+v%10;v/=10;}while(v);line(s);line(b+n);}
void WINAPI mainCRTStartup(void){
 HANDLE f=INVALID_HANDLE_VALUE,token;DWORD n,i,generation=0,fail=0;TOKEN_PRIVILEGES tp;
 Log=CreateFileA("C:\\xwn-large-write.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
 line("XWN bounded native Windows high-LBA overwrite and restart test\r\n");
 f=CreateFileA("C:\\xwn-high.bin",GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
 if(f==INVALID_HANDLE_VALUE){number("Open error: ",GetLastError());fail++;goto done;}
 if(GetFileSize(f,NULL)!=4097||!ReadFile(f,Data,sizeof(Data),&n,NULL)||n!=sizeof(Data)){fail++;goto done;}
 if(Data[0]==0x5a)generation=0;else if(Data[0]==0x65)generation=1;else {fail++;goto done;}
 for(i=0;i<sizeof(Data);i++)if(Data[i]!=(BYTE)(i*37+(i>>8)+0x5a+11*generation)){fail++;goto done;}
 number("Previous generation: ",generation);
 for(i=0;i<sizeof(Data);i++)Data[i]=(BYTE)(i*37+(i>>8)+0x5a+11*(generation+1));
 if(SetFilePointer(f,0,NULL,FILE_BEGIN)!=0||!WriteFile(f,Data,sizeof(Data),&n,NULL)||n!=sizeof(Data)||!FlushFileBuffers(f)){number("Write error: ",GetLastError());fail++;goto done;}
 CloseHandle(f);f=CreateFileA("C:\\xwn-high.bin",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE||!ReadFile(f,Check,sizeof(Check),&n,NULL)||n!=sizeof(Check)){fail++;goto done;}
 for(i=0;i<sizeof(Data);i++)if(Check[i]!=Data[i])fail++;
 number("Written generation: ",generation+1);
done:
 if(f!=INVALID_HANDLE_VALUE)CloseHandle(f);
 number("Failures: ",fail);
 if(fail){CloseHandle(Log);ExitProcess(fail);}
 line("XWN-LARGE-WRITE-PASS: existing high-LBA file overwritten, flushed and reopened\r\n");
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)||
    !LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){
  line("Shutdown privilege lookup failed\r\n");CloseHandle(Log);ExitProcess(3);
 }
 tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;SetLastError(0);
 if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=0){CloseHandle(token);line("Shutdown privilege failed\r\n");CloseHandle(Log);ExitProcess(4);}
 CloseHandle(token);
#ifdef XWN_REBOOT
 line("Requesting normal Windows restart\r\n");CloseHandle(Log);
 Sleep(3000);if(!ExitWindowsEx(EWX_REBOOT,0))ExitProcess(5);
#else
 line("Requesting normal Windows shutdown\r\n");CloseHandle(Log);
 Sleep(3000);if(!ExitWindowsEx(EWX_SHUTDOWN,0))ExitProcess(5);
#endif
 ExitProcess(0);
}
