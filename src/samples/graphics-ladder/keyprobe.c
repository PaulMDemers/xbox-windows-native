/* SPDX-License-Identifier: MIT
 * RGB32 color-key diagnostic: 3 keys x plain/keyed x unclipped/clipped.
 * Owned system-memory surfaces only. No primary surface or display-mode change.
 * A pixel mismatch is retained and later independent cases continue; API/layout
 * failures stop. This diagnostic does not turn unexpected pixels into a pass.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define DIRECTDRAW_VERSION 0x0700
#define COBJMACROS
#include <windows.h>
#include <ddraw.h>
#define SW 16
#define SH 12
#define DW 32
#define DH 24
static const GUID iid7={0x15e65ec0,0x3b9c,0x11d2,{0xb9,0x2f,0,0x60,0x97,0x97,0xea,0x5b}};
static const DWORD colors[16]={0,0xff0000,0x010000,1,0x00ff00,0x123456,0xab3456,0x123457,0x120000,0xffffff,0x00ffff,0xff00ff,0x654321,0x124321,0x0000ff,0x010001};
static const DWORD keys[3]={0,0xff0000,0x123456};
static HANDLE logf=INVALID_HANDLE_VALUE,sourcef=INVALID_HANDLE_VALUE,destf=INVALID_HANDLE_VALUE;
static DWORD source[SW*SH],expected[DW*DH],pixels[DW*DH];
static unsigned stage,completed;
static DWORD allbad;
static int io_error;
static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static int put(HANDLE h,const void *p,DWORD n){DWORD w=0;if(!WriteFile(h,p,n,&w,0)||w!=n||!FlushFileBuffers(h)){io_error=1;return 0;}return 1;}
static void text(const char *k,const char *v){char b[256];wsprintfA(b,"%s=%s\r\n",k,v);put(logf,b,lstrlenA(b));}
static void number(const char *k,DWORD v){char b[32];wsprintfA(b,"%lu",v);text(k,b);}
static int call(const char *k,HRESULT h){char b[16];wsprintfA(b,"%08lX",(DWORD)h);text(k,b);return h==DD_OK;}
static void snum(const char *k,DWORD v){char b[96];wsprintfA(b,"s%u.%s",stage,k);number(b,v);}
static int scall(const char *k,HRESULT h){char b[96];wsprintfA(b,"s%u.%s",stage,k);return call(b,h);}
static int token(const char **cursor,char *out,unsigned cap){const char *p=*cursor;unsigned n=0;int q=0;
 while(*p==' '||*p=='\t')p++;
 if(!*p){*cursor=p;return 0;}if(*p=='"'){q=1;p++;}
 while(*p&&(q?*p!='"':(*p!=' '&&*p!='\t'))){if(*p=='"'||n+1>=cap)return -1;out[n++]=*p++;}
 if(q){if(*p!='"')return -1;p++;if(*p&&*p!=' '&&*p!='\t')return -1;}
 out[n]=0;*cursor=p;return n?1:-1;
}
static HANDLE fresh(const char *prefix,const char *suffix){char b[256];if(lstrlenA(prefix)+lstrlenA(suffix)>=256)return INVALID_HANDLE_VALUE;lstrcpyA(b,prefix);lstrcatA(b,suffix);return CreateFileA(b,GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);}
static int modes(void){DEVMODEA d;unsigned i;char key[64];
 zero(&d,sizeof(d));d.dmSize=sizeof(d);if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&d))return 0;
 number("desktop.width",d.dmPelsWidth);number("desktop.height",d.dmPelsHeight);number("desktop.bpp",d.dmBitsPerPel);
 for(i=0;i<4096;i++){
  zero(&d,sizeof(d));d.dmSize=sizeof(d);
  if(!EnumDisplaySettingsA(0,i,&d)){number("modes.count",i);number("modes.complete",1);return i!=0;}
  wsprintfA(key,"m%u.width",i);number(key,d.dmPelsWidth);wsprintfA(key,"m%u.height",i);number(key,d.dmPelsHeight);
  wsprintfA(key,"m%u.bpp",i);number(key,d.dmBitsPerPel);wsprintfA(key,"m%u.hz",i);number(key,d.dmDisplayFrequency);wsprintfA(key,"m%u.flags",i);number(key,d.dmDisplayFlags);
 }
 number("modes.complete",0);return 0;
}
static int create_surface(IDirectDraw7 *dd,unsigned w,unsigned h,IDirectDrawSurface7 **s,const char *label){DDSURFACEDESC2 d;zero(&d,sizeof(d));d.dwSize=sizeof(d);d.dwFlags=DDSD_WIDTH|DDSD_HEIGHT|DDSD_CAPS|DDSD_PIXELFORMAT;d.dwWidth=w;d.dwHeight=h;d.ddsCaps.dwCaps=DDSCAPS_OFFSCREENPLAIN|DDSCAPS_SYSTEMMEMORY;
 d.ddpfPixelFormat.dwSize=sizeof(DDPIXELFORMAT);d.ddpfPixelFormat.dwFlags=DDPF_RGB;d.ddpfPixelFormat.dwRGBBitCount=32;d.ddpfPixelFormat.dwRBitMask=0xff0000;d.ddpfPixelFormat.dwGBitMask=0xff00;d.ddpfPixelFormat.dwBBitMask=255;
 return call(label,IDirectDraw7_CreateSurface(dd,&d,s,0));
}
static int access_pixels(IDirectDrawSurface7 *s,unsigned w,unsigned h,DWORD *want,int write,HANDLE f,const char *label){DDSURFACEDESC2 d;unsigned x,y;int valid,unlocked;DWORD bad=0;char key[64];zero(&d,sizeof(d));d.dwSize=sizeof(d);
 wsprintfA(key,"%s.lock",label);if(!scall(key,IDirectDrawSurface7_Lock(s,0,&d,DDLOCK_DONOTWAIT|(write?DDLOCK_WRITEONLY:DDLOCK_READONLY),0)))return 0;
 valid=d.lpSurface&&d.dwWidth==w&&d.dwHeight==h&&d.lPitch>0&&(DWORD)d.lPitch>=w*4&&d.lPitch<=65536&&d.lPitch%4==0&&d.ddpfPixelFormat.dwFlags==DDPF_RGB&&d.ddpfPixelFormat.dwRGBBitCount==32&&d.ddpfPixelFormat.dwRBitMask==0xff0000&&d.ddpfPixelFormat.dwGBitMask==0xff00&&d.ddpfPixelFormat.dwBBitMask==255&&(d.ddsCaps.dwCaps&DDSCAPS_SYSTEMMEMORY)&&!(d.ddsCaps.dwCaps&DDSCAPS_VIDEOMEMORY);
 wsprintfA(key,"%s.layout",label);snum(key,valid);wsprintfA(key,"%s.pitch",label);snum(key,(DWORD)d.lPitch);
 if(valid)for(y=0;y<h;y++)for(x=0;x<w;x++){DWORD *p=(DWORD*)((BYTE*)d.lpSurface+y*d.lPitch+x*4);if(write)*p=want[y*w+x];else{pixels[y*w+x]=*p;if(*p!=want[y*w+x])bad++;}}
 wsprintfA(key,"%s.unlock",label);unlocked=scall(key,IDirectDrawSurface7_Unlock(s,0));
 if(!write){wsprintfA(key,"%s.mismatches",label);snum(key,bad);allbad+=bad;if(valid&&!put(f,pixels,w*h*4))valid=0;}
 return valid&&unlocked;
}
static int run(HWND window,const char *backend){typedef HRESULT(WINAPI *CREATE)(GUID*,void**,REFIID,IUnknown*);union{FARPROC raw;CREATE create;}fn;HMODULE module=0;IDirectDraw7 *dd=0;IDirectDrawSurface7 *src=0,*dst=0;IDirectDrawClipper *clipper=0;DDSURFACEDESC2 mode;DDCOLORKEY key,got;struct{RGNDATAHEADER h;RECT r[2];}region,observed;DWORD size;RECT from={0,0,16,12},to={4,4,20,16};int ok=0,clean=1,attached=0;unsigned i,x,y;DWORD refs;
 module=LoadLibraryA("ddraw.dll");number("ddraw.load",module!=0);if(!module)goto done;fn.raw=GetProcAddress(module,"DirectDrawCreateEx");number("ddraw.entry",fn.raw!=0);if(!fn.raw)goto done;
 if(!call("ddraw.create",fn.create(lstrcmpA(backend,"hel")==0?(GUID*)DDCREATE_EMULATIONONLY:0,(void**)&dd,&iid7,0)))goto done;
 if(!call("ddraw.cooperative",IDirectDraw7_SetCooperativeLevel(dd,window,DDSCL_NORMAL)))goto done;
 zero(&mode,sizeof(mode));mode.dwSize=sizeof(mode);if(!call("ddraw.mode",IDirectDraw7_GetDisplayMode(dd,&mode)))goto done;number("mode.width",mode.dwWidth);number("mode.height",mode.dwHeight);number("mode.bpp",mode.ddpfPixelFormat.dwRGBBitCount);
 if(!create_surface(dd,SW,SH,&src,"source.create")||!create_surface(dd,DW,DH,&dst,"dest.create"))goto done;
 if(!call("clipper.create",IDirectDraw7_CreateClipper(dd,0,&clipper,0)))goto done;
 zero(&region,sizeof(region));region.h.dwSize=sizeof(RGNDATAHEADER);region.h.iType=RDH_RECTANGLES;region.h.nCount=2;region.h.nRgnSize=sizeof(region.r);SetRect(&region.h.rcBound,6,5,19,15);SetRect(&region.r[0],6,5,12,15);SetRect(&region.r[1],14,5,19,15);
 if(!call("clipper.set",IDirectDrawClipper_SetClipList(clipper,(RGNDATA*)&region,0)))goto done;
 zero(&observed,sizeof(observed));size=sizeof(observed);if(!call("clipper.get",IDirectDrawClipper_GetClipList(clipper,0,(RGNDATA*)&observed,&size)))goto done;
 {int exact=size==sizeof(region);for(i=0;i<sizeof(region);i++)if(((BYTE*)&observed)[i]!=((BYTE*)&region)[i])exact=0;number("clipper.exact",exact);if(!exact)goto done;}
 for(y=0;y<SH;y++)for(x=0;x<SW;x++)source[y*SW+x]=colors[(x+3*y)%16];
 stage=0;if(!access_pixels(src,SW,SH,source,1,sourcef,"source.write"))goto done;
 for(stage=0;stage<12;stage++){
  int clipped=(stage/2)%2,keyed=stage%2;
  snum("key.requested",keys[stage/4]);snum("keyed",keyed);snum("clipped",clipped);
  key.dwColorSpaceLowValue=key.dwColorSpaceHighValue=keys[stage/4];
  if(!scall("key.set",IDirectDrawSurface7_SetColorKey(src,DDCKEY_SRCBLT,&key)))goto done;
  zero(&got,sizeof(got));if(!scall("key.get",IDirectDrawSurface7_GetColorKey(src,DDCKEY_SRCBLT,&got)))goto done;
  snum("key.low",got.dwColorSpaceLowValue);snum("key.high",got.dwColorSpaceHighValue);
  if(got.dwColorSpaceLowValue!=keys[stage/4]||got.dwColorSpaceHighValue!=keys[stage/4])goto done;
  if(attached!=clipped){if(!scall("clipper.change",IDirectDrawSurface7_SetClipper(dst,clipped?clipper:0)))goto done;attached=clipped;}
  for(i=0;i<DW*DH;i++)expected[i]=0x335577;
  if(!access_pixels(dst,DW,DH,expected,1,destf,"dest.write"))goto done;
  if(!scall("blit",IDirectDrawSurface7_Blt(dst,&to,src,&from,DDBLT_DONOTWAIT|(keyed?DDBLT_KEYSRC:0),0)))goto done;
  for(y=4;y<16;y++)for(x=4;x<20;x++)if(!clipped||(y>=5&&y<15&&((x>=6&&x<12)||(x>=14&&x<19)))){DWORD v=source[(y-4)*SW+x-4];if(!keyed||v!=keys[stage/4])expected[y*DW+x]=v;}
  if(!access_pixels(src,SW,SH,source,0,sourcef,"source.read")||!access_pixels(dst,DW,DH,expected,0,destf,"dest.read"))goto done;
  snum("complete",1);completed++;
 }
 ok=1;
done:
 number("cleanup.clipper.attached",attached);
 if(dst&&attached)clean&=call("cleanup.clipper",IDirectDrawSurface7_SetClipper(dst,0));
 if(dst){refs=IDirectDrawSurface7_Release(dst);number("release.dest",refs);clean&=refs==0;}
 if(src){refs=IDirectDrawSurface7_Release(src);number("release.source",refs);clean&=refs==0;}
 if(clipper){refs=IDirectDrawClipper_Release(clipper);number("release.clipper",refs);clean&=refs==0;}
 if(dd){refs=IDirectDraw7_Release(dd);number("release.ddraw",refs);clean&=refs==0;}
 if(module){int unloaded=FreeLibrary(module)!=0;number("ddraw.unload",unloaded);clean&=unloaded;}
 return ok&&clean;
}
void WINAPI mainCRTStartup(void){const char *s=GetCommandLineA();char exe[512],backend[16],prefix[224],extra[2];WNDCLASSA cls;HWND window=0;OSVERSIONINFOA os;int code=2;
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
 if(token(&s,exe,sizeof(exe))!=1||token(&s,backend,sizeof(backend))!=1||token(&s,prefix,sizeof(prefix))!=1||token(&s,extra,sizeof(extra))!=0||(lstrcmpA(backend,"default")&&lstrcmpA(backend,"hel")))ExitProcess(2);
 logf=fresh(prefix,".txt");if(logf==INVALID_HANDLE_VALUE)ExitProcess(2);
 text("schema","xwn-keyprobe-1");text("backend",backend);text("scope","owned-rgb32-system-memory");
 sourcef=fresh(prefix,"-source.bin");destf=fresh(prefix,"-dest.bin");if(sourcef==INVALID_HANDLE_VALUE||destf==INVALID_HANDLE_VALUE)goto done;
 zero(&os,sizeof(os));os.dwOSVersionInfoSize=sizeof(os);if(!GetVersionExA(&os))goto done;number("os.major",os.dwMajorVersion);number("os.minor",os.dwMinorVersion);number("os.build",os.dwBuildNumber);
 if(!modes())goto done;
 zero(&cls,sizeof(cls));cls.lpfnWndProc=DefWindowProcA;cls.hInstance=GetModuleHandleA(0);cls.lpszClassName="XWNKeyProbe";if(!RegisterClassA(&cls))goto done;window=CreateWindowA(cls.lpszClassName,"XWN key probe",WS_OVERLAPPEDWINDOW,0,0,128,128,0,0,cls.hInstance,0);number("window.create",window!=0);if(!window)goto done;
 if(run(window,backend))code=allbad?1:0;
done:
 if(window&&!DestroyWindow(window))code=2;
 if(sourcef!=INVALID_HANDLE_VALUE&&!CloseHandle(sourcef))io_error=1;
 if(destf!=INVALID_HANDLE_VALUE&&!CloseHandle(destf))io_error=1;
 if(io_error)code=4;
 number("completed",completed);number("mismatches",allbad);number("exit",code);text("result",code==0?"KEYPROBE_OK":"FAILED");text("end","complete");
 if(!CloseHandle(logf))io_error=1;
 ExitProcess(io_error?4:(UINT)code);
}
