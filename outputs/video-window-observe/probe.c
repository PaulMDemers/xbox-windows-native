/* Controlled real GDI upload baseline; unchanged matched RAM0110/0112. GPL-2.0-or-later. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#define W 384
#define H 256
#define BYTES (W*H*4)
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
typedef struct {HDC dc;HBITMAP bm;HGDIOBJ old;DWORD *bits;} IMAGE;
static HANDLE Log;
static HWND Window;
static HDC Screen;
static IMAGE Ref,Readback,Source,Background,Pattern;
static DWORD Failures,Stage;
static HWND Mover,Block;
static DWORD Paints[3],PaintErrors;
static SIZE TextSize;
static HCURSOR Arrow;
static BOOL CursorVisible;
static const int Positions[6][2]={{12,16},{112,56},{208,104},{240,168},{-24,196},{88,-24}};
static void zero(void *p,DWORD n){volatile BYTE *b=p;while(n--)*b++=0;}
static DWORD hash(const void *p,DWORD n){const BYTE *b=p;DWORD v=2166137261u;while(n--)v=(v^*b++)*16777619u;return v;}
static void record(const char *s,DWORD a,DWORD b,DWORD c){char t[160];DWORD n,w;n=wsprintfA(t,"%s %lu %lu %lu\r\n",s,a,b,c);if(!WriteFile(Log,t,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);}
static BOOL image(IMAGE *im,int w,int h){BITMAPINFO bi;zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);bi.bmiHeader.biWidth=w;bi.bmiHeader.biHeight=-h;bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;im->dc=CreateCompatibleDC(Screen);im->bm=CreateDIBSection(Screen,&bi,DIB_RGB_COLORS,(void**)&im->bits,NULL,0);if(!im->dc||!im->bm)return FALSE;im->old=SelectObject(im->dc,im->bm);return im->old&&im->old!=HGDI_ERROR;}
static BOOL release(IMAGE *im){BOOL ok=SelectObject(im->dc,im->old)!=NULL;ok=DeleteObject(im->bm)&&ok;return DeleteDC(im->dc)&&ok;}
static DWORD base(int x,int y){return (((x*3+y*5)&255)<<16)|(((x*7+y*11)&255)<<8)|((x*13+y*17)&255);}
static BOOL stats(DWORD *d){zero(d,128);return GdiFlush()&&ExtEscape(Screen,0x58574432,0,NULL,128,(LPSTR)d)==1&&d[0]==0x53525758&&(d[1]==110||d[1]==112)&&d[20]==1;}

static BOOL text(HDC dc){HGDIOBJ f=SelectObject(dc,GetStockObject(SYSTEM_FIXED_FONT));BOOL ok;if(!f||!SetBkMode(dc,TRANSPARENT)||SetTextColor(dc,RGB(255,255,255))==CLR_INVALID)return FALSE;ok=TextOutA(dc,8,24,"XWN Move 137",12);return SelectObject(dc,f)!=NULL&&ok;}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM a,LPARAM b){
 if(m==WM_SETCURSOR){SetCursor(CursorVisible?Arrow:NULL);return TRUE;}
 if(m==WM_ERASEBKGND)return 1;
 if(m==WM_PAINT){PAINTSTRUCT p;HDC dc=BeginPaint(w,&p);BOOL ok=TRUE;int id=(int)GetWindowLongA(w,GWL_ID);
  if(id==1){ok=BitBlt(dc,0,0,128,80,Pattern.dc,0,0,SRCCOPY)&&text(dc);}
  else if(id==2){HBRUSH br=CreateSolidBrush(RGB(70,45,170));RECT r={0,0,96,144};ok=br&&FillRect(dc,&r,br);if(br)ok=DeleteObject(br)&&ok;}
  else ok=BitBlt(dc,0,0,W,H,Background.dc,0,0,SRCCOPY);
  if(id<0||id>2)PaintErrors++;else Paints[id]++;if(!ok)PaintErrors++;EndPaint(w,&p);return 0;
 }
 return DefWindowProcA(w,m,a,b);
}
static BOOL pump(void){MSG m;DWORD count=0;while(PeekMessageA(&m,NULL,0,0,PM_REMOVE)){if(++count>4096)return FALSE;TranslateMessage(&m);DispatchMessageA(&m);}return GdiFlush();}
static BOOL redraw(void){return RedrawWindow(Window,NULL,NULL,RDW_INVALIDATE|RDW_ALLCHILDREN|RDW_UPDATENOW)&&pump();}
static BOOL save(const char *name,const void *data,DWORD length){char path[96];HANDLE f;DWORD written;BOOL ok;wsprintfA(path,"C:\\xwnmove137\\%s",name);f=CreateFileA(path,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(f==INVALID_HANDLE_VALUE)return FALSE;ok=WriteFile(f,data,length,&written,NULL)&&written==length&&FlushFileBuffers(f);return CloseHandle(f)&&ok;}
static void compose(int left,int top){int x,y;for(y=0;y<H;y++)for(x=0;x<W;x++){DWORD value=base(x,y);if(x>=left&&x<left+128&&y>=top&&y<top+80)value=Source.bits[(y-top)*128+x-left];if(x>=144&&x<240&&y>=56&&y<200)value=0x462daa;Ref.bits[y*W+x]=value;}}
static DWORD compare(void){DWORD i,bad=0;HDC dc=GetDC(NULL);if(!dc)return 0xffffffff;if(!BitBlt(Readback.dc,0,0,W,H,dc,0,0,SRCCOPY)||!GdiFlush())bad=0xffffffff;else for(i=0;i<W*H;i++)bad+=((Readback.bits[i]^Ref.bits[i])&0xffffff)!=0;if(!ReleaseDC(NULL,dc))return 0xffffffff;return bad;}
static void counters(const char *label,DWORD *a,DWORD *b){DWORD i;for(i=2;i<=18;i++)record(label,i,a[i],b[i]);}
static BOOL one(DWORD n){DWORD quiet[32],pre[32],post[32],rpre[32],rpost[32],move_ms,redraw_ms,bad,rbad,pc[3],i,digest,errors=PaintErrors;BOOL ok;POINT at;RECT bounds;char name[32];int left=Positions[n%6][0],top=Positions[n%6][1];
 Stage=1;CursorVisible=TRUE;if(!SetCursorPos(40+(n%6)*32,32+(n%6)*24))return FALSE;SetCursor(Arrow);if(!pump())return FALSE;
 for(i=0;i<3;i++){pc[i]=Paints[i];}if(!stats(quiet)||!stats(pre))return FALSE;
 Stage=2;move_ms=GetTickCount();ok=SetWindowPos(Mover,NULL,left,top,128,80,SWP_NOZORDER|SWP_NOACTIVATE)&&pump();move_ms=GetTickCount()-move_ms;
 if(!stats(post)){return FALSE;}CursorVisible=FALSE;SetCursor(NULL);if(!GdiFlush())return FALSE;
 Stage=3;compose(left,top);bad=compare();wsprintfA(name,"move%02lu.rgb",n);if(!save(name,Readback.bits,BYTES))return FALSE;if(!GetWindowRect(Mover,&bounds))return FALSE;at.x=bounds.left;at.y=bounds.top;if(!ScreenToClient(Window,&at))return FALSE;
 record("CASE_POSITION",n,(DWORD)at.x,(DWORD)at.y);record("MOVE_API_PIXELS",ok,bad,W*H);record("MOVE_SIZE",bounds.right-bounds.left,bounds.bottom-bounds.top,0);
 for(i=0;i<3;i++){record("MOVE_PAINT",i,pc[i],Paints[i]);}counters("QUIET_COUNTER",quiet,pre);counters("DRAW_COUNTER",pre,post);
 Stage=4;if(!stats(rpre))return FALSE;redraw_ms=GetTickCount();ok=redraw()&&ok;redraw_ms=GetTickCount()-redraw_ms;if(!stats(rpost))return FALSE;rbad=compare();wsprintfA(name,"draw%02lu.rgb",n);if(!save(name,Readback.bits,BYTES))return FALSE;
 digest=hash(Ref.bits,BYTES);record("REDRAW_API_PIXELS",ok,rbad,W*H);counters("REDRAW_COUNTER",rpre,rpost);record("ELAPSED_MS",move_ms,redraw_ms,0);record("REFERENCE_HASH_BYTES",digest,BYTES,hash(Ref.bits,BYTES));record("PAINT_ERRORS",errors,PaintErrors,0);record("COHERENCE_ACTIVE",rpost[19],rpost[20],0);
 if(!ok||bad||rbad||errors!=PaintErrors||at.x!=left||at.y!=top||bounds.right-bounds.left!=128||bounds.bottom-bounds.top!=80)Failures++;
 wsprintfA(name,"ref%02lu.rgb",n);Stage=5;return save(name,Ref.bits,BYTES);
}
static BOOL restart(void){HANDLE t,v;TOKEN_PRIVILEGES p;v=CreateFileA("\\\\.\\C:",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);if(v==INVALID_HANDLE_VALUE)return FALSE;if(!FlushFileBuffers(v)){CloseHandle(v);return FALSE;}CloseHandle(v);if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&t))return FALSE;p.PrivilegeCount=1;p.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&p.Privileges[0].Luid)){CloseHandle(t);return FALSE;}SetLastError(0);if(!AdjustTokenPrivileges(t,FALSE,&p,0,NULL,NULL)||GetLastError()){CloseHandle(t);return FALSE;}CloseHandle(t);record("NORMAL_RESTART_REQUEST",0,0,0);return FlushFileBuffers(Log)&&ExitWindowsEx(EWX_REBOOT,0);}

void WINAPI mainCRTStartup(void){WNDCLASSA wc;WAIT_INSTALL wait_install;DWORD wait,i,x,y,start,id[8];BOOL ok;HGDIOBJ font;
 Log=CreateFileA("C:\\xwnmove137\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(Log==INVALID_HANDLE_VALUE)ExitProcess(91);record("ATTEMPT_ONCE",137,18,W*H);
 wait_install=(WAIT_INSTALL)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");if(!wait_install)ExitProcess(1);wait=wait_install(30000);record("INSTALL_IDLE_START",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(2);
 Screen=GetDC(NULL);if(!Screen)ExitProcess(3);GdiSetBatchLimit(1);
 zero(id,sizeof(id));if(ExtEscape(Screen,0x58574431,0,NULL,sizeof(id),(LPSTR)id)!=1||id[0]!=0x44525758||(id[1]!=110&&id[1]!=112)||id[2]!=1024||id[3]!=576||id[4]!=4096||id[5]!=32||id[6]!=2359296||id[7]!=1)ExitProcess(6);record("DRIVER_REVISION_GEOMETRY",id[1],id[2],id[3]);
 if(!image(&Ref,W,H)||!image(&Readback,W,H)||!image(&Background,W,H)||!image(&Source,128,80)||!image(&Pattern,128,80))ExitProcess(7);
 for(y=0;y<H;y++)for(x=0;x<W;x++)Background.bits[y*W+x]=base(x,y);
 for(y=0;y<80;y++)for(x=0;x<128;x++)Pattern.bits[y*128+x]=base(x+17,y+23);
 if(!BitBlt(Source.dc,0,0,128,80,Pattern.dc,0,0,SRCCOPY)||!text(Source.dc)||!GdiFlush())ExitProcess(8);
 font=SelectObject(Source.dc,GetStockObject(SYSTEM_FIXED_FONT));if(!font||!GetTextExtentPoint32A(Source.dc,"XWN Move 137",12,&TextSize)||!SelectObject(Source.dc,font))ExitProcess(9);
 record("TEXT_SIZE_SOURCE",TextSize.cx,TextSize.cy,hash(Source.bits,128*80*4));if(!save("source.rgb",Source.bits,128*80*4))ExitProcess(10);
 zero(&wc,sizeof(wc));wc.style=CS_OWNDC;wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="XwnMove137";if(!RegisterClassA(&wc))ExitProcess(11);
 Window=CreateWindowExA(WS_EX_TOPMOST,wc.lpszClassName,"XWN native movement RAM0110/0112",WS_POPUP|WS_VISIBLE|WS_CLIPCHILDREN,0,0,1024,576,NULL,NULL,wc.hInstance,NULL);if(!Window)ExitProcess(12);
 Mover=CreateWindowExA(0,wc.lpszClassName,"Moving bitmap and text",WS_CHILD|WS_VISIBLE|WS_CLIPSIBLINGS,88,-24,128,80,Window,(HMENU)1,wc.hInstance,NULL);
 Block=CreateWindowExA(0,wc.lpszClassName,"Fixed occluder",WS_CHILD|WS_VISIBLE|WS_CLIPSIBLINGS,144,56,96,144,Window,(HMENU)2,wc.hInstance,NULL);
 Arrow=LoadCursorA(NULL,IDC_ARROW);if(!Mover||!Block||!Arrow||!SetWindowPos(Block,HWND_TOP,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE))ExitProcess(13);
 SetForegroundWindow(Window);if(!redraw())ExitProcess(14);start=GetTickCount();while(GetTickCount()-start<2000){if(!pump())ExitProcess(15);Sleep(20);}
 {POINT origin={0,0};RECT wr;if(!ClientToScreen(Window,&origin)||!GetWindowRect(Window,&wr))ExitProcess(20);record("PARENT_ORIGIN",(DWORD)origin.x,(DWORD)origin.y,0);record("PARENT_SIZE",wr.right-wr.left,wr.bottom-wr.top,0);}
 for(i=0;i<18;i++)if(!one(i)){record("HARNESS_FAILURE",i,GetLastError(),Stage);if(restart()){CloseHandle(Log);ExitProcess(16);}ExitProcess(17);}
 ok=DestroyWindow(Window);ok=release(&Ref)&&ok;ok=release(&Readback)&&ok;ok=release(&Source)&&ok;ok=release(&Pattern)&&ok;ok=release(&Background)&&ok;ok=(ReleaseDC(NULL,Screen)!=0)&&ok;record("RELEASED",ok,0,0);if(!ok)Failures++;
 record("COMPLETE",Failures,18,18*W*H*2);wait=wait_install(30000);record("INSTALL_IDLE_END",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(18);
 if(!restart()){record("RESTART_FAILURE",GetLastError(),0,0);ExitProcess(19);}CloseHandle(Log);ExitProcess(0);
}
