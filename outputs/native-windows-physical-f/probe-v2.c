/* Native storage diagnostic: validate F geometry before any diagnostic write. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static BYTE Data[65537],Check[65537];
static char Report[4096];
static DWORD Used,Failures;
static const char Pending[]="XWN-V2-PENDING-20261004\r\n";
static void line(const char *s){DWORD n,len=lstrlenA(s);WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),s,len,&n,NULL);while(*s&&Used<sizeof(Report))Report[Used++]=*s++;}
static void number(const char *s,DWORD v){char b[16];unsigned n=sizeof(b);b[--n]=0;b[--n]='\n';b[--n]='\r';do{b[--n]='0'+v%10;v/=10;}while(v);line(s);line(b+n);}
static void error(const char *stage){DWORD e=GetLastError();Failures++;line(stage);number("; Win32 error: ",e);}
void WINAPI mainCRTStartup(void){
 HANDLE report=INVALID_HANDLE_VALUE,f=INVALID_HANDLE_VALUE,t;DWORD n,i,spc,bps,free,total;char path[MAX_PATH];TOKEN_PRIVILEGES tp;
 for(i=0;i<sizeof(Report);i++)Report[i]=' ';
 SetConsoleTitleA("XWN physical Windows storage diagnostic v2");
 line("XWN-V2-STARTED\r\n");
 if(!GetWindowsDirectoryA(path,sizeof(path))){error("GetWindowsDirectory");goto hold;}
 line("Windows directory: ");line(path);line("\r\n");
 if(lstrcmpiA(path,"C:\\WINNT")){line("Unexpected Windows root; no diagnostic writes.\r\n");goto hold;}
 if(!GetDiskFreeSpaceA("C:\\",&spc,&bps,&free,&total)){error("GetDiskFreeSpace C");goto hold;}
 number("Sectors per cluster: ",spc);number("Bytes per sector: ",bps);number("Total clusters: ",total);number("Free clusters: ",free);
 if(spc!=128||bps!=512||total!=3693243){line("Unexpected volume geometry; no diagnostic writes.\r\n");goto hold;}
 report=CreateFileA("C:\\xwn-report-v2.txt",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
 if(report==INVALID_HANDLE_VALUE){error("Open pre-created report");goto hold;}
 if(GetFileSize(report,NULL)!=sizeof(Report)||!ReadFile(report,Check,sizeof(Report),&n,NULL)||n!=sizeof(Report)){error("Read pending report");goto hold;}
 for(i=0;i<sizeof(Report);i++)if(Check[i]!=(BYTE)(i<sizeof(Pending)-1?Pending[i]:' ')){line("Report seed differs; not overwriting.\r\n");goto hold;}
 line("Pre-created report opened and seed verified.\r\n");
 f=CreateFileA("C:\\xwn-physical.bin",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE){error("Open seed");goto finish;}
 if(GetFileSize(f,NULL)!=sizeof(Data)||!ReadFile(f,Data,sizeof(Data),&n,NULL)||n!=sizeof(Data)){error("Read seed");goto finish;}
 for(i=0;i<sizeof(Data);i++)if(Data[i]!=(BYTE)(i*37+(i>>8)+0x5a)){line("Seed byte mismatch.\r\n");Failures++;goto finish;}
 CloseHandle(f);f=INVALID_HANDLE_VALUE;line("Seed read verified: 65537 bytes.\r\n");
 f=CreateFileA("C:\\xwn-create-v2.bin",GENERIC_READ|GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
 if(f==INVALID_HANDLE_VALUE){error("Create new test file");goto finish;}
 for(i=0;i<sizeof(Data);i++)Data[i]^=0xa5;
 if(!WriteFile(f,Data,sizeof(Data),&n,NULL)||n!=sizeof(Data)||!FlushFileBuffers(f)){error("Write/flush new test file");goto finish;}
 CloseHandle(f);f=CreateFileA("C:\\xwn-create-v2.bin",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE||GetFileSize(f,NULL)!=sizeof(Check)||!ReadFile(f,Check,sizeof(Check),&n,NULL)||n!=sizeof(Check)){error("Reopen/read new test file");goto finish;}
 for(i=0;i<sizeof(Data);i++)if(Check[i]!=Data[i]){line("Reopened byte mismatch.\r\n");Failures++;goto finish;}
 line("New file write, flush and reopen verified: 65537 bytes.\r\n");
finish:
 if(f!=INVALID_HANDLE_VALUE){CloseHandle(f);f=INVALID_HANDLE_VALUE;}
 number("Failures: ",Failures);line(Failures?"XWN-V2-FAIL\r\n":"XWN-V2-PASS\r\n");
 line("Verifying saved report before normal restart.\r\n");
 if(SetFilePointer(report,0,NULL,FILE_BEGIN)!=0||!WriteFile(report,Report,sizeof(Report),&n,NULL)||n!=sizeof(Report)||!FlushFileBuffers(report)){error("Save/flush existing report");goto hold;}
 CloseHandle(report);report=CreateFileA("C:\\xwn-report-v2.txt",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(report==INVALID_HANDLE_VALUE||GetFileSize(report,NULL)!=sizeof(Report)||!ReadFile(report,Check,sizeof(Report),&n,NULL)||n!=sizeof(Report)){error("Reopen report");goto hold;}
 for(i=0;i<sizeof(Report);i++)if(Check[i]!=(BYTE)Report[i]){line("Saved report byte mismatch.\r\n");goto hold;}
 CloseHandle(report);report=INVALID_HANDLE_VALUE;
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&t)||!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){error("Restart privilege lookup");goto hold;}
 tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;SetLastError(0);
 if(!AdjustTokenPrivileges(t,FALSE,&tp,0,NULL,NULL)||GetLastError()!=0){error("Restart privilege enable");CloseHandle(t);goto hold;}
 CloseHandle(t);line("Report verified; normal restart in 15 seconds.\r\n");Sleep(15000);
 if(!ExitWindowsEx(EWX_REBOOT,0)){error("Restart request");goto hold;}
 ExitProcess(Failures);
hold:
 if(f!=INVALID_HANDLE_VALUE)CloseHandle(f);
 if(report!=INVALID_HANDLE_VALUE)CloseHandle(report);
 line("\r\nSTOPPED: Photograph this console window, then reboot.\r\n");
 Sleep(INFINITE);
}
