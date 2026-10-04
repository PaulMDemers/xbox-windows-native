/* Bounded file API checks on a private emulator fixture; no raw disk access. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log;
static DWORD Failures;
static BYTE Data[131073], Readback[131073];
static void line(const char *s) {
 DWORD n; WriteFile(Log,s,lstrlenA(s),&n,NULL); FlushFileBuffers(Log);
 WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),s,lstrlenA(s),&n,NULL);
}
static void number(const char *s,DWORD v) {
 char b[16];unsigned n=sizeof(b);b[--n]=0;b[--n]='\n';b[--n]='\r';
 do {b[--n]='0'+v%10;v/=10;}while(v);line(s);line(b+n);
}
static void check(BOOL ok,const char *name) {
 if(!ok){++Failures;line("FAIL: ");number("Win32 error: ",GetLastError());}
 else line("PASS: ");line(name);line("\r\n");
}
static BOOL compare(DWORD count) {
 DWORD i;for(i=0;i<count;++i)if(Readback[i]!=Data[i])return FALSE;return TRUE;
}
void WINAPI mainCRTStartup(void) {
 DWORD max=0,flags=0,serial=0,i,n;HANDLE f;BOOL ok;WIN32_FIND_DATAA fd;
 char upper42[64]="C:\\xwnfstest\\",renamed42[64]="C:\\xwnfstest\\";
 char fs[32],p42[64]="C:\\xwnfstest\\",p43[64]="C:\\xwnfstest\\";
 Log=CreateFileA("C:\\xwn-fs.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
 line("XWN FATX file API test\r\n");
 ok=GetVolumeInformationA("C:\\",NULL,0,&serial,&max,&flags,fs,sizeof(fs));
 check(ok,"GetVolumeInformation");number("Maximum component: ",max);number("Flags: ",flags);
 check(ok && lstrcmpiA(fs,"FATX")==0,"Filesystem name FATX");
 check(ok && max==42,"42-byte component limit advertised");
 check(ok && (flags&FILE_CASE_PRESERVED_NAMES) && !(flags&FILE_UNICODE_ON_DISK),"OEM case-preserved capabilities");
 check(CreateDirectoryA("C:\\xwnfstest",NULL),"Create test directory");
 check(CreateDirectoryA("C:\\xwnfstest\\sub",NULL),"Create child directory");
 for(i=0;i<42;++i)p42[13+i]='a';p42[55]=0;
 for(i=0;i<43;++i)p43[13+i]='b';p43[56]=0;
 f=CreateFileA(p42,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 check(f!=INVALID_HANDLE_VALUE,"42-byte ASCII name accepted");if(f!=INVALID_HANDLE_VALUE)CloseHandle(f);
 f=CreateFileA(p43,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 check(f==INVALID_HANDLE_VALUE,"43-byte ASCII name rejected");if(f!=INVALID_HANDLE_VALUE){CloseHandle(f);DeleteFileA(p43);}
 for(i=0;i<sizeof(Data);++i)Data[i]=(BYTE)((i*37u)^(i>>8));
 f=CreateFileA("C:\\xwnfstest\\MiXeD.bin",GENERIC_WRITE|GENERIC_READ,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 check(f!=INVALID_HANDLE_VALUE,"Create mixed-case data file");
 if(f!=INVALID_HANDLE_VALUE){
  n=0;check(WriteFile(f,Data,sizeof(Data),&n,NULL)&&n==sizeof(Data),"Write 128 KiB plus one byte");
  check(FlushFileBuffers(f),"Flush data");CloseHandle(f);
 }
 f=CreateFileA("C:\\XWNFSTEST\\mixed.BIN",GENERIC_WRITE|GENERIC_READ,0,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 check(f!=INVALID_HANDLE_VALUE,"Case-insensitive reopen");
 if(f!=INVALID_HANDLE_VALUE){
  n=0;check(ReadFile(f,Readback,sizeof(Readback),&n,NULL)&&n==sizeof(Readback)&&compare(n),"Reopened full data comparison");
  check(SetFilePointer(f,65537,NULL,FILE_BEGIN)==65537 && SetEndOfFile(f),"Shrink at cluster-crossing boundary");
  check(GetFileSize(f,NULL)==65537,"Shrunk size");
  n=0;check(WriteFile(f,Data+65537,sizeof(Data)-65537,&n,NULL)&&n==sizeof(Data)-65537,"Regrow with explicit data");
  check(FlushFileBuffers(f),"Flush regrown file");CloseHandle(f);
 }
 check(MoveFileA("C:\\xwnfstest\\MiXeD.bin","C:\\xwnfstest\\sub\\Moved.bin"),"Rename across directories");
 f=CreateFileA("C:\\xwnfstest\\sub\\Moved.bin",GENERIC_READ,0,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 check(f!=INVALID_HANDLE_VALUE,"Open renamed file");
 if(f!=INVALID_HANDLE_VALUE){n=0;check(ReadFile(f,Readback,sizeof(Readback),&n,NULL)&&n==sizeof(Readback)&&compare(n),"Renamed regrown data comparison");CloseHandle(f);}
 check(DeleteFileA("C:\\xwnfstest\\sub\\Moved.bin"),"Delete data file");
 for(i=0;i<42;++i){upper42[13+i]='A';renamed42[13+i]='c';}upper42[55]=0;renamed42[55]=0;
 check(MoveFileExA(p42,upper42,0),"Case-only rename of 42-byte name");
 f=FindFirstFileA(upper42,&fd);check(f!=INVALID_HANDLE_VALUE && lstrcmpA(fd.cFileName,upper42+13)==0,"42-byte case change persisted in directory");if(f!=INVALID_HANDLE_VALUE)FindClose(f);
 check(DeleteFileA(upper42),"Delete boundary-length file");
 f=CreateFileA("C:\\xwnfstest\\short.bin",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 check(f!=INVALID_HANDLE_VALUE,"Create rename source");
 if(f!=INVALID_HANDLE_VALUE){n=0;check(WriteFile(f,Data,sizeof(Data),&n,NULL)&&n==sizeof(Data),"Write rename source");CloseHandle(f);}
 check(MoveFileA("C:\\xwnfstest\\short.bin",renamed42),"Same-directory rename to 42-byte name");
 f=FindFirstFileA(renamed42,&fd);check(f!=INVALID_HANDLE_VALUE && lstrcmpA(fd.cFileName,renamed42+13)==0,"42-byte rename persisted in directory");if(f!=INVALID_HANDLE_VALUE)FindClose(f);
 f=CreateFileA(renamed42,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 check(f!=INVALID_HANDLE_VALUE,"Reopen 42-byte renamed file");
 if(f!=INVALID_HANDLE_VALUE){n=0;check(ReadFile(f,Readback,sizeof(Readback),&n,NULL)&&n==sizeof(Readback)&&compare(n),"42-byte renamed data comparison");CloseHandle(f);}
 check(DeleteFileA(renamed42),"Delete 42-byte renamed file");
 check(RemoveDirectoryA("C:\\xwnfstest\\sub"),"Remove child directory");
 check(RemoveDirectoryA("C:\\xwnfstest"),"Remove test directory");
 number("Failures: ",Failures);CloseHandle(Log);ExitProcess(Failures);
}
