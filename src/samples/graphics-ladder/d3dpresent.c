/* SPDX-License-Identifier: MIT
 * D3D7 software rendering to an owned window/clipper/primary. No mode switch.
 * Paint handlers never draw the DirectDraw pattern: GDI supplies only guards.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define DIRECTDRAW_VERSION 0x0700
#define DIRECT3D_VERSION 0x0700
#define COBJMACROS
#include <windows.h>
#include <ddraw.h>
#include <d3d.h>
#include <tlhelp32.h>
#define CW 256
#define CH 192
#define TW 128
#define TH 112
static const GUID iid7={0x15e65ec0,0x3b9c,0x11d2,{0xb9,0x2f,0,0x60,0x97,0x97,0xea,0x5b}};
static const GUID d3d7={0xf5049e77,0x4861,0x11d2,{0xa4,7,0,0xa0,0xc9,6,0x29,0xa8}};
static const GUID rgb={0xa4665c60,0x2673,0x11cf,{0xa3,0x1a,0,0xaa,0,0xb9,0x33,0x56}};
typedef struct {float x,y,z,rhw;DWORD color;} VERTEX;
typedef char vertex_size[(sizeof(VERTEX)==20)?1:-1];
typedef char caps_size[(sizeof(D3DDEVICEDESC7)==236)?1:-1];
static DWORD enumerated,matches,enum_error;
static D3DDEVICEDESC7 selected;
static int context;
static const DWORD foreground[]={0xff0000,0x00ff00,0xffffff,0xffff00};
static const DWORD background[]={0x00ffff,0xff00ff,0x0000ff,0};
static HANDLE logf=INVALID_HANDLE_VALUE,files[4]={INVALID_HANDLE_VALUE,INVALID_HANDLE_VALUE,INVALID_HANDLE_VALUE};
static HWND panel,target,cover;
static HBRUSH brushes[3];
static DWORD screen[CW*CH],source[TW*TH],post_source[TW*TH];
static unsigned stage;
static int io_error,cancelled;
static void zero(void *v,DWORD n){BYTE *p=v;while(n--)*p++=0;}
static int eq(const char *a,const char *b){return lstrcmpA(a,b)==0;}
static int same(const void *a,const void *b,DWORD n){const BYTE *x=a,*y=b;while(n--)if(*x++!=*y++)return 0;return 1;}
static int put(HANDLE f,const void *p,DWORD n){DWORD w=0;if(!WriteFile(f,p,n,&w,0)||w!=n||!FlushFileBuffers(f)){io_error=1;return 0;}return 1;}
static void text(const char *k,const char *v){char b[1100];if(lstrlenA(k)+lstrlenA(v)+4>=(int)sizeof(b)){io_error=1;return;}wsprintfA(b,"%s=%s\r\n",k,v);put(logf,b,(DWORD)lstrlenA(b));}
static void number(const char *k,DWORD n){char b[32];wsprintfA(b,"%lu",n);text(k,b);}
static int call(const char *k,HRESULT hr){char b[16];wsprintfA(b,"%08lX",(DWORD)hr);text(k,b);return hr==DD_OK;}
static void snum(const char *k,DWORD n){char b[80];wsprintfA(b,"s%u.%s",stage,k);number(b,n);}
static int scall(const char *k,HRESULT hr){char b[80];wsprintfA(b,"s%u.%s",stage,k);return call(b,hr);}
static void hex(const char *key,const BYTE *p,DWORD n){static const char d[]="0123456789abcdef";char b[1041];DWORD i;if(n>520){io_error=1;return;}for(i=0;i<n;i++){b[2*i]=d[p[i]>>4];b[2*i+1]=d[p[i]&15];}b[n*2]=0;text(key,b);}
static int token(const char **s,char *o,unsigned cap){const char *p=*s;unsigned n=0;int q=0;
 while(*p==' '||*p=='\t')p++;
 if(!*p){*s=p;return 0;}if(*p=='"'){q=1;p++;}
 while(*p&&(q?*p!='"':(*p!=' '&&*p!='\t'))){if(*p=='"'||n+1>=cap)return -1;o[n++]=*p++;}
 if(q){if(*p!='"')return -1;p++;if(*p&&*p!=' '&&*p!='\t')return -1;}
 o[n]=0;*s=p;return n?1:-1;
}
static HANDLE fresh(const char *p,const char *s){char b[256];if(lstrlenA(p)+lstrlenA(s)>=256)return INVALID_HANDLE_VALUE;lstrcpyA(b,p);lstrcatA(b,s);return CreateFileA(b,GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);}
static int allowed(unsigned x,unsigned y,DWORD rgb){
 if(x>=12&&y>=12&&6*x+7*y<=724)return rgb==foreground[stage];
 if(x<=4||y<=4||6*x+7*y>=828)return rgb==background[stage];
 return rgb==foreground[stage]||rgb==background[stage];
}
static HRESULT CALLBACK enumerate(char *description,char *name,D3DDEVICEDESC7 *caps,void *ctx){(void)description;(void)name;if(ctx!=&context||!caps||++enumerated>16){enum_error=1;return D3DENUMRET_CANCEL;}if(same(&caps->deviceGUID,&rgb,16)){selected=*caps;matches++;}return D3DENUMRET_OK;}
static int modules(void){HANDLE h;MODULEENTRY32 m;DWORD n=0,error;char key[64];BOOL more;h=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,GetCurrentProcessId());if(h==INVALID_HANDLE_VALUE)return 0;zero(&m,sizeof(m));m.dwSize=sizeof(m);more=Module32First(h,&m);while(more){if(n>=64||!m.szExePath[0]||lstrlenA(m.szExePath)>=MAX_PATH){CloseHandle(h);return 0;}wsprintfA(key,"module%lu.path",n);hex(key,(BYTE*)m.szExePath,lstrlenA(m.szExePath));wsprintfA(key,"module%lu.bytes",n);number(key,m.modBaseSize);n++;more=Module32Next(h,&m);}error=GetLastError();CloseHandle(h);number("modules",n);number("modules.end_error",error);return n>0&&error==ERROR_NO_MORE_FILES&&!io_error;}
static int inrect(int x,int y,const RECT *r){return x>=r->left&&x<r->right&&y>=r->top&&y<r->bottom;}
static int covered(int x,int y){return (stage==1||stage==2)&&x>=48&&x<88&&y>=40&&y<72;}
static DWORD expected(unsigned x,unsigned y,int after){
 if(covered((int)x,(int)y))return 0xff00ffUL;
 if(x>=16&&x<112&&y>=16&&y<96)return after?source[y*TW+x]:0;
 return 255;
}
static LRESULT CALLBACK wnd(HWND h,UINT m,WPARAM w,LPARAM l){
 if(m==WM_CLOSE){cancelled=1;return 0;}
 if(m==WM_ERASEBKGND)return 1;
 if(m==WM_PAINT){PAINTSTRUCT ps;RECT r;HDC dc=BeginPaint(h,&ps);GetClientRect(h,&r);FillRect(dc,&r,brushes[h==target?1:h==cover?2:0]);EndPaint(h,&ps);return 0;}
 return DefWindowProcA(h,m,w,l);
}
static void pump(DWORD ms){MSG m;DWORD start=GetTickCount();do{while(PeekMessageA(&m,0,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessageA(&m);}Sleep(5);}while(!cancelled&&(DWORD)(GetTickCount()-start)<ms);}
static int windows(void){WNDCLASSA c;HINSTANCE inst=GetModuleHandleA(0);zero(&c,sizeof(c));c.lpfnWndProc=wnd;c.hInstance=inst;c.lpszClassName="XWND3DPresent08d";
 brushes[0]=CreateSolidBrush(RGB(0,0,255));brushes[1]=CreateSolidBrush(RGB(0,0,0));brushes[2]=CreateSolidBrush(RGB(255,0,255));
 if(!brushes[0]||!brushes[1]||!brushes[2]||!RegisterClassA(&c))return 0;
 panel=CreateWindowExA(WS_EX_TOPMOST|WS_EX_TOOLWINDOW,c.lpszClassName,"XWN D3D presentation",WS_POPUP|WS_CLIPCHILDREN,64,64,CW,CH,0,0,inst,0);
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
static int surface(IDirectDrawSurface7 *s,const DDPIXELFORMAT *pf,int post){
 DDSURFACEDESC2 d;DWORD x,y,bpp=pf->dwRGBBitCount/8,bad=0;int valid,ok;char label[64];
 zero(&d,sizeof(d));d.dwSize=sizeof(d);
 if(!scall(post?"post.lock":"source.lock",IDirectDrawSurface7_Lock(s,0,&d,DDLOCK_DONOTWAIT|DDLOCK_READONLY,0)))return 0;
 valid=d.lpSurface&&d.dwWidth==TW&&d.dwHeight==TH&&d.lPitch>0&&d.lPitch<=65536&&(DWORD)d.lPitch>=TW*bpp&&d.lPitch%(LONG)bpp==0&&d.ddpfPixelFormat.dwFlags==DDPF_RGB&&d.ddpfPixelFormat.dwRGBBitCount==pf->dwRGBBitCount&&d.ddpfPixelFormat.dwRBitMask==pf->dwRBitMask&&d.ddpfPixelFormat.dwGBitMask==pf->dwGBitMask&&d.ddpfPixelFormat.dwBBitMask==pf->dwBBitMask&&d.ddpfPixelFormat.dwRGBAlphaBitMask==0&&(d.ddsCaps.dwCaps&(DDSCAPS_SYSTEMMEMORY|DDSCAPS_OFFSCREENPLAIN|DDSCAPS_3DDEVICE))==(DDSCAPS_SYSTEMMEMORY|DDSCAPS_OFFSCREENPLAIN|DDSCAPS_3DDEVICE)&&!(d.ddsCaps.dwCaps&(DDSCAPS_VIDEOMEMORY|DDSCAPS_PRIMARYSURFACE));
 wsprintfA(label,"%s.layout",post?"post":"source");snum(label,valid);
 wsprintfA(label,"%s.pitch",post?"post":"source");snum(label,(DWORD)d.lPitch);
 if(valid)for(y=0;y<TH;y++)for(x=0;x<TW;x++){
  BYTE *q=(BYTE*)d.lpSurface+y*d.lPitch+x*bpp;DWORD v=bpp==2?*(WORD*)q:*(DWORD*)q;
  DWORD rgb=((v&pf->dwRBitMask)==pf->dwRBitMask?0xff0000UL:0)|((v&pf->dwGBitMask)==pf->dwGBitMask?0xff00UL:0)|((v&pf->dwBBitMask)==pf->dwBBitMask?255:0);
  DWORD native=((rgb&0xff0000)?pf->dwRBitMask:0)|((rgb&0xff00)?pf->dwGBitMask:0)|((rgb&255)?pf->dwBBitMask:0);
  if((v&(pf->dwRBitMask|pf->dwGBitMask|pf->dwBBitMask))!=native||!allowed(x,y,rgb)||(post&&source[y*TW+x]!=rgb))bad++;
  if(!post)source[y*TW+x]=rgb;else post_source[y*TW+x]=rgb;
 }
 ok=scall(post?"post.unlock":"source.unlock",IDirectDrawSurface7_Unlock(s,0));
 wsprintfA(label,"%s.mismatches",post?"post":"source");snum(label,bad);
 if(valid&&ok&&!bad&&!put(files[post?3:0],post?post_source:source,sizeof(source)))return 0;
 return valid&&ok&&!bad;
}
static int render(IDirect3DDevice7 *dev){
 VERTEX v[]={{8,8,.5f,1,0},{120,8,.5f,1,0},{8,104,.5f,1,0}};unsigned i;char label[80];HRESULT hr;
 for(i=0;i<3;i++)v[i].color=0xff000000UL|foreground[stage];
 wsprintfA(label,"s%u.vertices",stage);hex(label,(BYTE*)v,sizeof(v));
 snum("foreground",foreground[stage]);snum("background",background[stage]);
 if(!scall("clear",IDirect3DDevice7_Clear(dev,0,0,D3DCLEAR_TARGET,background[stage],1,0)))return 0;
 if(!scall("scene.begin",IDirect3DDevice7_BeginScene(dev)))return 0;
 hr=IDirect3DDevice7_DrawPrimitive(dev,D3DPT_TRIANGLELIST,D3DFVF_XYZRHW|D3DFVF_DIFFUSE,v,3,0);
 i=scall("draw",hr);return scall("scene.end",IDirect3DDevice7_EndScene(dev))&&i;
}
static int run(const char *backend){typedef HRESULT(WINAPI *CREATE)(GUID*,void**,REFIID,IUnknown*);union{FARPROC generic;CREATE create;}fn;
 HMODULE mod=0;IDirectDraw7 *dd=0;IDirect3D7 *d3d=0;IDirect3DDevice7 *dev=0;D3DVIEWPORT7 vp={0,0,TW,TH,0,1};IDirectDrawSurface7 *primary=0,*src=0;IDirectDrawClipper *cl=0;DDSURFACEDESC2 d,mode;DDPIXELFORMAT pf;HWND associated=0;int ok=0,clean=1;GUID *choice=eq(backend,"hel")?(GUID*)DDCREATE_EMULATIONONLY:0;
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
 zero(&d,sizeof(d));d.dwSize=sizeof(d);d.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT|DDSD_PIXELFORMAT;d.dwWidth=TW;d.dwHeight=TH;d.ddsCaps.dwCaps=DDSCAPS_OFFSCREENPLAIN|DDSCAPS_SYSTEMMEMORY|DDSCAPS_3DDEVICE;d.ddpfPixelFormat=pf;
 if(!call("source.create",IDirectDraw7_CreateSurface(dd,&d,&src,0)))goto done;
 if(!call("d3d.query",IDirectDraw7_QueryInterface(dd,&d3d7,(void**)&d3d)))goto done;
 if(!call("enum.hr",IDirect3D7_EnumDevices(d3d,enumerate,&context)))goto done;
 number("enum.count",enumerated);number("enum.matches",matches);number("enum.error",enum_error);hex("selected.caps",(BYTE*)&selected,sizeof(selected));
 if(enum_error||matches!=1||(selected.dwDevCaps&(D3DDEVCAPS_HWRASTERIZATION|D3DDEVCAPS_HWTRANSFORMANDLIGHT))||!(selected.dwDeviceRenderBitDepth&(pf.dwRGBBitCount==16?DDBD_16:DDBD_32)))goto done;
 if(!call("device.create",IDirect3D7_CreateDevice(d3d,&selected.deviceGUID,src,&dev)))goto done;
 if(!call("viewport",IDirect3DDevice7_SetViewport(dev,&vp)))goto done;
 if(!call("state.z",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_ZENABLE,FALSE)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.z",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_ZENABLE,&value)))goto done;number("value.z",value);if(value!=FALSE)goto done;}
 if(!call("state.zwrite",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_ZWRITEENABLE,FALSE)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.zwrite",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_ZWRITEENABLE,&value)))goto done;number("value.zwrite",value);if(value!=FALSE)goto done;}
 if(!call("state.lighting",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_LIGHTING,FALSE)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.lighting",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_LIGHTING,&value)))goto done;number("value.lighting",value);if(value!=FALSE)goto done;}
 if(!call("state.cull",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_CULLMODE,D3DCULL_NONE)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.cull",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_CULLMODE,&value)))goto done;number("value.cull",value);if(value!=D3DCULL_NONE)goto done;}
 if(!call("state.fill",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_FILLMODE,D3DFILL_SOLID)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.fill",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_FILLMODE,&value)))goto done;number("value.fill",value);if(value!=D3DFILL_SOLID)goto done;}
 if(!call("state.shade",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_SHADEMODE,D3DSHADE_FLAT)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.shade",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_SHADEMODE,&value)))goto done;number("value.shade",value);if(value!=D3DSHADE_FLAT)goto done;}
 if(!call("state.fog",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_FOGENABLE,FALSE)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.fog",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_FOGENABLE,&value)))goto done;number("value.fog",value);if(value!=FALSE)goto done;}
 if(!call("state.alpha",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_ALPHABLENDENABLE,FALSE)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.alpha",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_ALPHABLENDENABLE,&value)))goto done;number("value.alpha",value);if(value!=FALSE)goto done;}
 if(!call("state.alphatest",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_ALPHATESTENABLE,FALSE)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.alphatest",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_ALPHATESTENABLE,&value)))goto done;number("value.alphatest",value);if(value!=FALSE)goto done;}
 if(!call("state.dither",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_DITHERENABLE,FALSE)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.dither",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_DITHERENABLE,&value)))goto done;number("value.dither",value);if(value!=FALSE)goto done;}
 if(!call("state.specular",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_SPECULARENABLE,FALSE)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.specular",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_SPECULARENABLE,&value)))goto done;number("value.specular",value);if(value!=FALSE)goto done;}
 if(!call("state.antialias",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_ANTIALIAS,D3DANTIALIAS_NONE)))goto done;
 {DWORD value=0xffffffffUL;if(!call("get.antialias",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_ANTIALIAS,&value)))goto done;number("value.antialias",value);if(value!=D3DANTIALIAS_NONE)goto done;}
 if(!call("texture0",IDirect3DDevice7_SetTexture(dev,0,0)))goto done;
 if(!call("stage0.op",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_COLOROP,D3DTOP_SELECTARG1)))goto done;
 if(!call("stage0.arg",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_COLORARG1,D3DTA_DIFFUSE)))goto done;
 if(!call("stage0.alpha",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_ALPHAOP,D3DTOP_DISABLE)))goto done;
 if(!call("stage1.op",IDirect3DDevice7_SetTextureStageState(dev,1,D3DTSS_COLOROP,D3DTOP_DISABLE)))goto done;
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
  if(!capture(0,p)||!clip(cl,p)||!render(dev)||!surface(src,&pf,0))goto done;
  to.left=p.x;to.top=p.y;to.right=p.x+TW;to.bottom=p.y+TH;
  if(!scall("primary.blit",IDirectDrawSurface7_Blt(primary,&to,src,&from,DDBLT_DONOTWAIT,0)))goto done;
  if(!GdiFlush())goto done;
  Sleep(100);if(!capture(1,p)||!surface(src,&pf,1))goto done;
  snum("complete",1);pump(500);if(cancelled)goto done;
 }
 ok=modules();number("modules.ok",ok);
done:
 if(primary&&cl)clean&=call("primary.detach",IDirectDrawSurface7_SetClipper(primary,0));
 if(dev){ULONG refs=IDirect3DDevice7_Release(dev);number("release.device",refs);clean&=refs==0;}
 if(src){ULONG refs=IDirectDrawSurface7_Release(src);number("release.source",refs);clean&=refs==0;}
 if(primary){ULONG refs=IDirectDrawSurface7_Release(primary);number("release.primary",refs);clean&=refs==0;}
 if(cl){ULONG refs=IDirectDrawClipper_Release(cl);number("release.clipper",refs);clean&=refs==0;}
 if(d3d)number("release.d3d",IDirect3D7_Release(d3d));
 if(dd){ULONG refs=IDirectDraw7_Release(dd);number("release.ddraw",refs);clean&=refs==0;}
 if(mod){int unloaded=FreeLibrary(mod)!=0;number("ddraw.unload",unloaded);clean&=unloaded;}
 return ok&&clean;
}
void WINAPI mainCRTStartup(void){const char *s=GetCommandLineA();char exe[512],backend[16],prefix[224],extra[2];OSVERSIONINFOA os;int ok=0,code=1;unsigned i;
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
 if(token(&s,exe,sizeof(exe))!=1||token(&s,backend,sizeof(backend))!=1||token(&s,prefix,sizeof(prefix))!=1||token(&s,extra,sizeof(extra))!=0||(!eq(backend,"default")&&!eq(backend,"hel")))ExitProcess(2);
 logf=fresh(prefix,".txt");if(logf==INVALID_HANDLE_VALUE)ExitProcess(2);
 text("schema","xwn-d3d-present-1");text("rung","08d");text("backend",backend);text("visual","UNVERIFIED");text("scope","rgb-software-window-gdi-readback");
 files[0]=fresh(prefix,"-source.bin");files[1]=fresh(prefix,"-before.bin");files[2]=fresh(prefix,"-after.bin");files[3]=fresh(prefix,"-post.bin");
 for(i=0;i<4;i++)if(files[i]==INVALID_HANDLE_VALUE){code=2;goto done;}
 zero(&os,sizeof(os));os.dwOSVersionInfoSize=sizeof(os);if(!GetVersionExA(&os))goto done;
 number("os.major",os.dwMajorVersion);number("os.minor",os.dwMinorVersion);number("os.build",os.dwBuildNumber);
 ok=windows();number("window.create",ok);if(!ok)goto done;
 ok=run(backend);code=ok?0:cancelled?5:1;
done:
 if(panel&&!DestroyWindow(panel))code=1;
 for(i=0;i<3;i++)if(brushes[i]&&!DeleteObject(brushes[i]))code=1;
 for(i=0;i<4;i++)if(files[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(files[i]))io_error=1;
 if(io_error)code=4;
 number("exit",(DWORD)code);text("result",code==0?"PRESENTATION_OK":"FAILED");text("end","complete");
 if(!CloseHandle(logf))io_error=1;
 ExitProcess(io_error?4:(UINT)code);
}
