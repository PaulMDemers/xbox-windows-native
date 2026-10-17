/* SPDX-License-Identifier: MIT
 * Rung 03: an owned window/clipper/primary test. No exclusive mode or mode switch.
 * Paint handlers never draw the DirectDraw pattern: GDI supplies only guards.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define DIRECTDRAW_VERSION 0x0700
#define COBJMACROS
#include <windows.h>
#include <ddraw.h>
#define CW 256
#define CH 192
#define TW 128
#define TH 112
static const GUID iid7={0x15e65ec0,0x3b9c,0x11d2,{0xb9,0x2f,0,0x60,0x97,0x97,0xea,0x5b}};
static HANDLE logf=INVALID_HANDLE_VALUE,files[3]={INVALID_HANDLE_VALUE,INVALID_HANDLE_VALUE,INVALID_HANDLE_VALUE};
static HWND panel,target,cover;
static HBRUSH brushes[3];
static DWORD screen[CW*CH],source[TW*TH];
static unsigned stage;
static int io_error,cancelled;
static void zero(void *v,DWORD n){BYTE *p=v;while(n--)*p++=0;}
static int eq(const char *a,const char *b){return lstrcmpA(a,b)==0;}
static int put(HANDLE f,const void *p,DWORD n){DWORD w=0;if(!WriteFile(f,p,n,&w,0)||w!=n||!FlushFileBuffers(f)){io_error=1;return 0;}return 1;}
static void text(const char *k,const char *v){char b[256];wsprintfA(b,"%s=%s\r\n",k,v);put(logf,b,(DWORD)lstrlenA(b));}
static void number(const char *k,DWORD n){char b[32];wsprintfA(b,"%lu",n);text(k,b);}
static int call(const char *k,HRESULT hr){char b[16];wsprintfA(b,"%08lX",(DWORD)hr);text(k,b);return hr==DD_OK;}
static void snum(const char *k,DWORD n){char b[80];wsprintfA(b,"s%u.%s",stage,k);number(b,n);}
static int scall(const char *k,HRESULT hr){char b[80];wsprintfA(b,"s%u.%s",stage,k);return call(b,hr);}
static int token(const char **s,char *o,unsigned cap){const char *p=*s;unsigned n=0;int q=0;
 while(*p==' '||*p=='\t')p++;
 if(!*p){*s=p;return 0;}if(*p=='"'){q=1;p++;}
 while(*p&&(q?*p!='"':(*p!=' '&&*p!='\t'))){if(*p=='"'||n+1>=cap)return -1;o[n++]=*p++;}
 if(q){if(*p!='"')return -1;p++;if(*p&&*p!=' '&&*p!='\t')return -1;}
 o[n]=0;*s=p;return n?1:-1;
}
static HANDLE fresh(const char *p,const char *s){char b[256];if(lstrlenA(p)+lstrlenA(s)>=256)return INVALID_HANDLE_VALUE;lstrcpyA(b,p);lstrcatA(b,s);return CreateFileA(b,GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);}
static DWORD pattern(unsigned x,unsigned y,unsigned phase){unsigned c=((x/8)^(y/8)^phase)&7;return ((c&1)?0xff0000UL:0)|((c&2)?0xff00UL:0)|((c&4)?255:0);}
static int inrect(int x,int y,const RECT *r){return x>=r->left&&x<r->right&&y>=r->top&&y<r->bottom;}
static int covered(int x,int y){return (stage==1||stage==2)&&x>=48&&x<88&&y>=40&&y<72;}
static DWORD expected(unsigned x,unsigned y,int after){
 if(covered((int)x,(int)y))return 0xff00ffUL;
 if(x>=16&&x<112&&y>=16&&y<96)return after?pattern(x,y,stage):0;
 return 255;
}
static LRESULT CALLBACK wnd(HWND h,UINT m,WPARAM w,LPARAM l){
 if(m==WM_CLOSE){cancelled=1;return 0;}
 if(m==WM_ERASEBKGND)return 1;
 if(m==WM_PAINT){PAINTSTRUCT ps;RECT r;HDC dc=BeginPaint(h,&ps);GetClientRect(h,&r);FillRect(dc,&r,brushes[h==target?1:h==cover?2:0]);EndPaint(h,&ps);return 0;}
 return DefWindowProcA(h,m,w,l);
}
static void pump(DWORD ms){MSG m;DWORD start=GetTickCount();do{while(PeekMessageA(&m,0,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessageA(&m);}Sleep(5);}while(!cancelled&&(DWORD)(GetTickCount()-start)<ms);}
static int windows(void){WNDCLASSA c;HINSTANCE inst=GetModuleHandleA(0);zero(&c,sizeof(c));c.lpfnWndProc=wnd;c.hInstance=inst;c.lpszClassName="XWNPresent03";
 brushes[0]=CreateSolidBrush(RGB(0,0,255));brushes[1]=CreateSolidBrush(RGB(0,0,0));brushes[2]=CreateSolidBrush(RGB(255,0,255));
 if(!brushes[0]||!brushes[1]||!brushes[2]||!RegisterClassA(&c))return 0;
 panel=CreateWindowExA(WS_EX_TOPMOST|WS_EX_TOOLWINDOW,c.lpszClassName,"XWN DirectDraw presentation",WS_POPUP|WS_CLIPCHILDREN,64,64,CW,CH,0,0,inst,0);
 if(!panel)return 0;
 target=CreateWindowA(c.lpszClassName,"owned target",WS_CHILD|WS_VISIBLE|WS_CLIPSIBLINGS,16,16,96,80,panel,0,inst,0);
 cover=CreateWindowA(c.lpszClassName,"owned GDI occluder",WS_CHILD|WS_CLIPSIBLINGS,48,40,40,32,panel,0,inst,0);
 return target&&cover;
}
static int capture(int after,POINT origin){HDC dc=0,mem=0;HBITMAP bm=0;HGDIOBJ old=0;DWORD *bits=0;BITMAPINFO bi;unsigned i;DWORD bad=0;int ok=0,clean=1;char label[40];
 zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);bi.bmiHeader.biWidth=CW;bi.bmiHeader.biHeight=-CH;bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;
 dc=GetDC(0);if(!dc)goto done;mem=CreateCompatibleDC(dc);if(!mem)goto done;
 bm=CreateDIBSection(dc,&bi,DIB_RGB_COLORS,(void**)&bits,0,0);if(!bm||!bits)goto done;
 old=SelectObject(mem,bm);if(!old||old==HGDI_ERROR)goto done;
 if(!BitBlt(mem,0,0,CW,CH,dc,origin.x,origin.y,SRCCOPY)||!GdiFlush())goto done;
 for(i=0;i<CW*CH;i++){screen[i]=bits[i]&0xffffffUL;if(screen[i]!=expected(i%CW,i/CW,after))bad++;}
 if(!put(files[after?2:1],screen,sizeof(screen)))goto done;
 ok=1;
done:
 if(old&&old!=HGDI_ERROR)clean&=SelectObject(mem,old)!=0;
 if(bm)clean&=DeleteObject(bm)!=0;
 if(mem)clean&=DeleteDC(mem)!=0;
 if(dc)clean&=ReleaseDC(0,dc)!=0;
 wsprintfA(label,"%s.capture",after?"after":"before");snum(label,ok&&clean);
 wsprintfA(label,"%s.mismatches",after?"after":"before");snum(label,bad);
 return ok&&clean&&!bad;
}
static int clip(IDirectDrawClipper *c,POINT origin){struct {RGNDATAHEADER h;RECT r[64];} data;DWORD bytes=0,i;int x,y,bad=0;char label[64];
 if(!scall("clip.size",IDirectDrawClipper_GetClipList(c,0,0,&bytes)))return 0;
 snum("clip.bytes",bytes);if(bytes<sizeof(RGNDATAHEADER)||bytes>sizeof(data))return 0;
 zero(&data,sizeof(data));if(!scall("clip.list",IDirectDrawClipper_GetClipList(c,0,(RGNDATA*)&data,&bytes)))return 0;
 if(data.h.dwSize!=sizeof(RGNDATAHEADER)||data.h.iType!=RDH_RECTANGLES||!data.h.nCount||data.h.nCount>64||data.h.nRgnSize!=data.h.nCount*sizeof(RECT)||bytes!=sizeof(RGNDATAHEADER)+data.h.nRgnSize)return 0;
 snum("clip.count",data.h.nCount);
 for(i=0;i<data.h.nCount;i++){
  RECT *r=&data.r[i];
  if(r->left<origin.x+16||r->right>origin.x+112||r->top<origin.y+16||r->bottom>origin.y+96||r->left>=r->right||r->top>=r->bottom)bad=1;
#define EDGE(n) wsprintfA(label,"clip.r%lu." #n,i);snum(label,(DWORD)r->n)
  EDGE(left);EDGE(top);EDGE(right);EDGE(bottom);
#undef EDGE
 }
 for(y=0;y<CH;y++)for(x=0;x<CW;x++){unsigned found=0;int want=x>=16&&x<112&&y>=16&&y<96&&!covered(x,y);for(i=0;i<data.h.nCount;i++)found+=inrect(x+origin.x,y+origin.y,&data.r[i]);if(found!=(unsigned)want)bad=1;}
 snum("clip.exact",!bad);return !bad;
}
static int surface(IDirectDrawSurface7 *s,const DDPIXELFORMAT *pf,int write){DDSURFACEDESC2 d;DWORD x,y,bpp=pf->dwRGBBitCount/8;int valid,ok;zero(&d,sizeof(d));d.dwSize=sizeof(d);
 if(!scall(write?"source.write.lock":"source.read.lock",IDirectDrawSurface7_Lock(s,0,&d,DDLOCK_DONOTWAIT|(write?DDLOCK_WRITEONLY:DDLOCK_READONLY),0)))return 0;
 valid=d.lpSurface&&d.dwWidth==TW&&d.dwHeight==TH&&d.lPitch>0&&d.lPitch<=65536&&(DWORD)d.lPitch>=TW*bpp&&d.lPitch%(LONG)bpp==0&&d.ddpfPixelFormat.dwFlags==DDPF_RGB&&d.ddpfPixelFormat.dwRGBBitCount==pf->dwRGBBitCount&&d.ddpfPixelFormat.dwRBitMask==pf->dwRBitMask&&d.ddpfPixelFormat.dwGBitMask==pf->dwGBitMask&&d.ddpfPixelFormat.dwBBitMask==pf->dwBBitMask&&(d.ddsCaps.dwCaps&DDSCAPS_SYSTEMMEMORY)&&!(d.ddsCaps.dwCaps&DDSCAPS_VIDEOMEMORY);
 snum(write?"source.write.layout":"source.read.layout",valid);snum(write?"source.write.pitch":"source.read.pitch",(DWORD)d.lPitch);
 if(valid)for(y=0;y<TH;y++)for(x=0;x<TW;x++){
  BYTE *p=(BYTE*)d.lpSurface+y*d.lPitch+x*bpp;DWORD rgb=pattern(x,y,stage),v;
  if(write){v=((rgb&0xff0000)?pf->dwRBitMask:0)|((rgb&0xff00)?pf->dwGBitMask:0)|((rgb&255)?pf->dwBBitMask:0);if(bpp==2)*(WORD*)p=(WORD)v;else *(DWORD*)p=v;}
  else{v=bpp==2?*(WORD*)p:*(DWORD*)p;source[y*TW+x]=((v&pf->dwRBitMask)==pf->dwRBitMask?0xff0000UL:0)|((v&pf->dwGBitMask)==pf->dwGBitMask?0xff00UL:0)|((v&pf->dwBBitMask)==pf->dwBBitMask?255:0);if(v!=(((rgb&0xff0000)?pf->dwRBitMask:0)|((rgb&0xff00)?pf->dwGBitMask:0)|((rgb&255)?pf->dwBBitMask:0)))valid=0;}
 }
 ok=scall(write?"source.write.unlock":"source.read.unlock",IDirectDrawSurface7_Unlock(s,0));
 if(!write){snum("source.exact",valid);if(valid&&!put(files[0],source,sizeof(source)))valid=0;}
 return valid&&ok;
}
static int run(const char *backend){typedef HRESULT(WINAPI *CREATE)(GUID*,void**,REFIID,IUnknown*);union{FARPROC generic;CREATE create;}fn;
 HMODULE mod=0;IDirectDraw7 *dd=0;IDirectDrawSurface7 *primary=0,*src=0;IDirectDrawClipper *cl=0;DDSURFACEDESC2 d,mode;DDPIXELFORMAT pf;HWND associated=0;int ok=0,clean=1;GUID *choice=eq(backend,"hel")?(GUID*)DDCREATE_EMULATIONONLY:0;
 mod=LoadLibraryA("ddraw.dll");number("ddraw.load",mod!=0);if(!mod)goto done;
 fn.generic=GetProcAddress(mod,"DirectDrawCreateEx");number("ddraw.entry",fn.generic!=0);if(!fn.generic)goto done;
 if(!call("ddraw.create",fn.create(choice,(void**)&dd,&iid7,0)))goto done;
 if(!call("ddraw.cooperative",IDirectDraw7_SetCooperativeLevel(dd,panel,DDSCL_NORMAL)))goto done;
 zero(&mode,sizeof(mode));mode.dwSize=sizeof(mode);if(!call("ddraw.mode",IDirectDraw7_GetDisplayMode(dd,&mode)))goto done;
 number("mode.width",mode.dwWidth);number("mode.height",mode.dwHeight);number("mode.bpp",mode.ddpfPixelFormat.dwRGBBitCount);
 if(mode.dwWidth<640||mode.dwHeight<480)goto done;
 zero(&d,sizeof(d));d.dwSize=sizeof(d);d.dwFlags=DDSD_CAPS;d.ddsCaps.dwCaps=DDSCAPS_PRIMARYSURFACE;
 if(!call("primary.create",IDirectDraw7_CreateSurface(dd,&d,&primary,0)))goto done;
 zero(&pf,sizeof(pf));pf.dwSize=sizeof(pf);if(!call("primary.format",IDirectDrawSurface7_GetPixelFormat(primary,&pf)))goto done;
 number("format.flags",pf.dwFlags);number("format.bits",pf.dwRGBBitCount);number("format.red",pf.dwRBitMask);number("format.green",pf.dwGBitMask);number("format.blue",pf.dwBBitMask);
 if(pf.dwFlags!=DDPF_RGB||!((pf.dwRGBBitCount==32&&pf.dwRBitMask==0xff0000&&pf.dwGBitMask==0xff00&&pf.dwBBitMask==255)||(pf.dwRGBBitCount==16&&pf.dwBBitMask==31&&((pf.dwRBitMask==0xf800&&pf.dwGBitMask==0x7e0)||(pf.dwRBitMask==0x7c00&&pf.dwGBitMask==0x3e0)))))goto done;
 zero(&d,sizeof(d));d.dwSize=sizeof(d);d.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT|DDSD_PIXELFORMAT;d.dwWidth=TW;d.dwHeight=TH;d.ddsCaps.dwCaps=DDSCAPS_OFFSCREENPLAIN|DDSCAPS_SYSTEMMEMORY;d.ddpfPixelFormat=pf;
 if(!call("source.create",IDirectDraw7_CreateSurface(dd,&d,&src,0)))goto done;
 if(!call("clipper.create",IDirectDraw7_CreateClipper(dd,0,&cl,0)))goto done;
 if(!call("clipper.hwnd",IDirectDrawClipper_SetHWnd(cl,0,target)))goto done;
 if(!call("clipper.gethwnd",IDirectDrawClipper_GetHWnd(cl,&associated)))goto done;
 number("clipper.owner",associated==target);if(associated!=target)goto done;
 if(!call("primary.clipper",IDirectDrawSurface7_SetClipper(primary,cl)))goto done;
 for(stage=0;stage<4;stage++){
  POINT p={0,0};RECT rect,from={0,0,TW,TH},to;int moved=stage>=2;
  snum("cover.preabove",GetWindow(target,GW_HWNDPREV)==cover);
  if(!SetWindowPos(cover,HWND_TOP,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE|((stage==1||stage==2)?SWP_SHOWWINDOW:SWP_HIDEWINDOW)))goto done;
  if(!SetWindowPos(panel,HWND_TOPMOST,moved?144:64,moved?112:64,CW,CH,SWP_SHOWWINDOW))goto done;
  pump(100);if(cancelled)goto done;
  if(!RedrawWindow(panel,0,0,RDW_INVALIDATE|RDW_ERASE|RDW_ALLCHILDREN|RDW_UPDATENOW)||!GdiFlush())goto done;
  if(!ClientToScreen(panel,&p)||!GetClientRect(panel,&rect)||rect.right!=CW||rect.bottom!=CH||p.x!=(moved?144:64)||p.y!=(moved?112:64))goto done;
  snum("origin.x",(DWORD)p.x);snum("origin.y",(DWORD)p.y);snum("cover",stage==1||stage==2);
  snum("cover.visible",IsWindowVisible(cover)!=0);snum("cover.above",GetWindow(target,GW_HWNDPREV)==cover);
  if((IsWindowVisible(cover)!=0)!=(stage==1||stage==2)||GetWindow(target,GW_HWNDPREV)!=cover)goto done;
  if(!capture(0,p)||!clip(cl,p)||!surface(src,&pf,1)||!surface(src,&pf,0))goto done;
  to.left=p.x;to.top=p.y;to.right=p.x+TW;to.bottom=p.y+TH;
  if(!scall("primary.blit",IDirectDrawSurface7_Blt(primary,&to,src,&from,DDBLT_DONOTWAIT,0)))goto done;
  if(!GdiFlush())goto done;
  Sleep(100);if(!capture(1,p))goto done;
  snum("complete",1);pump(500);if(cancelled)goto done;
 }
 ok=1;
done:
 if(primary&&cl)clean&=call("primary.detach",IDirectDrawSurface7_SetClipper(primary,0));
 if(src)number("release.source",IDirectDrawSurface7_Release(src));
 if(primary)number("release.primary",IDirectDrawSurface7_Release(primary));
 if(cl)number("release.clipper",IDirectDrawClipper_Release(cl));
 if(dd)number("release.ddraw",IDirectDraw7_Release(dd));
 if(mod){int unloaded=FreeLibrary(mod)!=0;number("ddraw.unload",unloaded);clean&=unloaded;}
 return ok&&clean;
}
void WINAPI mainCRTStartup(void){const char *s=GetCommandLineA();char exe[512],backend[16],prefix[224],extra[2];OSVERSIONINFOA os;int ok=0,code=1;unsigned i;
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
 if(token(&s,exe,sizeof(exe))!=1||token(&s,backend,sizeof(backend))!=1||token(&s,prefix,sizeof(prefix))!=1||token(&s,extra,sizeof(extra))!=0||(!eq(backend,"default")&&!eq(backend,"hel")))ExitProcess(2);
 logf=fresh(prefix,".txt");if(logf==INVALID_HANDLE_VALUE)ExitProcess(2);
 text("schema","xwn-present-2");text("rung","03");text("backend",backend);text("visual","UNVERIFIED");text("scope","owned-window-gdi-readback");
 files[0]=fresh(prefix,"-source.bin");files[1]=fresh(prefix,"-before.bin");files[2]=fresh(prefix,"-after.bin");
 for(i=0;i<3;i++)if(files[i]==INVALID_HANDLE_VALUE){code=2;goto done;}
 zero(&os,sizeof(os));os.dwOSVersionInfoSize=sizeof(os);if(!GetVersionExA(&os))goto done;
 number("os.major",os.dwMajorVersion);number("os.minor",os.dwMinorVersion);number("os.build",os.dwBuildNumber);
 ok=windows();number("window.create",ok);if(!ok)goto done;
 ok=run(backend);code=ok?0:cancelled?5:1;
done:
 if(panel&&!DestroyWindow(panel))code=1;
 for(i=0;i<3;i++){if(brushes[i]&&!DeleteObject(brushes[i]))code=1;if(files[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(files[i]))io_error=1;}
 if(io_error)code=4;
 number("exit",(DWORD)code);text("result",code==0?"PRESENTATION_OK":"FAILED");text("end","complete");
 if(!CloseHandle(logf))io_error=1;
 ExitProcess(io_error?4:(UINT)code);
}
