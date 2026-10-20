/* MIT. Bounded external main-thread location sampling qualification. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <psapi.h>
#include "counter.h"
#include "suspend.h"
typedef BOOL (WINAPI *ENUMFN)(HANDLE,HMODULE*,DWORD,LPDWORD);
typedef BOOL (WINAPI *INFOFN)(HANDLE,HMODULE,LPMODULEINFO,DWORD);
typedef DWORD (WINAPI *NAMEFN)(HANDLE,HMODULE,LPSTR,DWORD);
typedef struct {DWORD base,size;char name[MAX_PATH];} MOD;
typedef struct {DWORD tick,eip,esp,ebp,cs,hold;SR619 balance;} SAMPLE;
typedef struct {HANDLE thread;CONTEXT c;} CALL;
static SAMPLE samples[512];static MOD mods[2][128];static DWORD modn[2];
static SU619 susp(void*p){return SuspendThread(((CALL*)p)->thread);}
static SU619 resu(void*p){return ResumeThread(((CALL*)p)->thread);}
static int ctxt(void*p){CALL*c=p;
 return GetThreadContext(c->thread,&c->c)!=0;}
static BOOL modules(HANDLE p,DWORD set){
 HMODULE m[128],lib=GetModuleHandleA("psapi.dll");DWORD bytes,i,j;MODULEINFO mi;
 ENUMFN en=(ENUMFN)GetProcAddress(lib,"EnumProcessModules");INFOFN in=(INFOFN)GetProcAddress(lib,"GetModuleInformation");
 NAMEFN na=(NAMEFN)GetProcAddress(lib,"GetModuleFileNameExA");
 if(!en||!in||!na||!en(p,m,sizeof(m),&bytes)||!bytes||bytes>sizeof(m)||bytes%sizeof(HMODULE))return FALSE;
 modn[set]=bytes/sizeof(HMODULE);
 for(i=0;i<modn[set];i++){
  MOD*t=&mods[set][i];DWORD count;
  if(!in(p,m[i],&mi,sizeof(mi))||!mi.SizeOfImage)return FALSE;
  t->base=(DWORD)mi.lpBaseOfDll;t->size=mi.SizeOfImage;
  if(t->base>0xffffffffu-t->size)return FALSE;
  count=na(p,m[i],t->name,sizeof(t->name));
 if(!count||count>=sizeof(t->name))return FALSE;
  for(j=0;j<i;j++)if(t->base<mods[set][j].base+mods[set][j].size&&mods[set][j].base<t->base+t->size)return FALSE;
 }
 return TRUE;
}
static BOOL threadrow(const char*tag,DWORD id,HANDLE h){
 FILETIME ct,et,kt,ut;char c[17],e[17],k[17],u[17],buf[180];
 if(!GetThreadTimes(h,&ct,&et,&kt,&ut))return FALSE;
 hex64(c,ft(ct));hex64(e,ft(et));hex64(k,ft(kt));hex64(u,ft(ut));
 wsprintfA(buf,"%s %lu %s %s %s %s\r\n",tag,id,c,e,k,u);
 return text(buf);
}
static BOOL run(DWORD id){
 STARTUPINFOA si;PROCESS_INFORMATION pi;HANDLE ready=0,release=0;BOOL ok=FALSE;DWORD i,j,n=0,code=99,rng=0x6190123u;
 SNAP a,b,oa,ob;FILETIME ct,et,kt,ut,tcs,tes,tks,tus,tce,tee,tke,tue;CALL call;char cmd[100],buf[400],hc[17],hk[17],hu[17];
 zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
 SetLastError(0);ready=CreateEventA(0,TRUE,FALSE,"XWN623_READY");
 if(!ready||GetLastError()==ERROR_ALREADY_EXISTS)goto end;

 SetLastError(0);release=CreateEventA(0,TRUE,FALSE,"XWN623_RELEASE");
 if(!release||GetLastError()==ERROR_ALREADY_EXISTS)goto end;

 wsprintfA(cmd,"subject619 %lu",id);
 if(!CreateProcessA("C:\\xwn623-kit\\subject.exe",cmd,0,0,FALSE,0,0,"C:\\xwn623-kit",&si,&pi))goto end;

 if(WaitForSingleObject(ready,15000)!=WAIT_OBJECT_0||!modules(pi.hProcess,0)||!GetProcessTimes(pi.hProcess,&ct,&et,&kt,&ut))goto end;

 if(lstrcmpiA(mods[0][0].name,"C:\\xwn623-kit\\subject.exe")!=0||!threadrow("THREAD_READY",id,pi.hThread))goto end;

 hex64(hc,ft(ct));wsprintfA(buf,"IDENTITY %lu %lu %lu %lu %s\r\n",id,pi.dwProcessId,pi.dwThreadId,GetCurrentProcessId(),hc);
 if(!text(buf))goto end;

 if(!GetThreadTimes(pi.hThread,&tcs,&tes,&tks,&tus)||!snap(GetCurrentProcess(),&oa,TRUE)||!snap(pi.hProcess,&a,TRUE)||!mark("START",id+1,&a))goto end;

 while(GetTickCount()-a.tick<20000){
  if(WaitForSingleObject(pi.hProcess,0)!=WAIT_TIMEOUT||n>=512)goto end;

  if(id>=4){
   SAMPLE*s=&samples[n];DWORD start;
   zero(&call,sizeof(call));call.thread=pi.hThread;call.c.ContextFlags=CONTEXT_CONTROL|CONTEXT_INTEGER;
   start=GetTickCount();
   if(!sample619(&call,susp,ctxt,resu,&s->balance)){text("SUSPEND_FAIL\r\n");goto end;
}
   s->hold=GetTickCount()-start;s->tick=start;s->eip=call.c.Eip;s->esp=call.c.Esp;s->ebp=call.c.Ebp;s->cs=call.c.SegCs;
   if((s->cs&3)!=3||!s->eip||!s->esp||s->hold>1000)goto end;

  }
  n++;rng=rng*1664525u+1013904223u;Sleep(50+(rng>>24)%64);
 }
 if(!snap(pi.hProcess,&b,TRUE)||!snap(GetCurrentProcess(),&ob,TRUE)||!GetThreadTimes(pi.hThread,&tce,&tee,&tke,&tue)||!mark("END",id+1,&b))goto end;

 if(!modules(pi.hProcess,1)||modn[0]!=modn[1])goto end;

 if(!SetEvent(release)||WaitForSingleObject(pi.hProcess,5000)!=WAIT_OBJECT_0||!GetExitCodeProcess(pi.hProcess,&code)||code)goto end;

 for(i=0;i<modn[0];i++){
  MOD*m=&mods[0][i];BOOL found=FALSE;
  for(j=0;j<modn[1];j++)if(m->base==mods[1][j].base&&m->size==mods[1][j].size&&lstrcmpiA(m->name,mods[1][j].name)==0)found=TRUE;
  if(!found)goto end;

  wsprintfA(buf,"MODULE %lu %08lx %08lx %s\r\n",id,m->base,m->size,m->name);
 if(!text(buf))goto end;

 }
 if(!row("SUBJECT_START",id,0,&a)||!row("SUBJECT_END",id,n,&b)||!row("OBSERVER_START",id,0,&oa)||!row("OBSERVER_END",id,n,&ob))goto end;

 hex64(hc,ft(tcs));hex64(hk,ft(tks));hex64(hu,ft(tus));wsprintfA(buf,"THREAD_START %lu %s %s %s\r\n",id,hc,hk,hu);
 if(!text(buf))goto end;

 hex64(hc,ft(tce));hex64(hk,ft(tke));hex64(hu,ft(tue));wsprintfA(buf,"THREAD_END %lu %s %s %s\r\n",id,hc,hk,hu);
 if(!text(buf))goto end;

 if(id>=4)for(i=0;i<n;i++){
  SAMPLE*s=&samples[i];BOOL found=FALSE;
  for(j=0;j<modn[0];j++)if(s->eip>=mods[0][j].base&&s->eip-mods[0][j].base<mods[0][j].size)found=TRUE;
  if(!found)goto end;

  wsprintfA(buf,"SAMPLE %lu %lu %lu %08lx %08lx %08lx %08lx %lu %lu %lu\r\n",id,i,s->tick,s->eip,s->esp,s->ebp,s->cs,s->hold,s->balance.prior,s->balance.resumed);
 if(!text(buf))goto end;

 }

 wsprintfA(buf,"CASE %lu %lu %lu\r\n",id,n,code);ok=text(buf);
end:
 if(pi.hProcess){if(WaitForSingleObject(pi.hProcess,0)!=WAIT_OBJECT_0){text("OWNED_TERMINATE\r\n");TerminateProcess(pi.hProcess,96);WaitForSingleObject(pi.hProcess,5000);}CloseHandle(pi.hThread);
 CloseHandle(pi.hProcess);}
 if(ready)CloseHandle(ready);
 if(release)CloseHandle(release);
 return ok;
}
void WINAPI mainCRTStartup(void){
 DWORD id;BOOL ok=FALSE;SNAP a,b;HANDLE token;TOKEN_PRIVILEGES tp;
 if(!CreateDirectoryA("C:\\xwn623",0)||!init("C:\\xwn623\\sampler.txt")||!serial_open())ExitProcess(90);
 if(!SetThreadPriority(GetCurrentThread(),THREAD_PRIORITY_HIGHEST))goto end;

 if(!snap(GetCurrentProcess(),&a,TRUE)||!mark("START",0,&a))goto end;

 Sleep(5000);
 if(!snap(GetCurrentProcess(),&b,TRUE)||!mark("END",0,&b)||!row("SLEEP_START",0,0,&a)||!row("SLEEP_END",0,0,&b))goto end;

 for(id=0;id<8;id++){if(!run(id))goto end;
}
 ok=TRUE;
end:
 if(!text(ok?"CONTROL_PASS\r\n":"CONTROL_FAIL\r\n"))ExitProcess(91);
 CloseHandle(serialh);zero(&tp,sizeof(tp));tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(92);
 if(!LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(93);
 SetLastError(0);
 if(!AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)||GetLastError())ExitProcess(94);
 CloseHandle(token);
 if(!text("RESTART\r\n"))ExitProcess(95);
 CloseHandle(logh);
 if(!ExitWindowsEx(EWX_REBOOT,0))ExitProcess(97);
 ExitProcess(ok?0:1);
}
