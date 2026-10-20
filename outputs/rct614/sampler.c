/* MIT. Original NT5 process-cost control. No game or driver modification. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <psapi.h>
typedef BOOL (WINAPI *MEMFN)(HANDLE,PPROCESS_MEMORY_COUNTERS,DWORD);
typedef struct {ULONGLONG q,k,u;DWORD tick,ws,peak,page;} SNAP;
static MEMFN memfn;
static HANDLE logh;
static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static ULONGLONG ft(FILETIME f){return ((ULONGLONG)f.dwHighDateTime<<32)|f.dwLowDateTime;}
static void hex64(char *s,ULONGLONG v){int i;for(i=15;i>=0;i--){s[i]="0123456789abcdef"[(DWORD)v&15];v>>=4;}s[16]=0;}
static BOOL snap(HANDLE p,SNAP *s,BOOL memory){
 FILETIME c,e,k,u;LARGE_INTEGER q;PROCESS_MEMORY_COUNTERS m;
 if(!QueryPerformanceCounter(&q)||q.QuadPart<0||!GetProcessTimes(p,&c,&e,&k,&u))return FALSE;
 zero(&m,sizeof(m));m.cb=sizeof(m);
 if(memory&&!memfn(p,&m,sizeof(m)))return FALSE;
 s->q=(ULONGLONG)q.QuadPart;s->tick=GetTickCount();s->k=ft(k);s->u=ft(u);
 s->ws=m.WorkingSetSize;s->peak=m.PeakWorkingSetSize;s->page=m.PagefileUsage;
 return TRUE;
}
static BOOL text(const char *s){DWORD n=lstrlenA(s),w;return WriteFile(logh,s,n,&w,0)&&n==w&&FlushFileBuffers(logh);}
static BOOL row(const char *tag,DWORD id,DWORD index,SNAP *s){
 char b[256],q[17],k[17],u[17];hex64(q,s->q);hex64(k,s->k);hex64(u,s->u);
 wsprintfA(b,"%s %lu %lu %s %lu %s %s %lu %lu %lu\r\n",tag,id,index,q,s->tick,k,u,s->ws,s->peak,s->page);
 return text(b);
}
static BOOL init(const char *path){
 HMODULE m;LARGE_INTEGER f;char b[80],h[17];
 m=LoadLibraryA("psapi.dll");if(!m)return FALSE;
 memfn=(MEMFN)GetProcAddress(m,"GetProcessMemoryInfo");if(!memfn)return FALSE;
 logh=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
 if(logh==INVALID_HANDLE_VALUE||!QueryPerformanceFrequency(&f)||f.QuadPart<=0)return FALSE;
 hex64(h,(ULONGLONG)f.QuadPart);wsprintfA(b,"FREQ %s\r\n",h);return text(b);
}
#ifdef WORKER
static HANDLE serialh;
static BOOL mark(const char *tag,DWORD id,SNAP *s){
 char b[100];DWORD n,w;wsprintfA(b,"MARK %s %lu %lu\r\n",tag,id,s->tick);n=lstrlenA(b);
 return WriteFile(serialh,b,n,&w,0)&&n==w;
}
static BOOL serial_open(void){
 DCB d;COMMTIMEOUTS t;
 serialh=CreateFileA("\\\\.\\COM1",GENERIC_WRITE,0,0,OPEN_EXISTING,0,0);if(serialh==INVALID_HANDLE_VALUE)return FALSE;
 zero(&d,sizeof(d));d.DCBlength=sizeof(d);if(!GetCommState(serialh,&d))return FALSE;
 d.BaudRate=CBR_115200;d.ByteSize=8;d.Parity=NOPARITY;d.StopBits=ONESTOPBIT;
 d.fBinary=TRUE;d.fParity=FALSE;d.fOutxCtsFlow=FALSE;d.fOutxDsrFlow=FALSE;
 d.fOutX=FALSE;d.fInX=FALSE;d.fDtrControl=DTR_CONTROL_ENABLE;d.fRtsControl=RTS_CONTROL_ENABLE;
 zero(&t,sizeof(t));t.WriteTotalTimeoutConstant=1000;
 return SetCommState(serialh,&d)&&SetCommTimeouts(serialh,&t);
}
void WINAPI mainCRTStartup(void){
 char path[100],b[100];const char *cmd=GetCommandLineA();DWORD n=lstrlenA(cmd),id,i;
 volatile DWORD value=1;BYTE *block;HANDLE ready,go;SNAP a,r,s,e;
 if(!n||cmd[n-1]<'0'||cmd[n-1]>'5')ExitProcess(80);
 id=cmd[n-1]-'0';
 wsprintfA(path,"C:\\xwn614\\child%lu.txt",id);if(!init(path))ExitProcess(81);
 ready=OpenEventA(EVENT_MODIFY_STATE,FALSE,"XWN614_READY");go=OpenEventA(SYNCHRONIZE,FALSE,"XWN614_GO");
 if(!ready||!go||!serial_open()||!snap(GetCurrentProcess(),&a,TRUE))ExitProcess(82);
 block=VirtualAlloc(0,8*1024*1024,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);if(!block)ExitProcess(83);
 for(i=0;i<8*1024*1024;i+=4096)block[i]=(BYTE)(i>>12);
 if(!snap(GetCurrentProcess(),&r,TRUE)||!row("ALLOC_BEFORE",id,0,&a)||!row("READY",id,0,&r))ExitProcess(84);
 if(!SetEvent(ready)||WaitForSingleObject(go,15000)!=WAIT_OBJECT_0)ExitProcess(85);
 if(!snap(GetCurrentProcess(),&s,TRUE)||!mark("START",id,&s))ExitProcess(86);
 if(id<2)Sleep(5000);
 else for(i=0;i<1073741824;i++)value=value*1664525u+1013904223u;
 if(!snap(GetCurrentProcess(),&e,TRUE)||!mark("END",id,&e))ExitProcess(87);
 CloseHandle(serialh);
 if(!row("WORK_START",id,0,&s)||!row("WORK_END",id,0,&e))ExitProcess(88);
 wsprintfA(b,"RESULT %lu %lu %lu\r\n",id,id<2?0u:1073741824u,value);
 if(!text(b)||!text("PASS\r\n"))ExitProcess(89);
 CloseHandle(logh);CloseHandle(ready);CloseHandle(go);VirtualFree(block,0,MEM_RELEASE);ExitProcess(0);
}
#else
static SNAP samples[1000];
static BOOL run(DWORD id){
 STARTUPINFOA si;PROCESS_INFORMATION pi;HANDLE ready,go;SNAP start,end,ob,oe;
 DWORD n=0,wait=WAIT_FAILED,code=99,t0;BOOL ok=FALSE,periodic=(id==1||id==3||id==4);
 char cmd[80],b[160];zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
 ready=CreateEventA(0,TRUE,FALSE,"XWN614_READY");if(!ready||GetLastError()==ERROR_ALREADY_EXISTS)return FALSE;
 go=CreateEventA(0,TRUE,FALSE,"XWN614_GO");if(!go||GetLastError()==ERROR_ALREADY_EXISTS)return FALSE;
 wsprintfA(cmd,"worker.exe %lu",id);
 if(!CreateProcessA("C:\\xwn614-kit\\worker.exe",cmd,0,0,FALSE,0,0,"C:\\xwn614-kit",&si,&pi))goto done;
 if(WaitForSingleObject(ready,15000)!=WAIT_OBJECT_0)goto done;
 if(!snap(pi.hProcess,&start,TRUE)||!snap(GetCurrentProcess(),&ob,TRUE)||!SetEvent(go))goto done;
 t0=GetTickCount();
 do{
  wait=WaitForSingleObject(pi.hProcess,100);
  if(wait==WAIT_TIMEOUT&&periodic){if(n>=1000||!snap(pi.hProcess,&samples[n],TRUE))goto done;n++;}
 }while(wait==WAIT_TIMEOUT&&(DWORD)(GetTickCount()-t0)<90000);
 if(wait!=WAIT_OBJECT_0||!GetExitCodeProcess(pi.hProcess,&code)||code!=0)goto done;
 /* Terminated-process memory may disappear; preserve final CPU times only. */
 if(!snap(pi.hProcess,&end,FALSE)||!snap(GetCurrentProcess(),&oe,TRUE))goto done;
 if(!row("START",id,0,&start)||!row("END",id,0,&end)||!row("OBSERVER_START",id,0,&ob)||!row("OBSERVER_END",id,0,&oe))goto done;
 {DWORD j;for(j=0;j<n;j++)if(!row("SAMPLE",id,j,&samples[j]))goto done;}
 wsprintfA(b,"CASE %lu %lu %lu %lu %lu\r\n",id,periodic,n,wait,code);ok=text(b);
