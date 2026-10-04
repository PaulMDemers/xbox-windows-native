/* Bounded native Windows FATX test: only dedicated XWN test files. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log=INVALID_HANDLE_VALUE;
static BYTE Data[65537],Check[65537];
static void line(const char *s){DWORD n;if(Log!=INVALID_HANDLE_VALUE){WriteFile(Log,s,lstrlenA(s),&n,NULL);FlushFileBuffers(Log);}}
static void number(const char *s,DWORD v){char b[16];unsigned n=sizeof(b);b[--n]=0;b[--n]='\n';b[--n]='\r';do{b[--n]='0'+v%10;v/=10;}while(v);line(s);line(b+n);}
void WINAPI mainCRTStartup(void){
 HANDLE f=INVALID_HANDLE_VALUE,t;DWORD n,i,fail=0,spc,bps,free,total;TOKEN_PRIVILEGES tp;char path[MAX_PATH];
 Log=CreateFileA("C:\\xwn-physical.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 if(Log==INVALID_HANDLE_VALUE){fail++;goto done;}
 line("XWN physical F native Windows test v1\r\n");
 if(!GetWindowsDirectoryA(path,sizeof(path))||lstrcmpiA(path,"C:\\WINNT")){line("Unexpected Windows directory\r\n");fail++;goto done;}
 if(!GetDiskFreeSpaceA("C:\\",&spc,&bps,&free,&total)){fail++;goto done;}
 number("Sectors per cluster: ",spc);number("Bytes per sector: ",bps);number("Total clusters: ",total);number("Free clusters: ",free);
 if(spc!=128||bps!=512||total<3000000){fail++;goto done;}
 f=CreateFileA("C:\\xwn-physical.bin",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE||GetFileSize(f,NULL)!=sizeof(Data)||!ReadFile(f,Data,sizeof(Data),&n,NULL)||n!=sizeof(Data)){fail++;goto done;}
 for(i=0;i<sizeof(Data);i++)if(Data[i]!=(BYTE)(i*37+(i>>8)+0x5a)){fail++;goto done;}
 CloseHandle(f);f=INVALID_HANDLE_VALUE;line("Seed read verified: 65537 bytes\r\n");
 f=CreateFileA("C:\\xwn-physical-write.bin",GENERIC_READ|GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
 if(f==INVALID_HANDLE_VALUE){fail++;goto done;}
 for(i=0;i<sizeof(Data);i++)Data[i]^=0xa5;
 if(!WriteFile(f,Data,sizeof(Data),&n,NULL)||n!=sizeof(Data)||!FlushFileBuffers(f)){fail++;goto done;}
 CloseHandle(f);f=CreateFileA("C:\\xwn-physical-write.bin",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE||GetFileSize(f,NULL)!=sizeof(Check)||!ReadFile(f,Check,sizeof(Check),&n,NULL)||n!=sizeof(Check)){fail++;goto done;}
 for(i=0;i<sizeof(Data);i++)if(Check[i]!=Data[i]){fail++;goto done;}
 line("New file write, flush and reopen verified: 65537 bytes\r\n");
done:
 if(f!=INVALID_HANDLE_VALUE)CloseHandle(f);number("Failures: ",fail);
 line(fail?"XWN-PHYSICAL-FAIL\r\n":"XWN-PHYSICAL-PASS\r\n");
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&t)||!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){line("Restart privilege unavailable\r\n");ExitProcess(3);}
 tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;SetLastError(0);
 if(!AdjustTokenPrivileges(t,FALSE,&tp,0,NULL,NULL)||GetLastError()!=0){CloseHandle(t);line("Restart privilege failed\r\n");ExitProcess(4);}
 CloseHandle(t);line("Requesting normal restart in 15 seconds\r\n");if(Log!=INVALID_HANDLE_VALUE)CloseHandle(Log);
 Sleep(15000);if(!ExitWindowsEx(EWX_REBOOT,0))ExitProcess(5);ExitProcess(fail);
}
