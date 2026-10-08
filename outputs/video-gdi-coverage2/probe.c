/* Real GDI operations against a separate DIB reference. No direct rendering hooks. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#define W 384
#define H 256
#define CASES 26
#define BYTES (W*H*4)
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
typedef struct {HDC dc;HBITMAP bm;HGDIOBJ old;BYTE *bits;int bytes;} IMAGE;
static HANDLE Log;
static HWND Window;
static HDC Screen;
static IMAGE Ref,Readback,Source,Source24;
static HBITMAP Mask;
static DWORD Failures,Stage;
static RECT LastClip;
static int LastClipType,LastEscape;
static BOOL LastFlush;
static DWORD LastStats[32];
static void zero(void *p,DWORD n){volatile BYTE *b=p;while(n--)*b++=0;}
static DWORD hash(const void *p,DWORD n){const BYTE *b=p;DWORD v=2166136261u;while(n--)v=(v^*b++)*16777619u;return v;}
static void record(const char *s,DWORD a,DWORD b,DWORD c){char t[200];DWORD n,w;n=wsprintfA(t,"%s %lu %lu %lu\r\n",s,a,b,c);if(!WriteFile(Log,t,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM a,LPARAM b){if(m==WM_PAINT){PAINTSTRUCT p;BeginPaint(w,&p);EndPaint(w,&p);return 0;}if(m==WM_ERASEBKGND)return 1;return DefWindowProcA(w,m,a,b);}
static BOOL visible(void){MSG m;RECT r;while(PeekMessageA(&m,NULL,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessageA(&m);}return (LastClipType=GetClipBox(Screen,&r),LastClip=r,LastClipType)==SIMPLEREGION&&r.left<=0&&r.top<=0&&r.right>=W&&r.bottom>=H;}
static BOOL image(IMAGE *im,int w,int h,int bpp){BITMAPINFO bi;zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);bi.bmiHeader.biWidth=w;bi.bmiHeader.biHeight=-h;bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=(WORD)bpp;im->bytes=((w*bpp+31)/32)*4*h;im->dc=CreateCompatibleDC(Screen);im->bm=CreateDIBSection(Screen,&bi,DIB_RGB_COLORS,(void**)&im->bits,NULL,0);if(!im->dc||!im->bm)return FALSE;im->old=SelectObject(im->dc,im->bm);return im->old&&im->old!=HGDI_ERROR;}
static BOOL release(IMAGE *im){BOOL ok=TRUE;if(im->dc&&im->old)ok=SelectObject(im->dc,im->old)!=NULL;if(im->bm)ok=DeleteObject(im->bm)&&ok;if(im->dc)ok=DeleteDC(im->dc)&&ok;return ok;}
static DWORD base(int x,int y){return (((x*3+y*5)&255)<<16)|(((x*7+y*11)&255)<<8)|((x*13+y*17)&255);}
static BOOL stats(DWORD *d){DWORD i;zero(d,128);LastFlush=GdiFlush();if(!LastFlush)return FALSE;LastEscape=ExtEscape(Screen,0x58574432,0,NULL,128,(LPSTR)d);for(i=0;i<32;i++)LastStats[i]=d[i];return LastEscape==1&&d[0]==0x53525758&&d[1]==109&&d[20]==1;}

__declspec(dllexport) __attribute__((noinline,noclone,used,externally_visible)) DWORD __cdecl XwnGdiShot(DWORD index,DWORD reference,LONG x,LONG y,DWORD width,DWORD height,DWORD stride,DWORD digest){__asm__ volatile("":::"memory");return index^reference^(DWORD)x^(DWORD)y^width^height^stride^digest;}

static BOOL draw(HDC dc,DWORD n){
 int saved=SaveDC(dc);BOOL ok=TRUE;HBRUSH brush=NULL;HPEN pen=NULL;HRGN r=NULL,r2=NULL;
 POINT points[]={{20,20},{310,40},{40,220},{340,210},{60,100}};
 RECT text={20,40,330,110};BLENDFUNCTION blend={AC_SRC_OVER,0,128,0};
 TRIVERTEX v[]={{20,20,0xffff,0,0,0},{330,220,0,0xffff,0xffff,0},{40,225,0,0,0xffff,0}};
 GRADIENT_RECT gr={0,1};GRADIENT_TRIANGLE gt={0,1,2};
 if(!saved)return FALSE;
 brush=(n==1||n==13||n==25)?CreateHatchBrush(HS_DIAGCROSS,RGB(233,91,27)):CreateSolidBrush(RGB(43,199,87));
 pen=CreatePen(n==9?PS_DASH:PS_SOLID,n==10?3:1,RGB(221,37,151));
 if(!brush||!pen||!SelectObject(dc,brush)||!SelectObject(dc,pen)||!SelectObject(dc,GetStockObject(SYSTEM_FIXED_FONT)))ok=FALSE;
 if(!SetBrushOrgEx(dc,0,0,NULL)||!SetBkMode(dc,OPAQUE)||SetBkColor(dc,RGB(16,32,48))==CLR_INVALID||SetTextColor(dc,RGB(245,173,61))==CLR_INVALID||!SetStretchBltMode(dc,COLORONCOLOR))ok=FALSE;
 if(ok)switch(n){
 case 0:ok=PatBlt(dc,17,19,290,190,PATCOPY);break;
 case 1:ok=PatBlt(dc,17,19,290,190,PATINVERT);break;
 case 2:ok=BitBlt(dc,47,51,128,96,Source.dc,0,0,SRCINVERT);break;
 case 3:ok=MaskBlt(dc,47,51,128,96,Source.dc,0,0,Mask,0,0,MAKEROP4(SRCCOPY,DSTINVERT));break;
 case 4:ok=StretchBlt(dc,25,21,310,210,Source.dc,0,0,128,96,SRCCOPY);break;
 case 5:ok=StretchBlt(dc,335,21,-310,210,Source.dc,0,0,128,96,SRCCOPY);break;
 case 6:ok=PlgBlt(dc,points,Source.dc,0,0,128,96,NULL,0,0);break;
 case 7:ok=PlgBlt(dc,points,Source.dc,0,0,128,96,Mask,0,0);break;
 case 8:ok=MoveToEx(dc,20,20,NULL)&&LineTo(dc,331,217);break;
 case 9:ok=Polyline(dc,points,5);break;
 case 10:ok=BeginPath(dc)&&MoveToEx(dc,20,20,NULL)&&PolyBezierTo(dc,points+1,3)&&EndPath(dc)&&StrokePath(dc);break;
 case 11:ok=SetPolyFillMode(dc,WINDING)&&BeginPath(dc)&&Polygon(dc,points,5)&&EndPath(dc)&&FillPath(dc);break;
 case 12:ok=BeginPath(dc)&&Ellipse(dc,31,27,330,220)&&EndPath(dc)&&StrokeAndFillPath(dc);break;
 case 13:r=CreateEllipticRgn(20,20,340,230);ok=r&&PaintRgn(dc,r);break;
 case 14:ok=ExtTextOutA(dc,27,55,ETO_OPAQUE|ETO_CLIPPED,&text,"Xbox NT5: opaque text 012345",27,NULL);break;
 case 15:ok=SetBkMode(dc,TRANSPARENT)&&TextOutA(dc,27,55,"Xbox NT5: transparent 012345",27);break;
 case 16:ok=GradientFill(dc,v,2,&gr,1,GRADIENT_FILL_RECT_H);break;
 case 17:ok=GradientFill(dc,v,3,&gt,1,GRADIENT_FILL_TRIANGLE);break;
 case 18:ok=AlphaBlend(dc,31,29,300,200,Source.dc,0,0,128,96,blend);break;
 case 19:blend.SourceConstantAlpha=255;blend.AlphaFormat=AC_SRC_ALPHA;ok=AlphaBlend(dc,31,29,300,200,Source.dc,0,0,128,96,blend);break;
 case 20:ok=TransparentBlt(dc,31,29,300,200,Source.dc,0,0,128,96,RGB(0,0,0));break;
 case 21:ok=BitBlt(dc,47,51,128,96,Source24.dc,0,0,SRCCOPY);break;
 case 22:r=CreateRectRgn(20,20,300,220);r2=CreateEllipticRgn(70,50,250,190);ok=r&&r2&&CombineRgn(r,r,r2,RGN_DIFF)!=ERROR&&SelectClipRgn(dc,r)!=ERROR&&StretchBlt(dc,0,0,W,H,Source.dc,0,0,128,96,SRCINVERT);break;
 case 23:r=CreateRectRgn(0,0,0,0);ok=r&&SelectClipRgn(dc,r)==NULLREGION&&PatBlt(dc,0,0,W,H,PATCOPY);break;
 case 24:ok=IntersectClipRect(dc,0,0,90,70)!=ERROR&&BitBlt(dc,-20,-10,128,96,Source.dc,0,0,SRCCOPY);break;
 case 25:ok=RoundRect(dc,21,23,341,229,45,39);break;
 default:ok=FALSE;break;
 }
 if(!GdiFlush())ok=FALSE;
 if(!RestoreDC(dc,saved))ok=FALSE;
 if(r)ok=DeleteObject(r)&&ok;
 if(r2)ok=DeleteObject(r2)&&ok;
 if(brush)ok=DeleteObject(brush)&&ok;
 if(pen)ok=DeleteObject(pen)&&ok;
 return ok;
}

static BOOL save_ref(DWORD n,DWORD digest){char name[80];HANDLE f;DWORD written;BOOL ok;wsprintfA(name,"C:\\xwngdi119\\ref%02lu.rgb",n);f=CreateFileA(name,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(f==INVALID_HANDLE_VALUE)return FALSE;ok=WriteFile(f,Ref.bits,BYTES,&written,NULL)&&written==BYTES&&FlushFileBuffers(f)&&hash(Ref.bits,BYTES)==digest;return CloseHandle(f)&&ok;}
static BOOL one(DWORD n){DWORD i,x,y,refpre[32],pre[32],post[32],source_hash,source24_hash,reference_hash,bad=0,changed=0;BOOL a,b;POINT pt={0,0};
 Stage=1;if(!visible())return FALSE;
 Stage=2;if(!GdiFlush())return FALSE;
 for(y=0;y<H;y++)for(x=0;x<W;x++)((DWORD*)Ref.bits)[y*W+x]=base(x,y);
 for(y=0;y<96;y++)for(x=0;x<128;x++){DWORD c=base(x,y)&0xfefefe;c=(c>>1)&0x7f7f7f;if((x/8+y/8)%3==0)c=0;((DWORD*)Source.bits)[y*128+x]=0x80000000|c;Source24.bits[(y*128+x)*3]=(BYTE)c;Source24.bits[(y*128+x)*3+1]=(BYTE)(c>>8);Source24.bits[(y*128+x)*3+2]=(BYTE)(c>>16);}
 Stage=3;if(!BitBlt(Screen,0,0,W,H,Ref.dc,0,0,SRCCOPY))return FALSE;
 Stage=4;if(!GdiFlush())return FALSE;
 source_hash=hash(Source.bits,Source.bytes);source24_hash=hash(Source24.bits,Source24.bytes);
 Stage=5;if(!stats(refpre))return FALSE;
 a=draw(Ref.dc,n);reference_hash=hash(Ref.bits,BYTES);
 for(y=0;y<H;y++)for(x=0;x<W;x++)changed+=((((DWORD*)Ref.bits)[y*W+x]&0xffffff)!=base(x,y));
 Stage=6;if(!stats(pre))return FALSE;
 b=draw(Screen,n);Stage=7;if(!stats(post))return FALSE;
 Stage=8;if(!BitBlt(Readback.dc,0,0,W,H,Screen,0,0,SRCCOPY))return FALSE;
 Stage=9;if(!GdiFlush())return FALSE;
 for(i=0;i<W*H;i++)bad+=((((DWORD*)Readback.bits)[i]^((DWORD*)Ref.bits)[i])&0xffffff)!=0;
 record("CASE_API",n,a,b);record("PIXELS_BAD_CHANGED",W*H,bad,changed);
 record("REFERENCE_HASH_BYTES",reference_hash,BYTES,hash(Ref.bits,BYTES));
 record("SOURCE32_HASH_PAIR",source_hash,hash(Source.bits,Source.bytes),0);
 record("SOURCE24_HASH_PAIR",source24_hash,hash(Source24.bits,Source24.bytes),0);
 record("COHERENCE_ACTIVE",post[19],post[20],0);
 Stage=10;for(i=0;i<14;i++){if(pre[i+2]<refpre[i+2])return FALSE;record("REFERENCE_CALLBACK_DELTA",i,pre[i+2]-refpre[i+2],0);if(pre[i+2]!=refpre[i+2])Failures++;}
 for(i=0;i<14;i++){if(post[i+2]<pre[i+2])return FALSE;record("CALLBACK_DELTA",i,post[i+2]-pre[i+2],0);}
 if(!a||!b||bad||(n==23?changed!=0:changed==0)||post[19]||post[20]!=1||hash(Ref.bits,BYTES)!=reference_hash||hash(Source.bits,Source.bytes)!=source_hash||hash(Source24.bits,Source24.bytes)!=source24_hash)Failures++;
 Stage=11;if(!save_ref(n,reference_hash))return FALSE;
 Stage=12;if(!FlushFileBuffers(Log))return FALSE;
 Stage=13;if(!ClientToScreen(Window,&pt))return FALSE;
 XwnGdiShot(n,(DWORD)Ref.bits,pt.x,pt.y,W,H,W*4,reference_hash);
 return TRUE;
}
static BOOL restart(void){HANDLE t,v;TOKEN_PRIVILEGES p;v=CreateFileA("\\\\.\\C:",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);if(v==INVALID_HANDLE_VALUE)return FALSE;if(!FlushFileBuffers(v)){CloseHandle(v);return FALSE;}CloseHandle(v);if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&t))return FALSE;p.PrivilegeCount=1;p.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&p.Privileges[0].Luid)){CloseHandle(t);return FALSE;}SetLastError(0);if(!AdjustTokenPrivileges(t,FALSE,&p,0,NULL,NULL)||GetLastError()){CloseHandle(t);return FALSE;}CloseHandle(t);record("NORMAL_RESTART_REQUEST",0,0,0);if(!FlushFileBuffers(Log))return FALSE;return ExitWindowsEx(EWX_REBOOT,0);}
void WINAPI mainCRTStartup(void){WNDCLASSA wc;WAIT_INSTALL wait_install;DWORD wait,i,start,id[8];BYTE mask[16*96];BOOL ok;
 Log=CreateFileA("C:\\xwngdi119\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(Log==INVALID_HANDLE_VALUE)ExitProcess(91);record("ATTEMPT_ONCE",119,CASES,W*H);
 wait_install=(WAIT_INSTALL)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");if(!wait_install)ExitProcess(1);wait=wait_install(30000);record("INSTALL_IDLE_START",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(2);
 zero(&wc,sizeof(wc));wc.style=CS_OWNDC;wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="XwnGdiCoverage118";if(!RegisterClassA(&wc))ExitProcess(3);
 Window=CreateWindowExA(WS_EX_TOPMOST,wc.lpszClassName,"XWN GDI independent DIB reference",WS_OVERLAPPED|WS_CAPTION|WS_VISIBLE,20,20,430,310,NULL,NULL,wc.hInstance,NULL);if(!Window)ExitProcess(4);SetForegroundWindow(Window);UpdateWindow(Window);Screen=GetDC(Window);if(!Screen)ExitProcess(5);GdiSetBatchLimit(1);
 zero(id,sizeof(id));if(ExtEscape(Screen,0x58574431,0,NULL,sizeof(id),(LPSTR)id)!=1||id[0]!=0x44525758||id[1]!=109||id[2]!=1024||id[3]!=576||id[4]!=4096||id[5]!=32||id[6]!=2359296||id[7]!=1)ExitProcess(6);record("DRIVER_REVISION_GEOMETRY",id[1],id[2],id[3]);
 if(!image(&Ref,W,H,32)||!image(&Readback,W,H,32)||!image(&Source,128,96,32)||!image(&Source24,128,96,24))ExitProcess(7);
 for(i=0;i<sizeof(mask);i++)mask[i]=(BYTE)((i/16)%2?0x55:0xaa);
 Mask=CreateBitmap(128,96,1,1,mask);if(!Mask)ExitProcess(8);
 if(!SetCursorPos(1000,550)||!GdiFlush())ExitProcess(9);
 record("CURSOR_PARKED",1000,550,0);
 start=GetTickCount();while(GetTickCount()-start<2000){visible();Sleep(20);}
 for(i=0;i<CASES;i++)if(!one(i)){record("HARNESS_FAILURE",i,GetLastError(),Stage);record("FAIL_CLIP_TYPE_LEFT_TOP",LastClipType,LastClip.left,LastClip.top);record("FAIL_CLIP_RIGHT_BOTTOM",LastClip.right,LastClip.bottom,0);if(Stage>=5&&Stage<=7){record("FAIL_STATS_FLUSH_ESCAPE",LastFlush,LastEscape,0);record("FAIL_STATS_MAGIC_REV_ACTIVE",LastStats[0],LastStats[1],LastStats[20]);}FlushFileBuffers(Log);if(restart()){CloseHandle(Log);ExitProcess(10);}record("FAIL_RESTART",GetLastError(),0,0);FlushFileBuffers(Log);ExitProcess(10);}
 ok=release(&Ref);ok=release(&Readback)&&ok;ok=release(&Source)&&ok;ok=release(&Source24)&&ok;ok=DeleteObject(Mask)&&ok;ok=(ReleaseDC(Window,Screen)!=0)&&ok;ok=DestroyWindow(Window)&&ok;record("RELEASED",ok,0,0);if(!ok)Failures++;
 record("COMPLETE",Failures,CASES,CASES*W*H);wait=wait_install(30000);record("INSTALL_IDLE_END",wait,0,0);if(wait!=WAIT_OBJECT_0){FlushFileBuffers(Log);ExitProcess(11);}
 if(!restart()){record("RESTART_FAILURE",GetLastError(),0,0);FlushFileBuffers(Log);ExitProcess(12);}CloseHandle(Log);ExitProcess(0);
}
