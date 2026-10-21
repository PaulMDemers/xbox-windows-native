/* SPDX-License-Identifier: MIT
 * NT5 boot geometry and GDI readback probe. No mode switch or registry edit. */
#define WIN32_LEAN_AND_MEAN
#define COBJMACROS
#include <windows.h>
#include <ddraw.h>
#include <winioctl.h>
#include <ntddvdeo.h>
void *memset(void *p,int value,size_t n){volatile unsigned char *q=p;while(n--)*q++=(unsigned char)value;return p;}
static HANDLE logh;
static unsigned failures;
static void item(const char *key,DWORD value) {
 char b[160];DWORD n,w;
 n=(DWORD)wsprintfA(b,"%s=%lu\r\n",key,value);
 if(!WriteFile(logh,b,n,&w,0)||w!=n||!FlushFileBuffers(logh))ExitProcess(90);
}
static void check(const char *key,BOOL yes){item(key,yes?1:0);if(!yes)++failures;}
static DWORD pixel(unsigned x,unsigned y) {
 return ((x*17u+y*3u)&255u)<<16|((y*29u+x*7u)&255u)<<8|((x^y^0x5au)&255u);
}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM a,LPARAM b){return DefWindowProcA(w,m,a,b);}
static void pump(void){MSG m;while(PeekMessageA(&m,0,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessageA(&m);}}
static void primary_pitch(HWND w){
 LPDIRECTDRAW dd=0;LPDIRECTDRAWSURFACE s=0;DDSURFACEDESC d={0};HRESULT hr;
 hr=DirectDrawCreate(0,&dd,0);item("dd.create",(DWORD)hr);if(FAILED(hr)){++failures;return;}
 hr=IDirectDraw_SetCooperativeLevel(dd,w,DDSCL_NORMAL);item("dd.cooperative",(DWORD)hr);
 if(SUCCEEDED(hr)){
  d.dwSize=sizeof(d);d.dwFlags=DDSD_CAPS;d.ddsCaps.dwCaps=DDSCAPS_PRIMARYSURFACE;
  hr=IDirectDraw_CreateSurface(dd,&d,&s,0);item("dd.primary",(DWORD)hr);
  if(SUCCEEDED(hr)){
   ZeroMemory(&d,sizeof(d));d.dwSize=sizeof(d);
   hr=IDirectDrawSurface_GetSurfaceDesc(s,&d);item("dd.describe",(DWORD)hr);
   if(SUCCEEDED(hr)){
    item("primary.flags",d.dwFlags);item("primary.width",d.dwWidth);item("primary.height",d.dwHeight);item("primary.pitch",(DWORD)d.lPitch);item("primary.bpp",d.ddpfPixelFormat.dwRGBBitCount);
    check("primary.geometry",(d.dwFlags&(DDSD_WIDTH|DDSD_HEIGHT|DDSD_PITCH|DDSD_PIXELFORMAT))==(DDSD_WIDTH|DDSD_HEIGHT|DDSD_PITCH|DDSD_PIXELFORMAT)&&d.dwWidth==720&&d.dwHeight==480&&d.lPitch==2880&&d.ddpfPixelFormat.dwRGBBitCount==32);
   }else ++failures;
   IDirectDrawSurface_Release(s);
  }else ++failures;
 }else ++failures;
 IDirectDraw_Release(dd);
}
static void miniport_query(void){
 DISPLAY_DEVICEA d={0};VIDEO_MODE_INFORMATION m={0};HANDLE h;DWORD bytes=0;BOOL ok;
 typedef char layout80[sizeof(VIDEO_MODE_INFORMATION)==80?1:-1];(void)sizeof(layout80);
 d.cb=sizeof(d);ok=EnumDisplayDevicesA(0,0,&d,0);item("miniport.enumerate",ok);
 if(!ok)return;
 h=CreateFileA(d.DeviceName,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,0,OPEN_EXISTING,0,0);
 item("miniport.open",h!=INVALID_HANDLE_VALUE);if(h==INVALID_HANDLE_VALUE){item("miniport.error",GetLastError());return;}
 ok=DeviceIoControl(h,IOCTL_VIDEO_QUERY_CURRENT_MODE,0,0,&m,sizeof(m),&bytes,0);item("miniport.query",ok);item("miniport.bytes",bytes);
 if(ok){item("miniport.width",m.VisScreenWidth);item("miniport.height",m.VisScreenHeight);item("miniport.pitch",m.ScreenStride);item("miniport.bpp",m.NumberOfPlanes*m.BitsPerPlane);check("miniport.geometry",bytes==sizeof(m)&&m.Length==sizeof(m)&&m.VisScreenWidth==720&&m.VisScreenHeight==480&&m.ScreenStride==2880&&m.NumberOfPlanes*m.BitsPerPlane==32);}
 else item("miniport.error",GetLastError());CloseHandle(h);
}
static void drawing(HWND w){
 BITMAPINFO bi={0};HDC dc=GetDC(w),src=0,dst=0;HBITMAP sb=0,db=0;HGDIOBJ os=0,od=0;
 DWORD *a=0,*b=0;unsigned x,y,pass;RECT r;
 if(!dc){check("draw.dc",FALSE);return;}
 GetClientRect(w,&r);check("draw.client",r.right==720&&r.bottom==480);
 bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);bi.bmiHeader.biWidth=720;bi.bmiHeader.biHeight=-480;
 bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;bi.bmiHeader.biCompression=BI_RGB;
 src=CreateCompatibleDC(dc);dst=CreateCompatibleDC(dc);
 sb=CreateDIBSection(dc,&bi,DIB_RGB_COLORS,(void**)&a,0,0);db=CreateDIBSection(dc,&bi,DIB_RGB_COLORS,(void**)&b,0,0);
 if(!src||!dst||!sb||!db){check("draw.allocate",FALSE);goto done;}
 os=SelectObject(src,sb);od=SelectObject(dst,db);
 for(y=0;y<480;++y)for(x=0;x<720;++x)a[y*720+x]=pixel(x,y);
 for(pass=0;pass<3;++pass){
  unsigned bad=0,first=0;char key[64];int sx=30,sy=40,dx=47,dy=53;
  if(pass==2){sx=47;sy=53;dx=30;dy=40;}
  check("draw.upload",BitBlt(dc,0,0,720,480,src,0,0,SRCCOPY));
  if(pass)check("draw.overlap",BitBlt(dc,dx,dy,200,120,dc,sx,sy,SRCCOPY));
  check("draw.flush",GdiFlush());
  check("draw.readback",BitBlt(dst,0,0,720,480,dc,0,0,SRCCOPY));check("readback.flush",GdiFlush());
  for(y=0;y<480;++y)for(x=0;x<720;++x){
   unsigned px=x,py=y;
   if(pass&&x>=(unsigned)dx&&x<(unsigned)(dx+200)&&y>=(unsigned)dy&&y<(unsigned)(dy+120)){px=x-dx+sx;py=y-dy+sy;}
   if((b[y*720+x]&0xffffffu)!=pixel(px,py)){if(!bad)first=y*720+x;++bad;}
  }
  wsprintfA(key,"pass%u.mismatches",pass);item(key,bad);
  if(bad){wsprintfA(key,"pass%u.first",pass);item(key,first);++failures;}
 }
done:
 if(os)SelectObject(src,os);if(od)SelectObject(dst,od);
 if(sb)DeleteObject(sb);if(db)DeleteObject(db);if(src)DeleteDC(src);if(dst)DeleteDC(dst);ReleaseDC(w,dc);
}
void WINAPI mainCRTStartup(void){
 WNDCLASSA wc={0};HWND w;DEVMODEA dm={0};HANDLE token;TOKEN_PRIVILEGES tp;BOOL restart;
 logh=CreateFileA("C:\\xwn480p638\\result.txt",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);
 if(logh==INVALID_HANDLE_VALUE)ExitProcess(91);
 item("case",638);item("begin.tick",GetTickCount());Sleep(10000);
 dm.dmSize=sizeof(dm);check("mode.query",EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&dm));
 item("mode.width",dm.dmPelsWidth);item("mode.height",dm.dmPelsHeight);item("mode.bpp",dm.dmBitsPerPel);item("mode.frequency",dm.dmDisplayFrequency);
 check("mode.expected",dm.dmPelsWidth==720&&dm.dmPelsHeight==480&&dm.dmBitsPerPel==32);
 item("screen.width",GetSystemMetrics(SM_CXSCREEN));item("screen.height",GetSystemMetrics(SM_CYSCREEN));
 wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleA(0);wc.lpszClassName="XWN480p638";
 check("window.class",RegisterClassA(&wc)!=0);
 w=CreateWindowExA(WS_EX_TOPMOST,wc.lpszClassName,"XWN 480p638 drawing",WS_POPUP|WS_VISIBLE,0,0,720,480,0,0,wc.hInstance,0);
 check("window.created",w!=0);
 if(w){SetForegroundWindow(w);ShowWindow(w,SW_SHOW);UpdateWindow(w);Sleep(1000);pump();primary_pitch(w);miniport_query();drawing(w);Sleep(2000);DestroyWindow(w);}
 item("failures",failures);item("complete",1);item("end.tick",GetTickCount());
 ZeroMemory(&tp,sizeof(tp));tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){item("restart.token",GetLastError());CloseHandle(logh);ExitProcess(92);}
 check("restart.lookup",LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid));
 SetLastError(0);check("restart.privilege",AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)&&GetLastError()==0);CloseHandle(token);
 item("restart.requesting",1);restart=ExitWindowsEx(EWX_REBOOT,0);item("restart.accepted",restart);CloseHandle(logh);ExitProcess(restart?failures:93);
}
