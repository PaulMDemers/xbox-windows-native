/* Read-only high-LBA payload verification on an owned emulator fixture. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log;
static void line(const char *s){DWORD n;WriteFile(Log,s,lstrlenA(s),&n,NULL);FlushFileBuffers(Log);}
static void number(const char *s,DWORD v){char b[16];unsigned n=sizeof(b);b[--n]=0;b[--n]='\n';b[--n]='\r';do{b[--n]='0'+v%10;v/=10;}while(v);line(s);line(b+n);}
void WINAPI mainCRTStartup(void){
 HANDLE f;BYTE b[1024];DWORD at=0,n,i,want,fail=0,spc,bps,free,total;
 Log=CreateFileA("C:\\xwn-large.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
 line("XWN native Windows high-LBA FATX read\r\n");
 if(GetDiskFreeSpaceA("C:\\",&spc,&bps,&free,&total)){
  number("Sectors per cluster: ",spc);number("Bytes per sector: ",bps);number("Total clusters: ",total);
  if(spc!=128||bps!=512)fail++;
 }else{number("GetDiskFreeSpace error: ",GetLastError());fail++;}
 f=CreateFileA("C:\\xwn-high.bin",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE){number("File open error: ",GetLastError());fail++;goto done;}
 if(GetFileSize(f,NULL)!=4097){fail++;goto close;}
 while(at<4097){
  want=4097-at;if(want>sizeof(b))want=sizeof(b);
  if(!ReadFile(f,b,want,&n,NULL)||n!=want){number("Read error: ",GetLastError());fail++;goto close;}
  for(i=0;i<n;i++)if(b[i]!=(BYTE)((at+i)*37+((at+i)>>8)+0x5a)){number("Mismatch offset: ",at+i);fail++;goto close;}
  at+=n;
 }
 if(!ReadFile(f,b,1,&n,NULL)||n!=0){fail++;goto close;}
 if(SetFilePointer(f,2041,NULL,FILE_BEGIN)!=2041||!ReadFile(f,b,31,&n,NULL)||n!=31){fail++;goto close;}
 for(i=0;i<n;i++)if(b[i]!=(BYTE)((2041+i)*37+((2041+i)>>8)+0x5a))fail++;
close:CloseHandle(f);
done:number("Bytes verified: ",at);number("Failures: ",fail);
 if(!fail)line("XWN-LARGE-PASS: native Windows high-LBA FATX read verified\r\n");
 CloseHandle(Log);ExitProcess(fail);
}
