/* Bounded synchronous log-style append sequence; owned emulator only. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static HANDLE Log,Ready,Stop;
static DWORD Mode;
static volatile LONG Frames,During,Active,DrawError;
static LONG counter(volatile LONG *p){return InterlockedCompareExchange(p,0,0);}
static LRESULT CALLBACK proc(HWND w,UINT msg,WPARAM a,LPARAM b){
 if(msg==WM_CLOSE){InterlockedExchange(&DrawError,1);DestroyWindow(w);return 0;}
 if(msg==WM_DESTROY){PostQuitMessage(0);return 0;}
 return DefWindowProcA(w,msg,a,b);
}
static DWORD WINAPI drawing(LPVOID unused){
 WNDCLASSA wc={0};HWND win=NULL;HDC screen=NULL,mem=NULL;HBITMAP bitmap=NULL;HGDIOBJ oldBitmap=NULL;
 HBRUSH brushes[8]={0};MSG msg;DWORD i,frame=0;RECT r;int good=1;
 (void)unused;wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="XwnDrawAppend";
 if(!RegisterClassA(&wc))good=0;
 if(good)win=CreateWindowExA(0,wc.lpszClassName,"Owned GDI / FATX diagnostic",WS_OVERLAPPEDWINDOW|WS_VISIBLE,30,30,560,390,NULL,NULL,wc.hInstance,NULL);
 if(!win)good=0;
 if(good){screen=GetDC(win);if(!screen)good=0;}
 if(good){mem=CreateCompatibleDC(screen);bitmap=CreateCompatibleBitmap(screen,512,320);if(!mem||!bitmap)good=0;}
 if(good){oldBitmap=SelectObject(mem,bitmap);if(!oldBitmap||oldBitmap==HGDI_ERROR)good=0;}
 for(i=0;i<8&&good;i++){brushes[i]=CreateSolidBrush(RGB(i*31,255-i*29,i*17));if(!brushes[i])good=0;}
 if(!good)InterlockedExchange(&DrawError,2);
 SetEvent(Ready);
 while(good&&WaitForSingleObject(Stop,0)==WAIT_TIMEOUT){
  while(PeekMessageA(&msg,NULL,0,0,PM_REMOVE)){
   if(msg.message==WM_QUIT){good=0;break;}
   TranslateMessage(&msg);DispatchMessageA(&msg);
  }
  if(Mode&&good){
   LONG wasActive=counter(&Active);
   for(i=0;i<8;i++){r.left=0;r.right=512;r.top=i*40;r.bottom=r.top+40;if(!FillRect(mem,&r,brushes[(i+frame)%8]))good=0;}
   if(!BitBlt(screen,0,0,512,320,mem,0,0,SRCCOPY)||!GdiFlush())good=0;
   if(good){InterlockedIncrement(&Frames);if(wasActive&&counter(&Active)==wasActive)InterlockedIncrement(&During);frame++;}
   else InterlockedExchange(&DrawError,3);
  }
  Sleep(10);
 }
 if(oldBitmap&&oldBitmap!=HGDI_ERROR&&!SelectObject(mem,oldBitmap))InterlockedExchange(&DrawError,4);
 if(bitmap&&!DeleteObject(bitmap))InterlockedExchange(&DrawError,5);
 if(mem&&!DeleteDC(mem))InterlockedExchange(&DrawError,6);
 for(i=0;i<8;i++)if(brushes[i]&&!DeleteObject(brushes[i]))InterlockedExchange(&DrawError,7);
 if(screen&&ReleaseDC(win,screen)!=1)InterlockedExchange(&DrawError,8);
 if(win&&IsWindow(win)&&!DestroyWindow(win))InterlockedExchange(&DrawError,9);
 if(!UnregisterClassA(wc.lpszClassName,wc.hInstance))InterlockedExchange(&DrawError,10);
 return counter(&DrawError)?1:0;
}
static BYTE Expected[1048576],Readback[1048576],Append[4097];
static const DWORD Offsets[]={401,3985,65425,270225};
static const DWORD Lengths[]={219,110,111,112,221,4097};
static DWORD update(DWORD h,const BYTE *b,DWORD n){DWORD i;for(i=0;i<n;i++)h=(h^b[i])*16777619u;return h;}
static DWORD checksum(const BYTE *b,DWORD n){return update(2166136261u,b,n);}
static void report(const char *name,DWORD a,DWORD b,DWORD c,DWORD d,DWORD e,DWORD f){char s[220];DWORD n,len;wsprintfA(s,"%s %lu %lu %lu %lu %lu %lu\r\n",name,a,b,c,d,e,f);len=lstrlenA(s);if(!WriteFile(Log,s,len,&n,NULL)||n!=len||!FlushFileBuffers(Log))Sleep(INFINITE);}
static int fail(DWORD id,DWORD stage){DWORD e=GetLastError();InterlockedExchange(&Active,0);report("FAIL",id,stage,e,0,0,0);return 0;}
static int failclosed(HANDLE h,DWORD id,DWORD stage){DWORD e=GetLastError();CloseHandle(h);SetLastError(e);return fail(id,stage);}
static BYTE prefix(DWORD i,DWORD key){return (BYTE)(33+(i*13+key*3)%90);}
static BYTE appended(DWORD i,DWORD key,DWORD step,DWORD size){return i==size-2?13:i==size-1?10:(BYTE)(32+(i*7+key*11+step*17)%95);}
static int testcase(DWORD id,DWORD policy,DWORD reopen,DWORD offset){
 char path[80];HANDLE h;DWORD i,step,n,size,key=id%4,total=offset,before,after;
 DWORD sourceBefore=2166136261u,sourceAfter=2166136261u,flushes=0,frameBefore,frameAfter;
 wsprintfA(path,"C:\\xwnda01\\t%03lu.bin",id);
 for(i=0;i<offset;i++)Expected[i]=prefix(i,key);
 before=checksum(Expected,offset);
 h=CreateFileA(path,GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 if(h==INVALID_HANDLE_VALUE)return fail(id,1);
 if(!WriteFile(h,Expected,offset,&n,NULL))return failclosed(h,id,2);
 after=checksum(Expected,offset);report("SEED",id,offset,n,before,after,0);
 if(n!=offset||before!=after)return failclosed(h,id,3);
 if(!FlushFileBuffers(h))return failclosed(h,id,4);
 /* No diagnostic I/O in this loop: only the selected payload flush policy. */
 frameBefore=counter(&During);InterlockedExchange(&Active,id+1);
 for(step=0;step<512;step++){
  if(reopen){
   if(!CloseHandle(h))return fail(id,5);
   h=CreateFileA(path,GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
   if(h==INVALID_HANDLE_VALUE)return fail(id,6);
  }
  if(SetFilePointer(h,0,NULL,FILE_END)!=total)return failclosed(h,id,7);
  size=Lengths[step%6];if(total+size>sizeof(Expected))return failclosed(h,id,8);
  for(i=0;i<size;i++){Append[i]=appended(i,key,step,size);Expected[total+i]=Append[i];}
  sourceBefore=update(sourceBefore,Append,size);
  if(!WriteFile(h,Append,size,&n,NULL)||n!=size)return failclosed(h,id,9);
  sourceAfter=update(sourceAfter,Append,size);
  for(i=0;i<size;i++)if(Append[i]!=appended(i,key,step,size))return failclosed(h,id,10);
  if(policy==0){if(!FlushFileBuffers(h))return failclosed(h,id,11);flushes++;}
  total+=size;
  if(step%16==15)Sleep(1);
 }
 InterlockedExchange(&Active,0);frameAfter=counter(&During);
 if(policy==1){if(!FlushFileBuffers(h))return failclosed(h,id,12);flushes++;}
 if(!CloseHandle(h))return fail(id,13);
 report("SOURCE",id,512,total-offset,sourceBefore,sourceAfter,flushes);
 report("DRAW",id,Mode,frameBefore,frameAfter,frameAfter-frameBefore,counter(&DrawError));
 if(counter(&DrawError)||(Mode&&frameAfter==frameBefore))return fail(id,17);
 h=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(h==INVALID_HANDLE_VALUE)return fail(id,14);
 if(GetFileSize(h,NULL)!=total||!ReadFile(h,Readback,total,&n,NULL)||n!=total)return failclosed(h,id,15);
 if(!CloseHandle(h))return fail(id,16);
 for(i=0;i<total;i++)if(Readback[i]!=Expected[i]){report("MISMATCH",id,i,Readback[i],Expected[i],0,0);return 0;}
 report("CASE",id,policy,reopen,offset,total,checksum(Readback,total));return 1;
}
void WINAPI mainCRTStartup(void){
 DWORD id=0,policy,reopen,o,started,status,n,exitCode;HANDLE token,config,thread;BYTE modeByte;TOKEN_PRIVILEGES tp;HMODULE setup;WAIT_INSTALL wait;int ok=1;
 if(!CreateDirectoryA("C:\\xwnda01",NULL))ExitProcess(80);
 Log=CreateFileA("C:\\xwnda01\\probe.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(81);
 config=CreateFileA("C:\\xwnidle\\drawmode.txt",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(config==INVALID_HANDLE_VALUE||GetFileSize(config,NULL)!=1||!ReadFile(config,&modeByte,1,&n,NULL)||n!=1||(modeByte!='0'&&modeByte!='1')){report("FAIL_CONFIG",0,0,0,0,0,0);ExitProcess(82);}
 CloseHandle(config);Mode=modeByte-'0';Ready=CreateEventA(NULL,TRUE,FALSE,NULL);Stop=CreateEventA(NULL,TRUE,FALSE,NULL);
 thread=CreateThread(NULL,0,drawing,NULL,0,NULL);
 if(!Ready||!Stop||!thread||WaitForSingleObject(Ready,10000)!=WAIT_OBJECT_0||counter(&DrawError)){report("FAIL_DRAW_START",counter(&DrawError),0,0,0,0,0);Sleep(INFINITE);}
 report("ATTEMPT_ONCE",16,512,4,2,2,Mode);started=GetTickCount();
 for(policy=0;policy<2&&ok;policy++)for(reopen=0;reopen<2&&ok;reopen++)for(o=0;o<4&&ok;o++){ok=testcase(id,policy,reopen,Offsets[o]);if(ok)id++;}
 SetEvent(Stop);
 if(WaitForSingleObject(thread,10000)!=WAIT_OBJECT_0||!GetExitCodeThread(thread,&exitCode)){report("FAIL_DRAW_JOIN",0,0,0,0,0,0);Sleep(INFINITE);}
 report("DRAW_END",Mode,counter(&Frames),counter(&During),counter(&DrawError),exitCode,0);
 CloseHandle(thread);CloseHandle(Ready);CloseHandle(Stop);
 if(counter(&DrawError)||exitCode||(Mode&&!counter(&During)))ok=0;
 report(ok?"COMPLETE":"WORKLOAD_FAILED",id,GetTickCount()-started,0,0,0,0);
 setup=LoadLibraryA("setupapi.dll");wait=setup?(WAIT_INSTALL)GetProcAddress(setup,"CMP_WaitNoPendingInstallEvents"):NULL;
 if(!wait){report("FAIL_PENDING_API",GetLastError(),0,0,0,0,0);Sleep(INFINITE);}
 status=wait(0);if(status!=WAIT_OBJECT_0){report("RESTART_BLOCKED_PENDING_INSTALL",status,0,0,0,0,0);Sleep(INFINITE);}
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){report("FAIL_TOKEN",GetLastError(),0,0,0,0,0);Sleep(INFINITE);}
 tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
 if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){report("FAIL_LOOKUP",GetLastError(),0,0,0,0,0);Sleep(INFINITE);}
 SetLastError(0);if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()){report("FAIL_PRIVILEGE",GetLastError(),0,0,0,0,0);Sleep(INFINITE);}
 CloseHandle(token);report("NORMAL_RESTART_REQUEST",0,0,0,0,0,0);
 if(!ExitWindowsEx(EWX_REBOOT,0))report("FAIL_RESTART",GetLastError(),0,0,0,0,0);
 CloseHandle(Log);ExitProcess(0);
}