done:
 if(pi.hProcess){
  if(WaitForSingleObject(pi.hProcess,0)!=WAIT_OBJECT_0){text("OWNED_TERMINATE\r\n");TerminateProcess(pi.hProcess,96);WaitForSingleObject(pi.hProcess,5000);}
  CloseHandle(pi.hThread);CloseHandle(pi.hProcess);
 }
 CloseHandle(ready);CloseHandle(go);return ok;
}
void WINAPI mainCRTStartup(void){
 DWORD i;BOOL ok=TRUE;HANDLE token;TOKEN_PRIVILEGES tp;
 if(!CreateDirectoryA("C:\\xwn614",0)||!init("C:\\xwn614\\sampler.txt"))ExitProcess(90);
 for(i=0;i<6;i++)if(!run(i)){ok=FALSE;break;}
 if(!text(ok?"CONTROL_PASS\r\n":"CONTROL_FAIL\r\n"))ExitProcess(91);
 zero(&tp,sizeof(tp));tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(92);
 if(!LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))ExitProcess(93);
 SetLastError(0);if(!AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)||GetLastError())ExitProcess(94);CloseHandle(token);
 if(!text("RESTART\r\n"))ExitProcess(95);
 CloseHandle(logh);
 if(!ExitWindowsEx(EWX_REBOOT,0))ExitProcess(97);
 ExitProcess(ok?0:1);
}
#endif
