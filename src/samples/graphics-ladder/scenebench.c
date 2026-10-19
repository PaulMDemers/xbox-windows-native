/* SPDX-License-Identifier: MIT
 * Three bounded, separately owned scene.exe processes. Whole-process telemetry,
 * including capture I/O and display pauses, not FPS or an in-process leak test.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
typedef struct {DWORD cb,faults,peak_ws,ws,peak_paged,paged,peak_nonpaged,nonpaged,commit,peak_commit;} COUNTERS;
typedef char counters_size[(sizeof(COUNTERS)==40)?1:-1];
typedef BOOL (WINAPI *MEMORY_FN)(HANDLE,COUNTERS*,DWORD);
static HANDLE log_file=INVALID_HANDLE_VALUE;
static int io_error;
static void zero(void *v,DWORD n){BYTE *p=v;while(n--)*p++=0;}
static int put(HANDLE h,const char *s){DWORD n=(DWORD)lstrlenA(s),w=0;if(!WriteFile(h,s,n,&w,0)||w!=n||!FlushFileBuffers(h)){io_error=1;return 0;}return 1;}
static void text(const char *k,const char *v){char b[700];wsprintfA(b,"%s=%s\r\n",k,v);put(log_file,b);}
static void num(const char *k,DWORD v){char b[32];wsprintfA(b,"%lu",v);text(k,b);}
static void cn(unsigned i,const char *k,DWORD v){char b[80];wsprintfA(b,"c%u.%s",i,k);num(b,v);}
static int token(const char **cursor,char *out,unsigned cap){const char *p=*cursor;unsigned n=0;int q=0;while(*p==' '||*p=='\t')p++;if(!*p){*cursor=p;return 0;}if(*p=='"'){q=1;p++;}while(*p&&(q?*p!='"':(*p!=' '&&*p!='\t'))){if(*p=='"'||n+1>=cap)return -1;out[n++]=*p++;}if(q){if(*p!='"')return -1;p++;if(*p&&*p!=' '&&*p!='\t')return -1;}out[n]=0;*cursor=p;return n?1:-1;}
static int prefix_ok(const char *s){unsigned n=0;for(;*s;s++,n++)if(!((*s>='a'&&*s<='z')||(*s>='A'&&*s<='Z')||(*s>='0'&&*s<='9')||*s=='-'))return 0;return n>0&&n<=48;}
static int vacant(const char *prefix){WIN32_FIND_DATAA d;HANDLE h;char b[80];wsprintfA(b,"%s*",prefix);h=FindFirstFileA(b,&d);if(h!=INVALID_HANDLE_VALUE){FindClose(h);return 0;}return GetLastError()==ERROR_FILE_NOT_FOUND;}
static void ft(unsigned i,const char *stem,FILETIME f){char b[60];wsprintfA(b,"%s.low",stem);cn(i,b,f.dwLowDateTime);wsprintfA(b,"%s.high",stem);cn(i,b,f.dwHighDateTime);}
static int child(unsigned i,const char *exe,const char *backend,const char *prefix,MEMORY_FN memory){
 STARTUPINFOA si;PROCESS_INFORMATION pi;FILETIME created,ended,kernel,user;COUNTERS m;
 char command[700],name[64],receipt[80],value[32];DWORD start,elapsed,wait=WAIT_FAILED,code=99,samples=0;
 DWORD min_ws=0xffffffff,max_ws=0,peak_ws=0,max_commit=0,peak_commit=0,first_faults=0,last_faults=0;
 MEMORYSTATUS before,after;HANDLE h;int good=0,clean=1;
 zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
 wsprintfA(name,"%s-c%u",prefix,i);wsprintfA(command,"\"%s\" %s %s",exe,backend,name);
 zero(&before,sizeof(before));before.dwLength=sizeof(before);GlobalMemoryStatus(&before);
 cn(i,"available_before",before.dwAvailPhys);cn(i,"physical_total",before.dwTotalPhys);
 start=GetTickCount();cn(i,"start_tick",start);
 if(!CreateProcessA(exe,command,0,0,FALSE,0,0,0,&si,&pi)){cn(i,"create_error",GetLastError());return 0;}
 cn(i,"pid",pi.dwProcessId);clean&=CloseHandle(pi.hThread)!=0;
 for(;;){
  wait=WaitForSingleObject(pi.hProcess,50);
  if(wait!=WAIT_TIMEOUT)break;
  if((DWORD)(GetTickCount()-start)>=50000){cn(i,"deadline",1);break;}
  zero(&m,sizeof(m));m.cb=sizeof(m);
  if(!memory(pi.hProcess,&m,sizeof(m))){
   /* A terminated child can race this snapshot. Only accept a signalled exit. */
   wait=WaitForSingleObject(pi.hProcess,0);
   if(wait==WAIT_OBJECT_0){cn(i,"exit_sample_race",1);break;}
   cn(i,"memory_error",GetLastError());break;
  }
  if(m.cb!=sizeof(m)){cn(i,"counter_size_error",m.cb);break;}
  if(!samples)first_faults=m.faults;
  last_faults=m.faults;samples++;
  if(m.ws<min_ws)min_ws=m.ws;
  if(m.ws>max_ws)max_ws=m.ws;
  if(m.peak_ws>peak_ws)peak_ws=m.peak_ws;
  if(m.commit>max_commit)max_commit=m.commit;
  if(m.peak_commit>peak_commit)peak_commit=m.peak_commit;
 }
 elapsed=(DWORD)(GetTickCount()-start);cn(i,"elapsed_ms",elapsed);cn(i,"wait",wait);
 if(wait!=WAIT_OBJECT_0){
  cn(i,"terminate",TerminateProcess(pi.hProcess,98));cn(i,"terminate_wait",WaitForSingleObject(pi.hProcess,5000));goto done;
 }
 if(!GetExitCodeProcess(pi.hProcess,&code)){cn(i,"exit_query_error",GetLastError());goto done;}
 cn(i,"exit",code);
 if(!GetProcessTimes(pi.hProcess,&created,&ended,&kernel,&user)){cn(i,"times_error",GetLastError());goto done;}
 ft(i,"created",created);ft(i,"ended",ended);ft(i,"kernel",kernel);ft(i,"user",user);
 cn(i,"samples",samples);cn(i,"min_ws",min_ws);cn(i,"max_ws",max_ws);cn(i,"peak_ws",peak_ws);
 cn(i,"max_commit",max_commit);cn(i,"peak_commit",peak_commit);cn(i,"first_faults",first_faults);cn(i,"last_faults",last_faults);
 wsprintfA(receipt,"%s.exit",name);h=CreateFileA(receipt,GENERIC_WRITE,0,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);
 if(h==INVALID_HANDLE_VALUE){cn(i,"receipt_error",GetLastError());goto done;}
 wsprintfA(value,"%lu\r\n",code);good=put(h,value);clean&=CloseHandle(h)!=0;
 good=good&&code==0&&samples>0&&elapsed>0&&elapsed<50000;
