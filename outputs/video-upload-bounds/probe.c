/* Controlled real GDI upload baseline; unchanged RAM0109. GPL-2.0-or-later. */
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
static IMAGE Ref,Readback,Source;
static DWORD Failures,Stage;
static RECT LastClip;
static int LastClipType;
static void zero(void *p,DWORD n){volatile BYTE *b=p;while(n--)*b++=0;}
static DWORD hash(const void *p,DWORD n){const BYTE *b=p;DWORD v=2166136261u;while(n--)v=(v^*b++)*16777619u;return v;}
static void record(const char *s,DWORD a,DWORD b,DWORD c){char t[160];DWORD n,w;n=wsprintfA(t,"%s %lu %lu %lu\r\n",s,a,b,c);if(!WriteFile(Log,t,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM a,LPARAM b){if(m==WM_SETCURSOR){SetCursor(NULL);return TRUE;}if(m==WM_PAINT){PAINTSTRUCT p;BeginPaint(w,&p);EndPaint(w,&p);return 0;}if(m==WM_ERASEBKGND)return 1;return DefWindowProcA(w,m,a,b);}
static BOOL visible(void){MSG m;while(PeekMessageA(&m,NULL,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessageA(&m);}LastClipType=GetClipBox(Screen,&LastClip);return LastClipType==SIMPLEREGION&&LastClip.left<=0&&LastClip.top<=0&&LastClip.right>=W&&LastClip.bottom>=H;}
static BOOL uncover(void){DWORD start=GetTickCount();do{visible();if(!SetWindowPos(Window,HWND_TOPMOST,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_SHOWWINDOW))return FALSE;Sleep(200);if(visible())return TRUE;}while(GetTickCount()-start<10000);return FALSE;}
static BOOL image(IMAGE *im,int w,int h){BITMAPINFO bi;zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);bi.bmiHeader.biWidth=w;bi.bmiHeader.biHeight=-h;bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;im->dc=CreateCompatibleDC(Screen);im->bm=CreateDIBSection(Screen,&bi,DIB_RGB_COLORS,(void**)&im->bits,NULL,0);if(!im->dc||!im->bm)return FALSE;im->old=SelectObject(im->dc,im->bm);return im->old&&im->old!=HGDI_ERROR;}
static BOOL release(IMAGE *im){BOOL ok=SelectObject(im->dc,im->old)!=NULL;ok=DeleteObject(im->bm)&&ok;return DeleteDC(im->dc)&&ok;}
static DWORD base(int x,int y){return (((x*3+y*5)&255)<<16)|(((x*7+y*11)&255)<<8)|((x*13+y*17)&255);}
static BOOL stats(DWORD *d){zero(d,128);return GdiFlush()&&ExtEscape(Screen,0x58574432,0,NULL,128,(LPSTR)d)==1&&d[0]==0x53525758&&d[1]==109&&d[19]==0&&d[20]==1;}
static BOOL draw(HDC dc,DWORD kind){
 int saved=SaveDC(dc);BOOL ok=TRUE;HBRUSH brush=CreateSolidBrush(RGB(43,199,87));HPEN pen=CreatePen(PS_SOLID,1,RGB(221,37,151));HRGN r=NULL,q=NULL;
 if(!saved||!brush||!pen||!SelectObject(dc,brush)||!SelectObject(dc,pen)||!SetStretchBltMode(dc,COLORONCOLOR))return FALSE;
 switch(kind){
 case 0:ok=PatBlt(dc,20,20,32,16,PATCOPY);break;
 case 1:ok=MoveToEx(dc,20,20,NULL)&&LineTo(dc,52,20);break;
 case 2:ok=IntersectClipRect(dc,20,20,52,21)!=ERROR&&MoveToEx(dc,20,20,NULL)&&LineTo(dc,52,20);break;
 case 3:ok=BitBlt(dc,40,40,128,96,dc,20,20,SRCCOPY);break;
 case 4:r=CreateRectRgn(20,20,36,36);q=CreateRectRgn(200,160,216,176);ok=r&&q&&CombineRgn(r,r,q,RGN_OR)==COMPLEXREGION&&SelectClipRgn(dc,r)==COMPLEXREGION&&PatBlt(dc,0,0,W,H,PATCOPY);break;
 case 5:ok=StretchBlt(dc,20,20,32,16,Source.dc,0,0,8,8,SRCCOPY);break;
 default:ok=FALSE;
 }
 ok=GdiFlush()&&ok;ok=RestoreDC(dc,saved)&&ok;
 if(r)ok=DeleteObject(r)&&ok;
 if(q)ok=DeleteObject(q)&&ok;
 ok=DeleteObject(brush)&&ok;return DeleteObject(pen)&&ok;
}
static BOOL save_ref(DWORD n,DWORD digest){char path[80];HANDLE f;DWORD written;BOOL ok;wsprintfA(path,"C:\\xwnupload128\\ref%02lu.rgb",n);f=CreateFileA(path,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(f==INVALID_HANDLE_VALUE)return FALSE;ok=WriteFile(f,Ref.bits,BYTES,&written,NULL)&&written==BYTES&&FlushFileBuffers(f)&&hash(Ref.bits,BYTES)==digest;return CloseHandle(f)&&ok;}
static BOOL one(DWORD n){DWORD i,x,y,first[32],idle[32],pre[32],post[32],digest,bad=0,changed=0,source_hash;BOOL a,b;
 Stage=1;if(!uncover()){record("FAIL_CLIP_TYPE_LEFT_TOP",LastClipType,LastClip.left,LastClip.top);record("FAIL_CLIP_RIGHT_BOTTOM",LastClip.right,LastClip.bottom,0);return FALSE;}
 record("CLIP_TYPE_LEFT_TOP",LastClipType,LastClip.left,LastClip.top);record("CLIP_RIGHT_BOTTOM",LastClip.right,LastClip.bottom,n);
 for(y=0;y<H;y++)for(x=0;x<W;x++)Ref.bits[y*W+x]=base(x,y);
 for(i=0;i<64;i++)Source.bits[i]=0x2bc757;
 Stage=2;if(!BitBlt(Screen,0,0,W,H,Ref.dc,0,0,SRCCOPY)||!GdiFlush())return FALSE;
 source_hash=hash(Source.bits,256);
 Stage=3;if(!stats(first)||!stats(idle))return FALSE;
 a=draw(Ref.dc,n%6);digest=hash(Ref.bits,BYTES);
 Stage=4;if(!stats(pre))return FALSE;
 b=draw(Screen,n%6);
 Stage=5;if(!stats(post))return FALSE;
 Stage=6;if(!BitBlt(Readback.dc,0,0,W,H,Screen,0,0,SRCCOPY)||!GdiFlush())return FALSE;
 for(y=0;y<H;y++)for(x=0;x<W;x++){i=y*W+x;bad+=((Ref.bits[i]^Readback.bits[i])&0xffffff)!=0;changed+=(Ref.bits[i]&0xffffff)!=base(x,y);}
 record("CASE_API",n,a,b);record("PIXELS_BAD_CHANGED",W*H,bad,changed);record("REFERENCE_HASH_BYTES",digest,BYTES,hash(Ref.bits,BYTES));record("SOURCE_HASH_PAIR",source_hash,hash(Source.bits,256),0);
 for(i=2;i<=18;i++){record("QUIET_COUNTER",i,first[i],idle[i]);record("REFERENCE_COUNTER",i,idle[i],pre[i]);record("DRAW_COUNTER",i,pre[i],post[i]);}
 record("COHERENCE_ACTIVE",post[19],post[20],0);
 if(!a||!b||bad||!changed||digest!=hash(Ref.bits,BYTES)||source_hash!=hash(Source.bits,256))Failures++;
 Stage=7;return save_ref(n,digest);
}
static BOOL restart(void){HANDLE t,v;TOKEN_PRIVILEGES p;v=CreateFileA("\\\\.\\C:",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);if(v==INVALID_HANDLE_VALUE)return FALSE;if(!FlushFileBuffers(v)){CloseHandle(v);return FALSE;}CloseHandle(v);if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&t))return FALSE;p.PrivilegeCount=1;p.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&p.Privileges[0].Luid)){CloseHandle(t);return FALSE;}SetLastError(0);if(!AdjustTokenPrivileges(t,FALSE,&p,0,NULL,NULL)||GetLastError()){CloseHandle(t);return FALSE;}CloseHandle(t);record("NORMAL_RESTART_REQUEST",0,0,0);return FlushFileBuffers(Log)&&ExitWindowsEx(EWX_REBOOT,0);}
void WINAPI mainCRTStartup(void){WNDCLASSA wc;WAIT_INSTALL wait_install;DWORD wait,i,start,id[8];BOOL ok;
 Log=CreateFileA("C:\\xwnupload128\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(Log==INVALID_HANDLE_VALUE)ExitProcess(91);record("ATTEMPT_ONCE",128,18,W*H);
 wait_install=(WAIT_INSTALL)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");if(!wait_install)ExitProcess(1);wait=wait_install(30000);record("INSTALL_IDLE_START",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(2);
 zero(&wc,sizeof(wc));wc.style=CS_OWNDC;wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="XwnUpload128";if(!RegisterClassA(&wc))ExitProcess(3);
 Window=CreateWindowExA(WS_EX_TOPMOST,wc.lpszClassName,"XWN unchanged-driver upload baseline",WS_POPUP|WS_VISIBLE,0,0,1024,576,NULL,NULL,wc.hInstance,NULL);if(!Window)ExitProcess(4);SetForegroundWindow(Window);UpdateWindow(Window);Screen=GetDC(Window);if(!Screen)ExitProcess(5);GdiSetBatchLimit(1);SetCursor(NULL);
 zero(id,sizeof(id));if(ExtEscape(Screen,0x58574431,0,NULL,sizeof(id),(LPSTR)id)!=1||id[0]!=0x44525758||id[1]!=109||id[2]!=1024||id[3]!=576||id[4]!=4096||id[5]!=32||id[6]!=2359296||id[7]!=1)ExitProcess(6);record("DRIVER_REVISION_GEOMETRY",id[1],id[2],id[3]);
 if(!image(&Ref,W,H)||!image(&Readback,W,H)||!image(&Source,8,8))ExitProcess(7);
 start=GetTickCount();while(GetTickCount()-start<2000){visible();Sleep(20);}
 for(i=0;i<18;i++)if(!one(i)){record("HARNESS_FAILURE",i,GetLastError(),Stage);if(restart()){CloseHandle(Log);ExitProcess(10);}record("FAIL_RESTART",GetLastError(),0,0);ExitProcess(11);}
 ok=release(&Ref);ok=release(&Readback)&&ok;ok=release(&Source)&&ok;ok=(ReleaseDC(Window,Screen)!=0)&&ok;ok=DestroyWindow(Window)&&ok;record("RELEASED",ok,0,0);if(!ok)Failures++;
 record("COMPLETE",Failures,18,18*W*H);wait=wait_install(30000);record("INSTALL_IDLE_END",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(12);
 if(!restart()){record("RESTART_FAILURE",GetLastError(),0,0);ExitProcess(13);}CloseHandle(Log);ExitProcess(0);
}
