/* MIT. Sampling primitives and measured loop qualified by actualPC620. */
#include "suspend.h"
#include "memory.h"
#include "caller_plan.h"
typedef BOOL (WINAPI *ENUMFN)(HANDLE,HMODULE*,DWORD,LPDWORD);
typedef BOOL (WINAPI *INFOFN)(HANDLE,HMODULE,LPMODULEINFO,DWORD);
typedef DWORD (WINAPI *NAMEFN)(HANDLE,HMODULE,LPSTR,DWORD);
typedef struct {DWORD base,size;char name[MAX_PATH];} MOD;
typedef struct {DWORD tick,eip,esp,ebp,cs,hold;SR619 balance;DWORD codeok,stackok;BYTE code[32],stack[64],caller[64];DWORD caller_address,caller_ok,target_address,target_ok,target;} SAMPLE;
typedef struct {HANDLE thread,process;CONTEXT c;SAMPLE *sample;} CALL;
static SAMPLE samples[512];static MOD mods[2][128];static DWORD modn[2];
static SU619 susp(void*p){return SuspendThread(((CALL*)p)->thread);}
static SU619 resu(void*p){return ResumeThread(((CALL*)p)->thread);}
static BOOL memory627(HANDLE p,DWORD address,BYTE *data,DWORD count,BOOL code){
 MEMORY_BASIC_INFORMATION mi;SIZE_T got=0;
 if(VirtualQueryEx(p,(LPCVOID)address,&mi,sizeof(mi))!=sizeof(mi))return FALSE;
 if(!readable627(address,count,(DWORD)mi.BaseAddress,mi.RegionSize,mi.State,mi.Protect,code))return FALSE;
 return ReadProcessMemory(p,(LPCVOID)address,data,count,&got)&&got==count;
}
static DWORD little628(const BYTE *p){return (DWORD)p[0]|((DWORD)p[1]<<8)|((DWORD)p[2]<<16)|((DWORD)p[3]<<24);}
static void caller628(CALL*c){
 DWORD i,base=0,ret;int off;SAMPLE*s=c->sample;
 s->caller_address=s->caller_ok=s->target_address=s->target_ok=s->target=0;
 if(!s->codeok||!s->stackok)return;
 for(i=0;i<modn[0];i++)if(lstrcmpiA(mods[0][i].name,"C:\\WINNT\\system32\\winmm.dll")==0)base=mods[0][i].base;
 if(!base||c->c.Eip<base)return;
 off=timer_offset628(c->c.Eip-base);if(off<0||off>60)return;
 if(c->c.Eip-base>=0x7bfd&&little628(s->stack+off-20)!=base+0x7bf6)return;
 ret=little628(s->stack+off);if(ret<32||ret>0xffffffffu-32)return;
 s->caller_address=ret-32;s->caller_ok=memory627(c->process,s->caller_address,s->caller,64,TRUE);
 if(!s->caller_ok)return;
 if(s->caller[26]==0xff&&s->caller[27]==0x15){
  s->target_address=little628(s->caller+28);
  s->target_ok=memory627(c->process,s->target_address,(BYTE*)&s->target,4,FALSE);
 }
}
static int ctxt(void*p){CALL*c=p;
 if(!GetThreadContext(c->thread,&c->c))return 0;
 c->sample->codeok=memory627(c->process,c->c.Eip,c->sample->code,32,TRUE);
 c->sample->stackok=memory627(c->process,c->c.Esp,c->sample->stack,64,FALSE);
 caller628(c);
 return 1;
}
static BOOL memoryrow627(const char *tag,DWORD id,DWORD index,DWORD address,DWORD ok,BYTE *data,DWORD count){
 char buf[240];DWORD i,n;static const char hex[]="0123456789abcdef";
 n=wsprintfA(buf,"%s %lu %lu %08lx %lu ",tag,id,index,address,ok);
 if(ok)for(i=0;i<count;i++){buf[n++]=hex[data[i]>>4];buf[n++]=hex[data[i]&15];}
 else buf[n++]='-';
 buf[n++]='\r';buf[n++]='\n';buf[n]=0;return text(buf);
}
static BOOL profile_modules(HANDLE p,DWORD set){
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

static BOOL profile_game(HANDLE process,HANDLE thread,DWORD pid,DWORD tid){
 const DWORD id=4;PROCESS_INFORMATION pi;DWORD i,j,n=0,rng=0x6190123u;
 SNAP a,b,oa,ob;FILETIME ct,et,kt,ut,tcs,tes,tks,tus,tce,tee,tke,tue;CALL call;char buf[400],hc[17],hk[17],hu[17];
 zero(&pi,sizeof(pi));pi.hProcess=process;pi.hThread=thread;pi.dwProcessId=pid;pi.dwThreadId=tid;
 if(!profile_modules(pi.hProcess,0)||!GetProcessTimes(pi.hProcess,&ct,&et,&kt,&ut))goto end;

 if(lstrcmpiA(mods[0][0].name,"C:\\xwn628-kit\\game\\RCT.EXE")!=0||!threadrow("THREAD_READY",id,pi.hThread))goto end;

 hex64(hc,ft(ct));wsprintfA(buf,"IDENTITY %lu %lu %lu %lu %s\r\n",id,pi.dwProcessId,pi.dwThreadId,GetCurrentProcessId(),hc);
 if(!text(buf))goto end;

 if(!GetThreadTimes(pi.hThread,&tcs,&tes,&tks,&tus)||!snap(GetCurrentProcess(),&oa,TRUE)||!snap(pi.hProcess,&a,TRUE)||!mark("START",id+1,&a))goto end;

 while(GetTickCount()-a.tick<20000){
  if(WaitForSingleObject(pi.hProcess,0)!=WAIT_TIMEOUT||n>=512)goto end;

  if(id>=4){
   SAMPLE*s=&samples[n];DWORD start;
   zero(&call,sizeof(call));call.thread=pi.hThread;call.process=pi.hProcess;call.sample=s;call.c.ContextFlags=CONTEXT_CONTROL|CONTEXT_INTEGER;
   start=GetTickCount();
   if(!sample619(&call,susp,ctxt,resu,&s->balance)){text("SUSPEND_FAIL\r\n");goto end;
}
   s->hold=GetTickCount()-start;s->tick=start;s->eip=call.c.Eip;s->esp=call.c.Esp;s->ebp=call.c.Ebp;s->cs=call.c.SegCs;
   if((s->cs&3)!=3||!s->eip||!s->esp||s->hold>1000)goto end;

  }
  n++;rng=rng*1664525u+1013904223u;Sleep(50+(rng>>24)%64);
 }
 if(!snap(pi.hProcess,&b,TRUE)||!snap(GetCurrentProcess(),&ob,TRUE)||!GetThreadTimes(pi.hThread,&tce,&tee,&tke,&tue)||!mark("END",id+1,&b))goto end;

 if(!profile_modules(pi.hProcess,1)||modn[0]!=modn[1])goto end;

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
 if(!text(buf)||!memoryrow627("CODE",id,i,s->eip,s->codeok,s->code,32)||!memoryrow627("STACK",id,i,s->esp,s->stackok,s->stack,64)||!memoryrow627("CALLSITE",id,i,s->caller_address,s->caller_ok,s->caller,64)||!memoryrow627("TARGET",id,i,s->target_address,s->target_ok,(BYTE*)&s->target,4))goto end;

 }

 return text("PROFILE_DONE\r\n");
end:
 return FALSE;
}
