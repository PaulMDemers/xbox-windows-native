/* MIT. Original direct/traced identity and timed-work coordination control. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <psapi.h>
#include "counter.h"
typedef DWORD (WINAPI *NAMEFN)(HANDLE,HMODULE,LPSTR,DWORD);
static SNAP sample_subject[512],sample_tracer[512];
static BOOL run(DWORD which){
 STARTUPINFOA si;PROCESS_INFORMATION pi;HANDLE ev[4]={0,0,0,0},phase[2]={0,0},subject=0,pf;
 const char* names[4]={"READY","GO","DONE","RELEASE"};
 DWORD j,n=0,id[4],got,wait,sc=99,tc=99;FILETIME ct,et,kt,ut;char name[200],cmd[80],image[MAX_PATH],line[240];
 SNAP a,b,ta,tb,oa,ob;BOOL ok=FALSE,identityread;NAMEFN namefn;
 zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
 zero(&ta,sizeof(ta));zero(&tb,sizeof(tb));
 for(j=0;j<4;j++){
  wsprintfA(name,"XWN616_%s_%lu",names[j],which);SetLastError(0);
  ev[j]=CreateEventA(0,TRUE,FALSE,name);if(!ev[j]||GetLastError()==ERROR_ALREADY_EXISTS)goto finish;
 }
 if(!which){
  SetLastError(0);phase[0]=CreateEventA(0,TRUE,FALSE,"XWN616PhaseRequest");
  if(!phase[0]||GetLastError()==ERROR_ALREADY_EXISTS)goto finish;
  SetLastError(0);phase[1]=CreateEventA(0,TRUE,FALSE,"XWN616PhaseAck");
  if(!phase[1]||GetLastError()==ERROR_ALREADY_EXISTS)goto finish;
 }
 lstrcpyA(cmd,which?"trace616":"subject616 0");
 if(!CreateProcessA(which?"C:\\xwn616-kit\\trace.exe":"C:\\xwn616-kit\\subject.exe",cmd,0,0,FALSE,0,0,"C:\\xwn616-kit",&si,&pi))goto finish;
 if(WaitForSingleObject(ev[0],30000)!=WAIT_OBJECT_0)goto finish;
 if(which){
  pf=CreateFileA("C:\\xwn616\\identity.bin",GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,0,0);
  if(pf==INVALID_HANDLE_VALUE)goto finish;
  identityread=GetFileSize(pf,0)==sizeof(id)&&ReadFile(pf,id,sizeof(id),&got,0)&&got==sizeof(id);CloseHandle(pf);
  if(!identityread||id[1]!=pi.dwProcessId||!id[0]||id[0]==id[1])goto finish;
 }else{
  if(!GetProcessTimes(pi.hProcess,&ct,&et,&kt,&ut))goto finish;
  id[0]=pi.dwProcessId;id[1]=0;id[2]=ct.dwLowDateTime;id[3]=ct.dwHighDateTime;
 }
 ok=FALSE;
 if(id[0]==GetCurrentProcessId())goto finish;
 subject=OpenProcess(PROCESS_QUERY_INFORMATION|PROCESS_VM_READ|SYNCHRONIZE,FALSE,id[0]);
 if(!subject||!GetProcessTimes(subject,&ct,&et,&kt,&ut)||ct.dwLowDateTime!=id[2]||ct.dwHighDateTime!=id[3])goto finish;
 namefn=(NAMEFN)GetProcAddress(GetModuleHandleA("psapi.dll"),"GetModuleFileNameExA");if(!namefn)goto finish;
 zero(image,sizeof(image));got=namefn(subject,0,image,sizeof(image));
 if(!got||got>=sizeof(image)||lstrcmpiA(image,"C:\\xwn616-kit\\subject.exe")!=0)goto finish;
 wsprintfA(line,"IDENTITY %lu %lu %lu %lu %lu %lu\r\n",which+1,id[0],id[1],GetCurrentProcessId(),id[2],id[3]);
 if(!text(line))goto finish;
 if(!snap(GetCurrentProcess(),&oa,TRUE)||(which&&!snap(pi.hProcess,&ta,TRUE))||
    !snap(subject,&a,TRUE)||!mark("START",which+1,&a)||!SetEvent(ev[1]))goto finish;
 do{
  wait=WaitForSingleObject(subject,100);
  if(wait!=WAIT_TIMEOUT||n>=512||!snap(subject,&sample_subject[n],TRUE)||
     (which&&!snap(pi.hProcess,&sample_tracer[n],TRUE)))goto finish;
  n++;
 }while((DWORD)(sample_subject[n-1].tick-a.tick)<20000);
 if(!snap(subject,&b,TRUE)||(which&&!snap(pi.hProcess,&tb,TRUE))||
    !snap(GetCurrentProcess(),&ob,TRUE)||!mark("END",which+1,&b))goto finish;
 if(WaitForSingleObject(ev[2],0)!=WAIT_OBJECT_0)goto finish;
 if(!row("SUBJECT_START",which+1,0,&a)||!row("SUBJECT_END",which+1,0,&b)||
    !row("OBSERVER_START",which+1,0,&oa)||!row("OBSERVER_END",which+1,0,&ob))goto finish;
 if(which&&(!row("TRACER_START",2,0,&ta)||!row("TRACER_END",2,0,&tb)))goto finish;
 for(j=0;j<n;j++){
  if(!row("SUBJECT_SAMPLE",which+1,j,&sample_subject[j])||
     (which&&!row("TRACER_SAMPLE",2,j,&sample_tracer[j])))goto finish;
 }
 if(!SetEvent(ev[3])||WaitForSingleObject(subject,5000)!=WAIT_OBJECT_0||
    !GetExitCodeProcess(subject,&sc)||sc!=0||WaitForSingleObject(pi.hProcess,5000)!=WAIT_OBJECT_0||
    !GetExitCodeProcess(pi.hProcess,&tc)||tc!=0)goto finish;
 wsprintfA(line,"CASE %lu %lu %lu %lu\r\n",which+1,n,sc,tc);ok=text(line);
finish:
 if(pi.hProcess){
  if(WaitForSingleObject(pi.hProcess,0)!=WAIT_OBJECT_0){
   text("OWNED_TERMINATE\r\n");TerminateProcess(pi.hProcess,96);WaitForSingleObject(pi.hProcess,5000);
  }
  CloseHandle(pi.hThread);CloseHandle(pi.hProcess);
 }
 if(subject)CloseHandle(subject);
 for(j=0;j<4;j++)if(ev[j])CloseHandle(ev[j]);
 for(j=0;j<2;j++)if(phase[j])CloseHandle(phase[j]);
 return ok;
}
void WINAPI mainCRTStartup(void){
 SNAP a,b;BOOL ok=FALSE;HANDLE token;TOKEN_PRIVILEGES tp;
 if(!CreateDirectoryA("C:\\xwn616",0)||!init("C:\\xwn616\\sampler.txt")||!serial_open())ExitProcess(90);
 if(!snap(GetCurrentProcess(),&a,TRUE)||!mark("START",0,&a))goto end;
 Sleep(5000);
 if(!snap(GetCurrentProcess(),&b,TRUE)||!mark("END",0,&b)||
    !row("SLEEP_START",0,0,&a)||!row("SLEEP_END",0,0,&b))goto end;
 ok=run(0)&&run(1);
end:
 if(!text(ok?"CONTROL_PASS\r\n":"CONTROL_FAIL\r\n"))ExitProcess(91);
 CloseHandle(serialh);
 zero(&tp,sizeof(tp));tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(92);
 if(!LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(93);
 SetLastError(0);if(!AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)||GetLastError())ExitProcess(94);
 CloseHandle(token);
 if(!text("RESTART\r\n"))ExitProcess(95);
 CloseHandle(logh);
 if(!ExitWindowsEx(EWX_REBOOT,0))ExitProcess(97);
 ExitProcess(ok?0:1);
}
