/* Clean-shutdown persistence check on a private emulator disk. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log;
static DWORD Failures;
static const char Key[]="SOFTWARE\\XWN\\PersistenceProbe";
static void line(const char *s){DWORD n;WriteFile(Log,s,lstrlenA(s),&n,NULL);FlushFileBuffers(Log);}
static void number(const char *s,DWORD v){char b[16];unsigned n=sizeof(b);b[--n]=0;b[--n]='\n';b[--n]='\r';do{b[--n]='0'+v%10;v/=10;}while(v);line(s);line(b+n);}
static void fail(const char *s){++Failures;line(s);line("\r\n");}
void WINAPI mainCRTStartup(void){
 HKEY h=NULL;HANDLE f=INVALID_HANDLE_VALUE;LONG status;DWORD count=0,type=0,size=4,n=0,disposition,words[3],next=0;
 BOOL haveRegistry=FALSE,haveFile=FALSE;
 Log=CreateFileA("C:\\xwn-persist.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
 line("XWN clean-shutdown persistence probe\r\n");
 status=RegOpenKeyExA(HKEY_LOCAL_MACHINE,Key,0,KEY_QUERY_VALUE,&h);
 if(status==ERROR_SUCCESS){
  status=RegQueryValueExA(h,"Count",NULL,&type,(BYTE*)&count,&size);RegCloseKey(h);h=NULL;
  if(status!=ERROR_SUCCESS||type!=REG_DWORD||size!=4){fail("Invalid existing registry counter");goto done;}
  haveRegistry=TRUE;
 }else if(status!=ERROR_FILE_NOT_FOUND){number("Registry open error: ",status);fail("Registry open failed");goto done;}
 f=CreateFileA("C:\\xwn-persist.bin",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f!=INVALID_HANDLE_VALUE){
  haveFile=TRUE;
  if(GetFileSize(f,NULL)!=sizeof(words)||!ReadFile(f,words,sizeof(words),&n,NULL)||n!=sizeof(words)||words[0]!=0x58574e50||words[2]!=(words[1]^0xa55a1234)){fail("Invalid existing file counter");goto done;}
  CloseHandle(f);f=INVALID_HANDLE_VALUE;
 }else if(GetLastError()!=ERROR_FILE_NOT_FOUND){fail("Counter file open failed");goto done;}
 if(haveRegistry!=haveFile||(haveFile&&words[1]!=count)||count>100){fail("Registry and file counters disagree");goto done;}
 number("Previous count: ",count);next=count+1;
 status=RegCreateKeyExA(HKEY_LOCAL_MACHINE,Key,0,NULL,REG_OPTION_NON_VOLATILE,KEY_SET_VALUE|KEY_QUERY_VALUE,NULL,&h,&disposition);
 if(status!=ERROR_SUCCESS){fail("Counter key creation failed");goto done;}
 words[0]=0x58574e50;words[1]=next;words[2]=next^0xa55a1234;
 f=CreateFileA("C:\\xwn-persist.bin",GENERIC_WRITE,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
 if(f==INVALID_HANDLE_VALUE||!WriteFile(f,words,sizeof(words),&n,NULL)||n!=sizeof(words)||!FlushFileBuffers(f)){fail("Counter file write/flush failed");goto done;}
 CloseHandle(f);f=INVALID_HANDLE_VALUE;
 if(RegSetValueExA(h,"Count",0,REG_DWORD,(BYTE*)&next,sizeof(next))!=ERROR_SUCCESS||RegFlushKey(h)!=ERROR_SUCCESS){fail("Counter registry write/flush failed");goto done;}
 number("Written count: ",next);line("File and registry explicitly flushed\r\n");
 done:
 if(f!=INVALID_HANDLE_VALUE)CloseHandle(f);if(h)RegCloseKey(h);
 number("Failures: ",Failures);CloseHandle(Log);ExitProcess(Failures);
}