done:
 clean&=CloseHandle(pi.hProcess)!=0;cn(i,"handles_closed",clean);
 zero(&after,sizeof(after));after.dwLength=sizeof(after);GlobalMemoryStatus(&after);cn(i,"available_after",after.dwAvailPhys);
 cn(i,"complete",good&&clean&&!io_error);return good&&clean&&!io_error;
}
void WINAPI mainCRTStartup(void){
 const char *s=GetCommandLineA();char own[MAX_PATH],arg[512],backend[16],prefix[64],extra[2],path[80],psapi_path[MAX_PATH];
 unsigned i,n;HMODULE lib=0;union {FARPROC raw;MEMORY_FN memory;} fn;int code=1;OSVERSIONINFOA os;
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
 if(token(&s,arg,sizeof(arg))!=1||token(&s,backend,sizeof(backend))!=1||token(&s,prefix,sizeof(prefix))!=1||token(&s,extra,sizeof(extra))!=0||
    (lstrcmpA(backend,"default")&&lstrcmpA(backend,"hel"))||!prefix_ok(prefix)||!vacant(prefix))ExitProcess(2);
 n=GetModuleFileNameA(0,own,sizeof(own));if(!n||n>=sizeof(own))ExitProcess(2);
 while(n&&own[n-1]!='\\')n--;
 if(!n||n+10>=sizeof(own))ExitProcess(2);
 lstrcpyA(own+n,"scene.exe");
 wsprintfA(path,"%s-bench.txt",prefix);log_file=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);
 if(log_file==INVALID_HANDLE_VALUE)ExitProcess(2);
 text("schema","xwn-scene-bench-1");text("backend",backend);text("scope","three-child-processes-including-pauses-and-capture-io");
 num("iterations",3);num("poll_ms",50);num("child_deadline_ms",50000);
 zero(&os,sizeof(os));os.dwOSVersionInfoSize=sizeof(os);if(!GetVersionExA(&os))goto done;
 num("os.major",os.dwMajorVersion);num("os.minor",os.dwMinorVersion);num("os.build",os.dwBuildNumber);
 n=GetSystemDirectoryA(psapi_path,sizeof(psapi_path));if(!n||n+11>=sizeof(psapi_path))goto done;
 lstrcatA(psapi_path,"\\psapi.dll");lib=LoadLibraryA(psapi_path);num("psapi.load",lib!=0);if(!lib)goto done;
 fn.raw=GetProcAddress(lib,"GetProcessMemoryInfo");num("psapi.entry",fn.raw!=0);if(!fn.raw)goto done;
 for(i=0;i<3;i++)if(!child(i,own,backend,prefix,fn.memory))break;
 num("completed",i);if(i==3)code=0;
done:
 if(lib){int ok=FreeLibrary(lib)!=0;num("psapi.unload",ok);if(!ok)code=1;}
 if(io_error)code=4;
 num("exit",code);text("end","complete");if(!CloseHandle(log_file))io_error=1;ExitProcess(io_error?4:(UINT)code);
}
