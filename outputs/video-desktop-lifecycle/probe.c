/* NT5 desktop API exercise. No driver calls, mode edits, hooks or injected input. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#define W 128
#define H 96
#define ROUNDS 3
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static HANDLE Log;
static DWORD Stage,Failures;
static void zero(void *p,DWORD n){volatile BYTE *b=p;while(n--)*b++=0;}
static DWORD hash(const void *p,DWORD n){const BYTE *b=p;DWORD h=2166136261u;while(n--)h=(h^*b++)*16777619u;return h;}
static void record(const char *s,DWORD a,DWORD b,DWORD c){char t[192];DWORD n,w;n=wsprintfA(t,"%s %lu %lu %lu\r\n",s,a,b,c);if(!WriteFile(Log,t,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);}
__declspec(dllexport) __attribute__((noinline,noclone,used,externally_visible)) DWORD __cdecl XwnDesktopStage(DWORD round,DWORD phase,DWORD desktop,DWORD result){__asm__ volatile("":::"memory");return round^phase^desktop^result;}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM a,LPARAM b){if(m==WM_SETCURSOR){SetCursor(NULL);return TRUE;}if(m==WM_PAINT){PAINTSTRUCT p;BeginPaint(w,&p);EndPaint(w,&p);return 0;}return DefWindowProcA(w,m,a,b);}
static BOOL shot(DWORD index){
 HWND window=NULL;HDC screen=NULL,src=NULL,dst=NULL;HBITMAP sb=NULL,db=NULL;HGDIOBJ so=NULL,doo=NULL;DWORD *s=NULL,*d=NULL,id[8],pre[32],post[32],x,y,bad=0,written;BITMAPINFO bi;BOOL ok=FALSE,clean=TRUE;HANDLE f=INVALID_HANDLE_VALUE;char name[80];MSG msg;RECT clip;DWORD start;
 Stage=10;window=CreateWindowExA(WS_EX_TOPMOST,"XwnDesktop126","XWN supported desktop lifecycle",WS_POPUP|WS_VISIBLE,0,0,1024,576,NULL,NULL,GetModuleHandleA(NULL),NULL);if(!window)goto done;
 SetForegroundWindow(window);UpdateWindow(window);screen=GetDC(window);if(!screen)goto done;
 start=GetTickCount();do{while(PeekMessageA(&msg,NULL,0,0,PM_REMOVE)){TranslateMessage(&msg);DispatchMessageA(&msg);}if(GetClipBox(screen,&clip)==SIMPLEREGION&&clip.left<=0&&clip.top<=0&&clip.right>=W&&clip.bottom>=H)break;Sleep(50);}while(GetTickCount()-start<10000);
 if(GetClipBox(screen,&clip)!=SIMPLEREGION||clip.left>0||clip.top>0||clip.right<W||clip.bottom<H)goto done;
 Stage=11;zero(id,sizeof(id));if(ExtEscape(screen,0x58574431,0,NULL,sizeof(id),(LPSTR)id)!=1||id[0]!=0x44525758||id[1]!=109||id[2]!=1024||id[3]!=576||id[4]!=4096||id[5]!=32||id[6]!=2359296||id[7]!=1)goto done;
 zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);bi.bmiHeader.biWidth=W;bi.bmiHeader.biHeight=-H;bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;
 src=CreateCompatibleDC(screen);dst=CreateCompatibleDC(screen);sb=CreateDIBSection(screen,&bi,DIB_RGB_COLORS,(void**)&s,NULL,0);db=CreateDIBSection(screen,&bi,DIB_RGB_COLORS,(void**)&d,NULL,0);if(!src||!dst||!sb||!db)goto done;
 so=SelectObject(src,sb);doo=SelectObject(dst,db);if(!so||so==HGDI_ERROR||!doo||doo==HGDI_ERROR)goto done;
 for(y=0;y<H;y++)for(x=0;x<W;x++)s[y*W+x]=(((x*3+y*5+index*17)&255)<<16)|(((x*7+y*11+index*29)&255)<<8)|((x*13+y*17+index*43)&255);
 Stage=12;zero(pre,sizeof(pre));zero(post,sizeof(post));if(!GdiFlush()||ExtEscape(screen,0x58574432,0,NULL,sizeof(pre),(LPSTR)pre)!=1||pre[0]!=0x53525758||pre[1]!=109||pre[20]!=1)goto done;
 if(!BitBlt(screen,0,0,W,H,src,0,0,SRCCOPY)||!GdiFlush()||!BitBlt(dst,0,0,W,H,screen,0,0,SRCCOPY)||!GdiFlush())goto done;
 if(ExtEscape(screen,0x58574432,0,NULL,sizeof(post),(LPSTR)post)!=1||post[0]!=pre[0]||post[1]!=109||post[19]||post[20]!=1)goto done;
 for(x=0;x<W*H;x++){if((s[x]^d[x])&0xffffff)bad++;d[x]&=0xffffff;}
 record("SHOT",index,W*H,bad);record("DIGEST",hash(d,W*H*4),hash(s,W*H*4),W*H*4);record("DRIVER",id[1],id[2],id[3]);record("COHERENCE",post[19],post[20],0);
 if(bad)goto done;
 Stage=13;wsprintfA(name,"C:\\xwndesk126\\ref%02lu.rgb",index);f=CreateFileA(name,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(f==INVALID_HANDLE_VALUE)goto done;
 if(!WriteFile(f,d,W*H*4,&written,NULL)||written!=W*H*4||!FlushFileBuffers(f))goto done;
 ok=TRUE;
done:
 if(f!=INVALID_HANDLE_VALUE)clean=CloseHandle(f)&&clean;
 if(src&&so&&so!=HGDI_ERROR)clean=(SelectObject(src,so)!=NULL)&&clean;
 if(dst&&doo&&doo!=HGDI_ERROR)clean=(SelectObject(dst,doo)!=NULL)&&clean;
 if(sb)clean=DeleteObject(sb)&&clean;
 if(db)clean=DeleteObject(db)&&clean;
 if(src)clean=DeleteDC(src)&&clean;
 if(dst)clean=DeleteDC(dst)&&clean;
 if(screen)clean=(ReleaseDC(window,screen)!=0)&&clean;
 if(window)clean=DestroyWindow(window)&&clean;
 record("SHOT_RELEASE",index,ok,clean);return ok&&clean;
}
static BOOL cycle(DWORD round,HDESK original,HDESK input){
 const DWORD access=DESKTOP_CREATEWINDOW|DESKTOP_READOBJECTS|DESKTOP_WRITEOBJECTS|DESKTOP_SWITCHDESKTOP;
 HDESK fresh=NULL,test;char name[64];BOOL ok=FALSE,a,b,c;DWORD err;
 wsprintfA(name,"XwnDesktop126_%lu",round);Stage=1;
 test=OpenDesktopA(name,0,FALSE,access);if(test){CloseDesktop(test);return FALSE;}
 err=GetLastError();record("ABSENT_BEFORE",round,err,0);if(err!=ERROR_FILE_NOT_FOUND)return FALSE;
 if(!shot(round*3))return FALSE;
 XwnDesktopStage(round,0,0,0);Stage=2;fresh=CreateDesktopA(name,NULL,NULL,0,access,NULL);record("CREATED",round,(DWORD)fresh,fresh?0:GetLastError());if(!fresh)return FALSE;
 XwnDesktopStage(round,1,(DWORD)fresh,1);a=SetThreadDesktop(fresh);record("ATTACHED",round,a,a?0:GetLastError());if(!a)goto done;
 Stage=3;a=SwitchDesktop(fresh);record("SWITCHED",round,a,a?0:GetLastError());if(!a)goto done;
 XwnDesktopStage(round,2,(DWORD)fresh,1);if(!shot(round*3+1))goto done;ok=TRUE;
done:
 Stage=4;a=SetThreadDesktop(original);b=SwitchDesktop(input);record("RESTORED",round,a,b);XwnDesktopStage(round,3,(DWORD)fresh,a&&b);
 c=CloseDesktop(fresh);record("CLOSED",round,c,c?0:GetLastError());XwnDesktopStage(round,4,(DWORD)fresh,c);
 if(!ok||!a||!b||!c)return FALSE;
 test=OpenDesktopA(name,0,FALSE,access);err=test?0:GetLastError();record("ABSENT_AFTER",round,err,0);if(test){CloseDesktop(test);return FALSE;}if(err!=ERROR_FILE_NOT_FOUND)return FALSE;
 if(!shot(round*3+2))return FALSE;
 record("CYCLE_COMPLETE",round,3,0);return TRUE;
}
static BOOL restart(void){HANDLE t,v;TOKEN_PRIVILEGES p;v=CreateFileA("\\\\.\\C:",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);if(v==INVALID_HANDLE_VALUE)return FALSE;if(!FlushFileBuffers(v)){CloseHandle(v);return FALSE;}CloseHandle(v);if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&t))return FALSE;p.PrivilegeCount=1;p.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&p.Privileges[0].Luid)){CloseHandle(t);return FALSE;}SetLastError(0);if(!AdjustTokenPrivileges(t,FALSE,&p,0,NULL,NULL)||GetLastError()){CloseHandle(t);return FALSE;}CloseHandle(t);record("NORMAL_RESTART_REQUEST",0,0,0);return ExitWindowsEx(EWX_REBOOT,0);}
void WINAPI mainCRTStartup(void){WNDCLASSA wc;WAIT_INSTALL wait_install;DWORD wait,i;HDESK original,input;BOOL ok;
 Log=CreateFileA("C:\\xwndesk126\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(Log==INVALID_HANDLE_VALUE)ExitProcess(91);record("ATTEMPT_ONCE",126,ROUNDS,9*W*H);
 wait_install=(WAIT_INSTALL)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");if(!wait_install)ExitProcess(1);wait=wait_install(30000);record("INSTALL_IDLE_START",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(2);
 original=GetThreadDesktop(GetCurrentThreadId());input=OpenInputDesktop(0,FALSE,DESKTOP_SWITCHDESKTOP|DESKTOP_READOBJECTS);if(!original||!input)ExitProcess(3);
 zero(&wc,sizeof(wc));wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="XwnDesktop126";if(!RegisterClassA(&wc))ExitProcess(4);GdiSetBatchLimit(1);
 for(i=0;i<ROUNDS;i++)if(!cycle(i,original,input)){record("HARNESS_FAILURE",i,GetLastError(),Stage);Failures++;break;}
 ok=SwitchDesktop(input);record("INPUT_RESTORED",ok,0,0);if(!ok)Failures++;ok=CloseDesktop(input);record("INPUT_CLOSED",ok,0,0);if(!ok)Failures++;ok=UnregisterClassA(wc.lpszClassName,wc.hInstance);record("CLASS_CLOSED",ok,0,0);if(!ok)Failures++;
 record("COMPLETE",Failures,i,i*3*W*H);wait=wait_install(30000);record("INSTALL_IDLE_END",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(5);if(!restart()){record("RESTART_FAILURE",GetLastError(),0,0);ExitProcess(6);}CloseHandle(Log);ExitProcess(Failures?7:0);
}
