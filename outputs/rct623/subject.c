/* MIT. Original timer calls with busy and paced polling. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <mmsystem.h>
void WINAPI mainCRTStartup(void){
 const char*cmd=GetCommandLineA();DWORD n=lstrlenA(cmd),id,mode,w,start=0,end=0,calls=0,changes=0,first=0,last=0,now,i,batch;
 HANDLE ready=0,release=0,file=INVALID_HANDLE_VALUE;char path[180],buf[400];BOOL ok=FALSE;
 if(!n||cmd[n-1]<'0'||cmd[n-1]>'7')ExitProcess(80);
 id=cmd[n-1]-'0';mode=id%4;
 wsprintfA(path,"C:\\xwn623\\subject%lu.txt",id);
 file=CreateFileA(path,GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
 if(file==INVALID_HANDLE_VALUE)ExitProcess(81);
 ready=OpenEventA(EVENT_MODIFY_STATE,FALSE,"XWN623_READY");
 release=OpenEventA(SYNCHRONIZE,FALSE,"XWN623_RELEASE");
 if(!ready||!release)goto end;
 start=GetTickCount();first=last=(mode<2?timeGetTime():GetTickCount());
 if(!SetEvent(ready))goto end;
 batch=(mode&1)?1:4096;
 while(WaitForSingleObject(release,0)==WAIT_TIMEOUT){
  if(GetTickCount()-start>40000)goto end;
  for(i=0;i<batch;i++){
   now=(mode<2?timeGetTime():GetTickCount());
   if(now-last>1000||calls==0xffffffffu)goto end;
   if(now!=last)changes++;
   last=now;calls++;
  }
  if(mode&1)Sleep(10);
 }
 end=GetTickCount();ok=calls>0&&changes>0;
end:
 wsprintfA(buf,"TIMER %lu MODE %lu PID %lu TID %lu CALLS %lu FIRST %lu LAST %lu CHANGES %lu START %lu END %lu PASS %lu\r\n",id,mode,GetCurrentProcessId(),GetCurrentThreadId(),calls,first,last,changes,start,end,(DWORD)ok);
 if(!WriteFile(file,buf,lstrlenA(buf),&w,0)||w!=(DWORD)lstrlenA(buf)||!FlushFileBuffers(file))ok=FALSE;
 if(ready)CloseHandle(ready);
 if(release)CloseHandle(release);
 CloseHandle(file);ExitProcess(ok?0:1);
}
