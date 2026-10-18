/* SPDX-License-Identifier: MIT
 * Rung08b: enumerated RGB software device, owned depth buffer and order controls.
 * No primary surface, mode change, texture, stencil, or hardware claim.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define DIRECTDRAW_VERSION 0x0700
#define DIRECT3D_VERSION 0x0700
#define COBJMACROS
#include <windows.h>
#include <tlhelp32.h>
#include <ddraw.h>
#include <d3d.h>
static const GUID dd7={0x15e65ec0,0x3b9c,0x11d2,{0xb9,0x2f,0,0x60,0x97,0x97,0xea,0x5b}};
static const GUID d3d7={0xf5049e77,0x4861,0x11d2,{0xa4,7,0,0xa0,0xc9,6,0x29,0xa8}};
static const GUID rgb={0xa4665c60,0x2673,0x11cf,{0xa3,0x1a,0,0xaa,0,0xb9,0x33,0x56}};
typedef struct {float x,y,z,rhw;DWORD color;} VERTEX;
typedef char vertex_size[(sizeof(VERTEX)==20)?1:-1];
typedef char caps_size[(sizeof(D3DDEVICEDESC7)==236)?1:-1];
static VERTEX vertices[]={
 {8,8,.25f,1,0xff40c080},{56,8,.25f,1,0xff40c080},{8,56,.25f,1,0xff40c080},
 {8,8,.75f,1,0xffc04080},{56,8,.75f,1,0xffc04080},{8,56,.75f,1,0xffc04080}};
static DDPIXELFORMAT formats[64],depth_format;
static DWORD format_count,format_error,format_index=0xffffffff;
static const char *const stages[]={"clear","far_near","near_far","no_z","zero_z"};
static const char *const suffixes[]={"-clear.bin","-far-near.bin","-near-far.bin","-no-z.bin","-zero-z.bin"};
static HANDLE captures[5];
static HANDLE log_file=INVALID_HANDLE_VALUE;
static DWORD enumerated,matches,enum_error;
static D3DDEVICEDESC7 selected;
static int io_error,context;
static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static int eq(const char *a,const char *b){return lstrcmpA(a,b)==0;}
static int same(const void *a,const void *b,DWORD n){const BYTE *x=a,*y=b;while(n--)if(*x++!=*y++)return 0;return 1;}
static int put(HANDLE h,const void *p,DWORD n){DWORD w=0;if(!WriteFile(h,p,n,&w,0)||w!=n||!FlushFileBuffers(h)){io_error=1;return 0;}return 1;}
static void text(const char *key,const char *v){char b[1100];if(lstrlenA(key)+lstrlenA(v)+4>=(int)sizeof(b)){io_error=1;return;}wsprintfA(b,"%s=%s\r\n",key,v);put(log_file,b,lstrlenA(b));}
static void number(const char *key,DWORD v){char b[32];wsprintfA(b,"%lu",v);text(key,b);}
static void hex(const char *key,const BYTE *p,DWORD n){static const char d[]="0123456789abcdef";char b[1041];DWORD i;if(n>520){io_error=1;return;}for(i=0;i<n;i++){b[2*i]=d[p[i]>>4];b[2*i+1]=d[p[i]&15];}b[n*2]=0;text(key,b);}
static int token(const char **cursor,char *out,unsigned cap){const char *p=*cursor;unsigned n=0;int q=0;while(*p==' '||*p=='\t')p++;if(!*p){*cursor=p;return 0;}if(*p=='"'){q=1;p++;}while(*p&&(q?*p!='"':(*p!=' '&&*p!='\t'))){if(*p=='"'||n+1>=cap)return -1;out[n++]=*p++;}if(q){if(*p!='"')return -1;p++;if(*p&&*p!=' '&&*p!='\t')return -1;}out[n]=0;*cursor=p;return n?1:-1;}
static HANDLE fresh(const char *prefix,const char *suffix){char b[256];if(lstrlenA(prefix)+lstrlenA(suffix)>=256)return INVALID_HANDLE_VALUE;lstrcpyA(b,prefix);lstrcatA(b,suffix);return CreateFileA(b,GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);}
static HRESULT CALLBACK enumerate(char *description,char *name,D3DDEVICEDESC7 *caps,void *ctx){(void)description;(void)name;if(ctx!=&context||!caps||++enumerated>16){enum_error=1;return D3DENUMRET_CANCEL;}if(same(&caps->deviceGUID,&rgb,16)){selected=*caps;matches++;}return D3DENUMRET_OK;}
static int acceptable(const DDPIXELFORMAT *p){return p->dwSize==sizeof(*p)&&p->dwFlags==DDPF_ZBUFFER&&p->dwFourCC==0&&(p->dwZBufferBitDepth==16||p->dwZBufferBitDepth==24||p->dwZBufferBitDepth==32)&&p->dwStencilBitDepth==0&&p->dwStencilBitMask==0;}
static HRESULT CALLBACK depth_enum(DDPIXELFORMAT *p,void *ctx){if(ctx!=&context||!p||p->dwSize!=sizeof(*p)||format_count>=64){format_error=1;return D3DENUMRET_CANCEL;}formats[format_count]=*p;if(format_index==0xffffffff&&acceptable(p)){format_index=format_count;depth_format=*p;}format_count++;return D3DENUMRET_OK;}
static int modules(void){HANDLE h;MODULEENTRY32 m;DWORD n=0,error;char key[64];BOOL more;h=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,GetCurrentProcessId());if(h==INVALID_HANDLE_VALUE)return 0;zero(&m,sizeof(m));m.dwSize=sizeof(m);more=Module32First(h,&m);while(more){if(n>=64||!m.szExePath[0]||lstrlenA(m.szExePath)>=MAX_PATH){CloseHandle(h);return 0;}wsprintfA(key,"module%lu.path",n);hex(key,(BYTE*)m.szExePath,lstrlenA(m.szExePath));wsprintfA(key,"module%lu.bytes",n);number(key,m.modBaseSize);n++;more=Module32Next(h,&m);}error=GetLastError();CloseHandle(h);number("modules",n);number("modules.end_error",error);return n>0&&error==ERROR_NO_MORE_FILES&&!io_error;}
static int format(const DDSURFACEDESC2 *s){return s->dwWidth==64&&s->dwHeight==64&&s->ddpfPixelFormat.dwFlags==DDPF_RGB&&s->ddpfPixelFormat.dwRGBBitCount==32&&s->ddpfPixelFormat.dwRBitMask==0xff0000&&s->ddpfPixelFormat.dwGBitMask==0xff00&&s->ddpfPixelFormat.dwBBitMask==0xff&&s->ddpfPixelFormat.dwRGBAlphaBitMask==0&&(s->ddsCaps.dwCaps&(DDSCAPS_SYSTEMMEMORY|DDSCAPS_3DDEVICE|DDSCAPS_OFFSCREENPLAIN))==(DDSCAPS_SYSTEMMEMORY|DDSCAPS_3DDEVICE|DDSCAPS_OFFSCREENPLAIN)&&!(s->ddsCaps.dwCaps&(DDSCAPS_PRIMARYSURFACE|DDSCAPS_VIDEOMEMORY));}
static int snapshot(IDirectDrawSurface7 *surface,HANDLE file,const char *stem){DDSURFACEDESC2 s;HRESULT hr;DWORD y;int good=0;char key[80];zero(&s,sizeof(s));s.dwSize=sizeof(s);hr=IDirectDrawSurface7_Lock(surface,0,&s,DDLOCK_WAIT|DDLOCK_READONLY,0);wsprintfA(key,"%s.lock",stem);number(key,(DWORD)hr);if(hr!=DD_OK)return 0;
 wsprintfA(key,"%s.pitch",stem);number(key,(DWORD)s.lPitch);wsprintfA(key,"%s.caps",stem);number(key,s.ddsCaps.dwCaps);
 if(format(&s)&&s.lpSurface&&s.lPitch>=256&&s.lPitch<=4096){good=1;for(y=0;y<64;y++)if(!put(file,(BYTE*)s.lpSurface+y*s.lPitch,256)){good=0;break;}}
 hr=IDirectDrawSurface7_Unlock(surface,0);wsprintfA(key,"%s.unlock",stem);number(key,(DWORD)hr);wsprintfA(key,"%s.valid",stem);number(key,good);return good&&hr==DD_OK;
}
#define HR(key,expr) do{hr=(expr);number(key,(DWORD)hr);if(hr!=DD_OK)goto done;}while(0)
#define RS(key,state,value) HR(key,IDirect3DDevice7_SetRenderState(dev,state,value))
static int run(HWND w,const char *backend){typedef HRESULT(WINAPI *CREATE)(GUID*,void**,REFIID,IUnknown*);union{FARPROC raw;CREATE create;}fn;HMODULE m=0;IDirectDraw7 *dd=0;IDirect3D7 *d3d=0;IDirectDrawSurface7 *target=0,*depth=0,*attached_check=0;IDirect3DDevice7 *dev=0;HRESULT hr;DDSURFACEDESC2 s;D3DVIEWPORT7 vp={0,0,64,64,0,1};int ok=0,scene=0,clean=1,attached=0;ULONG refs;DWORD i,j;char key[80];DDSCAPS2 caps;
 m=LoadLibraryA("ddraw.dll");number("ddraw.load",m!=0);if(!m)goto done;fn.raw=GetProcAddress(m,"DirectDrawCreateEx");number("ddraw.entry",fn.raw!=0);if(!fn.raw)goto done;
 HR("ddraw.create",fn.create(eq(backend,"hel")?(GUID*)DDCREATE_EMULATIONONLY:0,(void**)&dd,&dd7,0));
 HR("ddraw.cooperative",IDirectDraw7_SetCooperativeLevel(dd,w,DDSCL_NORMAL));
 HR("d3d.query",IDirectDraw7_QueryInterface(dd,&d3d7,(void**)&d3d));
 HR("enum.hr",IDirect3D7_EnumDevices(d3d,enumerate,&context));number("enum.count",enumerated);number("enum.matches",matches);number("enum.error",enum_error);
 if(enum_error||matches!=1||(selected.dwDevCaps&(D3DDEVCAPS_HWRASTERIZATION|D3DDEVCAPS_HWTRANSFORMANDLIGHT))||!(selected.dwDeviceRenderBitDepth&DDBD_32))goto done;
 hex("device.caps",(BYTE*)&selected,sizeof(selected));hex("vertices",(BYTE*)vertices,sizeof(vertices));number("vertex.stride",sizeof(VERTEX));number("vertex.fvf",D3DFVF_XYZRHW|D3DFVF_DIFFUSE);
 zero(&s,sizeof(s));s.dwSize=sizeof(s);s.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT|DDSD_PIXELFORMAT;s.dwWidth=s.dwHeight=64;s.ddsCaps.dwCaps=DDSCAPS_SYSTEMMEMORY|DDSCAPS_OFFSCREENPLAIN|DDSCAPS_3DDEVICE;s.ddpfPixelFormat.dwSize=sizeof(DDPIXELFORMAT);s.ddpfPixelFormat.dwFlags=DDPF_RGB;s.ddpfPixelFormat.dwRGBBitCount=32;s.ddpfPixelFormat.dwRBitMask=0xff0000;s.ddpfPixelFormat.dwGBitMask=0xff00;s.ddpfPixelFormat.dwBBitMask=0xff;
 HR("target.create",IDirectDraw7_CreateSurface(dd,&s,&target,0));
 HR("formats.hr",IDirect3D7_EnumZBufferFormats(d3d,&selected.deviceGUID,depth_enum,&context));number("formats.count",format_count);number("formats.error",format_error);number("formats.selected",format_index);
 for(i=0;i<format_count;i++){wsprintfA(key,"format%lu",i);hex(key,(BYTE*)&formats[i],sizeof(formats[i]));}
 if(format_error||format_index==0xffffffff)goto done;
 zero(&s,sizeof(s));s.dwSize=sizeof(s);s.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT|DDSD_PIXELFORMAT;s.dwWidth=s.dwHeight=64;s.ddsCaps.dwCaps=DDSCAPS_SYSTEMMEMORY|DDSCAPS_ZBUFFER;s.ddpfPixelFormat=depth_format;
 HR("depth.create",IDirectDraw7_CreateSurface(dd,&s,&depth,0));
 zero(&s,sizeof(s));s.dwSize=sizeof(s);HR("depth.desc",IDirectDrawSurface7_GetSurfaceDesc(depth,&s));
 number("depth.width",s.dwWidth);number("depth.height",s.dwHeight);number("depth.caps",s.ddsCaps.dwCaps);hex("depth.format",(BYTE*)&s.ddpfPixelFormat,sizeof(s.ddpfPixelFormat));
 if(s.dwWidth!=64||s.dwHeight!=64||!same(&s.ddpfPixelFormat,&depth_format,sizeof(depth_format))||(s.ddsCaps.dwCaps&(DDSCAPS_SYSTEMMEMORY|DDSCAPS_ZBUFFER))!=(DDSCAPS_SYSTEMMEMORY|DDSCAPS_ZBUFFER)||(s.ddsCaps.dwCaps&(DDSCAPS_PRIMARYSURFACE|DDSCAPS_VIDEOMEMORY)))goto done;
 HR("depth.attach",IDirectDrawSurface7_AddAttachedSurface(target,depth));attached=1;
 zero(&caps,sizeof(caps));caps.dwCaps=DDSCAPS_ZBUFFER;
 HR("depth.get_attached",IDirectDrawSurface7_GetAttachedSurface(target,&caps,&attached_check));number("depth.identity",attached_check==depth);
 if(attached_check!=depth)goto done;
 number("depth.release_query",IDirectDrawSurface7_Release(attached_check));attached_check=0;
 HR("device.create",IDirect3D7_CreateDevice(d3d,&selected.deviceGUID,target,&dev));
 HR("viewport",IDirect3DDevice7_SetViewport(dev,&vp));
 RS("state.z",D3DRENDERSTATE_ZENABLE,D3DZB_TRUE);RS("state.zwrite",D3DRENDERSTATE_ZWRITEENABLE,TRUE);RS("state.zfunc",D3DRENDERSTATE_ZFUNC,D3DCMP_LESS);RS("state.lighting",D3DRENDERSTATE_LIGHTING,FALSE);RS("state.cull",D3DRENDERSTATE_CULLMODE,D3DCULL_NONE);RS("state.fill",D3DRENDERSTATE_FILLMODE,D3DFILL_SOLID);RS("state.shade",D3DRENDERSTATE_SHADEMODE,D3DSHADE_FLAT);RS("state.fog",D3DRENDERSTATE_FOGENABLE,FALSE);RS("state.alpha",D3DRENDERSTATE_ALPHABLENDENABLE,FALSE);RS("state.alphatest",D3DRENDERSTATE_ALPHATESTENABLE,FALSE);RS("state.dither",D3DRENDERSTATE_DITHERENABLE,FALSE);RS("state.specular",D3DRENDERSTATE_SPECULARENABLE,FALSE);RS("state.antialias",D3DRENDERSTATE_ANTIALIAS,D3DANTIALIAS_NONE);
 HR("texture0",IDirect3DDevice7_SetTexture(dev,0,0));HR("stage0.op",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_COLOROP,D3DTOP_SELECTARG1));HR("stage0.arg",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_COLORARG1,D3DTA_DIFFUSE));HR("stage0.alpha",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_ALPHAOP,D3DTOP_DISABLE));HR("stage1.op",IDirect3DDevice7_SetTextureStageState(dev,1,D3DTSS_COLOROP,D3DTOP_DISABLE));
 for(i=0;i<5;i++){
  DWORD enabled=i==3?D3DZB_FALSE:D3DZB_TRUE;D3DVALUE z=i==4?0.0f:1.0f;
  wsprintfA(key,"%s.z_enabled",stages[i]);number(key,enabled);wsprintfA(key,"%s.clear_z",stages[i]);number(key,i==4?0:1);
  wsprintfA(key,"%s.state_z",stages[i]);RS(key,D3DRENDERSTATE_ZENABLE,enabled);
  wsprintfA(key,"%s.clear_hr",stages[i]);HR(key,IDirect3DDevice7_Clear(dev,0,0,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0x00102030,z,0));
  if(i){
   wsprintfA(key,"%s.begin",stages[i]);HR(key,IDirect3DDevice7_BeginScene(dev));scene=1;
   for(j=0;j<2;j++){
    DWORD index=i==1?(1-j):j;wsprintfA(key,"%s.draw%lu.index",stages[i],j);number(key,index);
    wsprintfA(key,"%s.draw%lu.hr",stages[i],j);HR(key,IDirect3DDevice7_DrawPrimitive(dev,D3DPT_TRIANGLELIST,D3DFVF_XYZRHW|D3DFVF_DIFFUSE,vertices+3*index,3,0));
   }
   hr=IDirect3DDevice7_EndScene(dev);scene=0;wsprintfA(key,"%s.end",stages[i]);number(key,(DWORD)hr);if(hr!=DD_OK)goto done;
  }
  if(!snapshot(target,captures[i],stages[i]))goto done;
 }
 ok=modules();number("modules.ok",ok);ok=ok&&!io_error;
done:
 if(scene){number("cleanup.end_scene",(DWORD)IDirect3DDevice7_EndScene(dev));clean=0;}
 if(dev){refs=IDirect3DDevice7_Release(dev);number("release.device",refs);clean&=refs==0;}
 if(attached_check)IDirectDrawSurface7_Release(attached_check);
 if(attached){hr=IDirectDrawSurface7_DeleteAttachedSurface(target,0,depth);number("depth.detach",(DWORD)hr);clean&=hr==DD_OK;}
 if(depth){refs=IDirectDrawSurface7_Release(depth);number("release.depth",refs);clean&=refs==0;}
 if(target){refs=IDirectDrawSurface7_Release(target);number("release.target",refs);clean&=refs==0;}
 if(d3d)number("release.d3d",IDirect3D7_Release(d3d));
 if(dd){refs=IDirectDraw7_Release(dd);number("release.ddraw",refs);clean&=refs==0;}
 if(m){int unloaded=FreeLibrary(m)!=0;number("ddraw.unload",unloaded);clean&=unloaded;}
 return ok&&clean;
}
void WINAPI mainCRTStartup(void){const char *s=GetCommandLineA();char exe[512],backend[16],prefix[224],extra[2];WNDCLASSA cls;HWND w=0;OSVERSIONINFOA os;int code=1;DWORD i;
 for(i=0;i<5;i++)captures[i]=INVALID_HANDLE_VALUE;
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
 if(token(&s,exe,sizeof(exe))!=1||token(&s,backend,sizeof(backend))!=1||token(&s,prefix,sizeof(prefix))!=1||token(&s,extra,sizeof(extra))!=0||(!eq(backend,"default")&&!eq(backend,"hel")))ExitProcess(2);
 log_file=fresh(prefix,".txt");if(log_file==INVALID_HANDLE_VALUE)ExitProcess(2);for(i=0;i<5;i++){captures[i]=fresh(prefix,suffixes[i]);if(captures[i]==INVALID_HANDLE_VALUE)goto done;}
 text("schema","xwn-d3d-depth-1");text("backend",backend);text("scope","offscreen-rgb-software");number("width",64);number("height",64);
 zero(&os,sizeof(os));os.dwOSVersionInfoSize=sizeof(os);if(!GetVersionExA(&os))goto done;number("os.major",os.dwMajorVersion);number("os.minor",os.dwMinorVersion);number("os.build",os.dwBuildNumber);
 zero(&cls,sizeof(cls));cls.lpfnWndProc=DefWindowProcA;cls.hInstance=GetModuleHandleA(0);cls.lpszClassName="XWND3DDepth08b";if(!RegisterClassA(&cls))goto done;
 w=CreateWindowA(cls.lpszClassName,"XWN D3D depth",WS_OVERLAPPEDWINDOW,0,0,128,128,0,0,cls.hInstance,0);number("window.created",w!=0);if(w&&run(w,backend))code=0;
done:
 if(w&&!DestroyWindow(w))code=1;
 for(i=0;i<5;i++)if(captures[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(captures[i]))io_error=1;
 if(io_error)code=4;
 number("exit",code);text("result",code==0?"CAPTURED":"FAILED");text("end","complete");if(!CloseHandle(log_file))io_error=1;ExitProcess(io_error?4:(UINT)code);
}
