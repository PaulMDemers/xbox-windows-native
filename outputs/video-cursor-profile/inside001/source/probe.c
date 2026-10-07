/* Bounded GDI path comparison; fixed video0093, no device/mode/cache changes. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log;
static HWND Window;
static HDC Screen,Memory,Readback;
static HBITMAP Mb,Rb;
static HGDIOBJ Mo,Ro;
static DWORD *Mem,*Pixels;
static int W,H,Stride;
static DWORD Failures;
static int CursorX,CursorY,Outside;
static HCURSOR Arrow;
static BOOL cursor_good(void){CURSORINFO ci;ci.cbSize=sizeof(ci);return GetCursorInfo(&ci)&&(ci.flags&CURSOR_SHOWING)&&ci.hCursor==Arrow&&ci.ptScreenPos.x==CursorX&&ci.ptScreenPos.y==CursorY;}

typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static WAIT_INSTALL WaitInstall;
static void zero(void*p,DWORD n){volatile BYTE*b=p;while(n--)*b++=0;}
static void record(const char*s,DWORD a,DWORD b,DWORD c){char t[256];DWORD n,w;n=wsprintfA(t,"%s %lu %lu %lu\r\n",s,a,b,c);if(!WriteFile(Log,t,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);}
static void fail(const char*s,DWORD a,DWORD b,DWORD c){++Failures;record(s,a,b,c);}
static BOOL pump(void){MSG m;while(PeekMessageA(&m,NULL,0,0,PM_REMOVE)){if(m.message==WM_QUIT)return FALSE;TranslateMessage(&m);DispatchMessageA(&m);}return IsWindow(Window)&&!(GetAsyncKeyState(VK_ESCAPE)&0x8000);}
static BOOL visible(void){RECT r;return GetClipBox(Screen,&r)==SIMPLEREGION&&r.left<=0&&r.top<=0&&r.right>=W+16&&r.bottom>=H+16;}
static BOOL uncover(void){DWORD start=GetTickCount();do{if(!pump())return FALSE;if(!SetWindowPos(Window,HWND_TOPMOST,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_SHOWWINDOW))return FALSE;Sleep(200);if(!pump())return FALSE;if(visible()){if(!SetCursorPos(CursorX,CursorY))return FALSE;SetCursor(Arrow);Sleep(100);if(!pump())return FALSE;SetCursor(Arrow);return cursor_good();}}while(GetTickCount()-start<10000);return FALSE;}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM a,LPARAM b){if(m==WM_SETCURSOR){SetCursor(Arrow);return TRUE;}if(m==WM_PAINT){PAINTSTRUCT p;BeginPaint(w,&p);EndPaint(w,&p);return 0;}if(m==WM_ERASEBKGND)return 1;if(m==WM_DESTROY){PostQuitMessage(0);return 0;}return DefWindowProcA(w,m,a,b);}
static DWORD pattern(int x,int y){return (((x*13+y*7)&255)<<16)|(((y*11+x*3)&255)<<8)|((x*17+y*19)&255);}
static BOOL initialize(void){int x,y;if(!GdiFlush())return FALSE;for(y=0;y<H+16;y++)for(x=0;x<Stride;x++)Mem[y*Stride+x]=0x557799;for(y=0;y<H;y++)for(x=0;x<W;x++)Mem[y*Stride+x]=pattern(x,y);return BitBlt(Screen,0,0,W,H,Memory,0,0,SRCCOPY)&&GdiFlush();}
static BOOL compare(DWORD kind,int position,DWORD count){int x,y;DWORD got,want;BOOL direct=kind==5;
 if(!direct&&kind!=2){if(!BitBlt(Readback,0,0,W,H,Screen,position,position,SRCCOPY)||!GdiFlush())return FALSE;}
 for(y=0;y<H;y++)for(x=0;x<W;x++){
  got=(direct?Mem[(y+position)*Stride+x+position]:Pixels[y*Stride+x])&0xffffff;
  want=kind==0?((count&1)?0:0xffffff):pattern(x,y);
  if(got!=want){fail("FAIL_PIXEL_X_Y_KIND",x,y,kind);record("EXPECTED_ACTUAL_COUNT",want,got,count);return FALSE;}
 }
 return TRUE;
}
static BOOL operation(DWORD kind,DWORD count){int dst=(count&1)?0:16,src=(count&1)?16:0;
 switch(kind){
 case 0:return PatBlt(Screen,0,0,W,H,(count&1)?WHITENESS:BLACKNESS);
 case 1:return BitBlt(Screen,0,0,W,H,Memory,0,0,SRCCOPY);
 case 2:return BitBlt(Readback,0,0,W,H,Screen,0,0,SRCCOPY);
 case 3:return BitBlt(Screen,dst,dst,W,H,Screen,src,src,SRCCOPY);
 case 4:return BitBlt(Memory,dst,dst,W,H,Memory,src,src,SRCCOPY)&&BitBlt(Screen,dst,dst,W,H,Memory,dst,dst,SRCCOPY);
 default:return BitBlt(Memory,dst,dst,W,H,Memory,src,src,SRCCOPY);
 }
}
static BOOL one(DWORD size,DWORD round,DWORD kind){DWORD count=0,start,elapsed;int pos;BOOL ok;
 if(!uncover()||!initialize()){fail("FAIL_INITIALIZE",size,round,kind);return FALSE;}
 /* Both overlap directions verified before collecting any timings. */
 if(!operation(kind,0)||!GdiFlush()||!compare(kind,kind>=3?16:0,1)||!operation(kind,1)||!GdiFlush()||!compare(kind,0,2)){
  fail("FAIL_PRECHECK",size,round,kind);return FALSE;
 }
 if(!initialize()){fail("FAIL_REINITIALIZE",size,round,kind);return FALSE;}
 start=GetTickCount();
 do{ok=operation(kind,count)&&GdiFlush();if(!ok||!pump()||!visible()||!cursor_good()){fail("FAIL_TIMED_API",kind,count,GetLastError());return FALSE;}++count;elapsed=GetTickCount()-start;}while(count<4096&&elapsed<300);
 pos=kind>=3&&(count&1)?16:0;
 if(!compare(kind,pos,count)||!visible()||!cursor_good()){fail("FAIL_POSTCHECK",size,round,kind);return FALSE;}
 record("CASE_SIZE_ROUND_KIND",size,round,kind);record("TIMING_COUNT_MS_PIXELS",count,elapsed,W*H);record("VERIFIED_PRE_POST",2,1,0);return TRUE;
}
static BOOL surfaces(int w,int h){BITMAPINFO b;W=w;H=h;Stride=w+16;zero(&b,sizeof(b));b.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);b.bmiHeader.biWidth=Stride;b.bmiHeader.biHeight=-(H+16);b.bmiHeader.biPlanes=1;b.bmiHeader.biBitCount=32;
 Memory=CreateCompatibleDC(Screen);Readback=CreateCompatibleDC(Screen);Mb=CreateDIBSection(Screen,&b,DIB_RGB_COLORS,(void**)&Mem,NULL,0);Rb=CreateDIBSection(Screen,&b,DIB_RGB_COLORS,(void**)&Pixels,NULL,0);
 if(!Memory||!Readback||!Mb||!Rb)return FALSE;
 Mo=SelectObject(Memory,Mb);Ro=SelectObject(Readback,Rb);return Mo&&Ro&&Mo!=HGDI_ERROR&&Ro!=HGDI_ERROR;
}
static BOOL release(void){BOOL ok=GdiFlush();if(Memory&&Mo&&Mo!=HGDI_ERROR)ok=(SelectObject(Memory,Mo)!=NULL)&&ok;if(Readback&&Ro&&Ro!=HGDI_ERROR)ok=(SelectObject(Readback,Ro)!=NULL)&&ok;if(Mb)ok=DeleteObject(Mb)&&ok;if(Rb)ok=DeleteObject(Rb)&&ok;if(Memory)ok=DeleteDC(Memory)&&ok;if(Readback)ok=DeleteDC(Readback)&&ok;Memory=Readback=NULL;Mb=Rb=NULL;Mo=Ro=NULL;return ok;}
static BOOL restart(void){HANDLE t,v;TOKEN_PRIVILEGES p;v=CreateFileA("\\\\.\\C:",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);if(v==INVALID_HANDLE_VALUE)return FALSE;if(!FlushFileBuffers(v)){CloseHandle(v);return FALSE;}CloseHandle(v);if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&t))return FALSE;p.PrivilegeCount=1;p.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&p.Privileges[0].Luid)){CloseHandle(t);return FALSE;}SetLastError(0);if(!AdjustTokenPrivileges(t,FALSE,&p,0,NULL,NULL)||GetLastError()){CloseHandle(t);return FALSE;}CloseHandle(t);record("NORMAL_RESTART_REQUEST",0,0,0);return ExitWindowsEx(EWX_REBOOT,0);}
void WINAPI mainCRTStartup(void){WNDCLASSA wc;DWORD s,r,i,wait,start;RECT bounds;char setting[4];const int widths[]={64,256,768},heights[]={64,128,384};
 Log=CreateFileA("C:\\xwnvid108\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(Log==INVALID_HANDLE_VALUE)ExitProcess(91);record("ATTEMPT_ONCE",108,3,3);
 if(GetEnvironmentVariableA("XWN_CURSOR_OUTSIDE",setting,sizeof(setting))!=1||(setting[0]!='0'&&setting[0]!='1'))ExitProcess(92);
 Outside=setting[0]=='1';CursorX=Outside?1000:512;CursorY=Outside?550:288;Arrow=LoadCursorA(NULL,IDC_ARROW);if(!Arrow)ExitProcess(93);record("CURSOR_CONFIGURATION",CursorX,CursorY,Outside);
 WaitInstall=(WAIT_INSTALL)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");if(!WaitInstall){fail("FAIL_INSTALL_EXPORT",GetLastError(),0,0);ExitProcess(1);}wait=WaitInstall(30000);record("INSTALL_IDLE_START",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(2);
 zero(&wc,sizeof(wc));wc.style=CS_OWNDC;wc.hCursor=Arrow;wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="XwnVideoCursor108";if(!RegisterClassA(&wc))ExitProcess(3);
 Window=CreateWindowExA(WS_EX_TOPMOST,wc.lpszClassName,"XWN copy-path correctness/profile",WS_OVERLAPPED|WS_CAPTION|WS_VISIBLE,20,20,830,470,NULL,NULL,wc.hInstance,NULL);if(!Window)ExitProcess(4);SetForegroundWindow(Window);UpdateWindow(Window);Screen=GetDC(Window);if(!Screen)ExitProcess(5);GdiSetBatchLimit(1);
 record("MODE_WIDTH_HEIGHT_BPP",GetDeviceCaps(Screen,HORZRES),GetDeviceCaps(Screen,VERTRES),GetDeviceCaps(Screen,BITSPIXEL)*GetDeviceCaps(Screen,PLANES));
 if(GetDeviceCaps(Screen,HORZRES)!=1024||GetDeviceCaps(Screen,VERTRES)!=576||GetDeviceCaps(Screen,BITSPIXEL)*GetDeviceCaps(Screen,PLANES)!=32){fail("FAIL_MODE",0,0,0);ExitProcess(6);}
 if(!GetClientRect(Window,&bounds)||bounds.right<784||bounds.bottom<400){fail("FAIL_CLIENT",bounds.right,bounds.bottom,0);ExitProcess(7);}
 start=GetTickCount();while(GetTickCount()-start<2000){if(!pump())ExitProcess(8);Sleep(20);}
 for(s=0;s<3&&!Failures;s++){
  if(!surfaces(widths[s],heights[s])){fail("FAIL_SURFACES",s,GetLastError(),0);release();break;}
  record("GEOMETRY_INDEX_W_H",s,W,H);record("DIB_STRIDE_BYTES",Stride*4,(H+16)*Stride*4,2);
  for(r=0;r<3&&!Failures;r++)for(i=0;i<6&&!Failures;i++)one(s,r,(i+r)%6);
  if(!release())fail("FAIL_RELEASE",s,GetLastError(),0);
 }
 if(!ReleaseDC(Window,Screen)||!DestroyWindow(Window))fail("FAIL_WINDOW_RELEASE",GetLastError(),0,0);
 record(Failures?"FAIL":"COMPLETE",Failures,54,162);if(Failures){CloseHandle(Log);ExitProcess(10);}
 wait=WaitInstall(30000);record("INSTALL_IDLE_END",wait,0,0);if(wait!=WAIT_OBJECT_0){CloseHandle(Log);ExitProcess(11);}
 if(!restart()){fail("FAIL_RESTART",GetLastError(),0,0);CloseHandle(Log);ExitProcess(12);}CloseHandle(Log);ExitProcess(0);
}
