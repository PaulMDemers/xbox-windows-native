/* SPDX-License-Identifier: MIT
 * Rung06: bounded installed D3D7 inventory. No device creation or rendering.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define DIRECTDRAW_VERSION 0x0700
#define DIRECT3D_VERSION 0x0700
#define COBJMACROS
#include <windows.h>
#include <ddraw.h>
#include <d3d.h>
#define CAPACITY 16
typedef char caps_size_must_be_236[(sizeof(D3DDEVICEDESC7)==236)?1:-1];
static const GUID dd7={0x15e65ec0,0x3b9c,0x11d2,{0xb9,0x2f,0,0x60,0x97,0x97,0xea,0x5b}};
static const GUID d3d7={0xf5049e77,0x4861,0x11d2,{0xa4,0x07,0,0xa0,0xc9,0x06,0x29,0xa8}};
static HANDLE log_file=INVALID_HANDLE_VALUE,capture=INVALID_HANDLE_VALUE;
static D3DDEVICEDESC7 devices[CAPACITY];
static DWORD count,callback_error;
static int io_error,callback_context;
static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static int eq(const char *a,const char *b){return lstrcmpA(a,b)==0;}
static int put(HANDLE h,const void *p,DWORD n){DWORD w=0;if(!WriteFile(h,p,n,&w,0)||w!=n||!FlushFileBuffers(h)){io_error=1;return 0;}return 1;}
static void text(const char *key,const char *v){char b[1024];if((DWORD)(lstrlenA(key)+lstrlenA(v)+4)>=sizeof(b)){io_error=1;return;}wsprintfA(b,"%s=%s\r\n",key,v);put(log_file,b,lstrlenA(b));}
static void number(const char *key,DWORD v){char b[32];wsprintfA(b,"%lu",v);text(key,b);}
static void hex(const char *key,const BYTE *p,DWORD n){static const char digits[]="0123456789abcdef";char b[513];DWORD i;if(n>256){io_error=1;return;}for(i=0;i<n;i++){b[2*i]=digits[p[i]>>4];b[2*i+1]=digits[p[i]&15];}b[n*2]=0;text(key,b);}
static int string(const char *key,const char *p){DWORD n;if(!p)return 0;for(n=0;n<256;n++)if(!p[n]){if(!n)return 0;hex(key,(const BYTE*)p,n);return !io_error;}return 0;}
static void item(const char *key,DWORD v){char b[96];wsprintfA(b,"d%lu.%s",count,key);number(b,v);}
static HRESULT CALLBACK device(char *description,char *name,D3DDEVICEDESC7 *caps,void *ctx){DWORD i,j;char key[64];
 if(ctx!=&callback_context||!caps){callback_error=1;return D3DENUMRET_CANCEL;}
 if(count>=CAPACITY){callback_error=2;return D3DENUMRET_CANCEL;}
 for(i=0;i<count;i++){int same=1;for(j=0;j<16;j++)if(((BYTE*)&devices[i].deviceGUID)[j]!=((BYTE*)&caps->deviceGUID)[j])same=0;if(same){callback_error=3;return D3DENUMRET_CANCEL;}}
 devices[count]=*caps;
 wsprintfA(key,"d%lu.raw",count);hex(key,(const BYTE*)caps,sizeof(*caps));
 wsprintfA(key,"d%lu.description",count);if(!string(key,description)){callback_error=4;return D3DENUMRET_CANCEL;}
 wsprintfA(key,"d%lu.name",count);if(!string(key,name)){callback_error=5;return D3DENUMRET_CANCEL;}
 wsprintfA(key,"d%lu.guid",count);hex(key,(const BYTE*)&caps->deviceGUID,16);
 item("caps",caps->dwDevCaps);item("render_depths",caps->dwDeviceRenderBitDepth);item("z_depths",caps->dwDeviceZBufferBitDepth);
 item("max_texture_width",caps->dwMaxTextureWidth);item("max_texture_height",caps->dwMaxTextureHeight);
 item("texture_ops",caps->dwTextureOpCaps);item("blend_stages",caps->wMaxTextureBlendStages);item("textures",caps->wMaxSimultaneousTextures);
 item("hardware_rasterization_reported",(caps->dwDevCaps&D3DDEVCAPS_HWRASTERIZATION)!=0);
 item("hardware_tnl_reported",(caps->dwDevCaps&D3DDEVCAPS_HWTRANSFORMANDLIGHT)!=0);
 if(io_error||!put(capture,caps,sizeof(*caps))){callback_error=6;return D3DENUMRET_CANCEL;}
 count++;return D3DENUMRET_OK;
}
static int token(const char **cursor,char *out,unsigned cap){const char *p=*cursor;unsigned n=0;int q=0;
 while(*p==' '||*p=='\t')p++;
 if(!*p){*cursor=p;return 0;}if(*p=='"'){q=1;p++;}
 while(*p&&(q?*p!='"':(*p!=' '&&*p!='\t'))){if(*p=='"'||n+1>=cap)return -1;out[n++]=*p++;}
 if(q){if(*p!='"')return -1;p++;if(*p&&*p!=' '&&*p!='\t')return -1;}
 out[n]=0;*cursor=p;return n?1:-1;
}
static HANDLE fresh(const char *prefix,const char *suffix){char b[256];if(lstrlenA(prefix)+lstrlenA(suffix)>=256)return INVALID_HANDLE_VALUE;lstrcpyA(b,prefix);lstrcatA(b,suffix);return CreateFileA(b,GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);}
static int run(HWND w,const char *backend){typedef HRESULT(WINAPI *CREATE)(GUID*,void**,REFIID,IUnknown*);union{FARPROC raw;CREATE create;}fn;HMODULE m=0;IDirectDraw7 *dd=0;IDirect3D7 *d3d=0;HRESULT hr;DDSURFACEDESC2 mode;int ok=0,clean=1;
 m=LoadLibraryA("ddraw.dll");number("ddraw.load",m!=0);if(!m)goto done;fn.raw=GetProcAddress(m,"DirectDrawCreateEx");number("ddraw.entry",fn.raw!=0);if(!fn.raw)goto done;
 hr=fn.create(eq(backend,"hel")?(GUID*)DDCREATE_EMULATIONONLY:0,(void**)&dd,&dd7,0);number("ddraw.create",(DWORD)hr);if(hr!=DD_OK)goto done;
 hr=IDirectDraw7_SetCooperativeLevel(dd,w,DDSCL_NORMAL);number("ddraw.cooperative",(DWORD)hr);if(hr!=DD_OK)goto done;
 zero(&mode,sizeof(mode));mode.dwSize=sizeof(mode);hr=IDirectDraw7_GetDisplayMode(dd,&mode);number("ddraw.mode",(DWORD)hr);if(hr!=DD_OK)goto done;number("mode.width",mode.dwWidth);number("mode.height",mode.dwHeight);number("mode.bpp",mode.ddpfPixelFormat.dwRGBBitCount);
 hr=IDirectDraw7_QueryInterface(dd,&d3d7,(void**)&d3d);number("d3d.query",(DWORD)hr);number("d3d.pointer",d3d!=0);
 if(hr==E_NOINTERFACE&&!d3d){number("enum.called",0);text("interface.status","unavailable");ok=1;goto done;}
 if(hr!=DD_OK||!d3d)goto done;
 number("enum.called",1);hr=IDirect3D7_EnumDevices(d3d,device,&callback_context);number("enum.hr",(DWORD)hr);text("interface.status","available");ok=hr==DD_OK&&!callback_error&&!io_error;
done:
 number("devices",count);number("callback.error",callback_error);
 if(d3d)number("release.d3d",IDirect3D7_Release(d3d));
 if(dd){ULONG refs=IDirectDraw7_Release(dd);number("release.ddraw",refs);clean&=refs==0;}
 if(m){int unloaded=FreeLibrary(m)!=0;number("ddraw.unload",unloaded);clean&=unloaded;}
 return ok&&clean;
}
void WINAPI mainCRTStartup(void){const char *s=GetCommandLineA();char exe[512],backend[16],prefix[224],extra[2];WNDCLASSA cls;HWND w=0;OSVERSIONINFOA os;int code=1;
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
 if(token(&s,exe,sizeof(exe))!=1||token(&s,backend,sizeof(backend))!=1||token(&s,prefix,sizeof(prefix))!=1||token(&s,extra,sizeof(extra))!=0||(!eq(backend,"default")&&!eq(backend,"hel")))ExitProcess(2);
 log_file=fresh(prefix,".txt");if(log_file==INVALID_HANDLE_VALUE)ExitProcess(2);capture=fresh(prefix,"-caps.bin");if(capture==INVALID_HANDLE_VALUE){CloseHandle(log_file);ExitProcess(2);}
 text("schema","xwn-d3d-discovery-1");text("backend",backend);text("scope","capability-inventory-only");number("capacity",CAPACITY);number("caps.bytes",sizeof(D3DDEVICEDESC7));number("rendering_tested",0);
 zero(&os,sizeof(os));os.dwOSVersionInfoSize=sizeof(os);if(!GetVersionExA(&os))goto done;number("os.major",os.dwMajorVersion);number("os.minor",os.dwMinorVersion);number("os.build",os.dwBuildNumber);
 zero(&cls,sizeof(cls));cls.lpfnWndProc=DefWindowProcA;cls.hInstance=GetModuleHandleA(0);cls.lpszClassName="XWND3DDiscovery06";if(!RegisterClassA(&cls))goto done;
 w=CreateWindowA(cls.lpszClassName,"XWN D3D inventory",WS_OVERLAPPEDWINDOW,0,0,128,128,0,0,cls.hInstance,0);number("window.created",w!=0);if(w&&run(w,backend))code=0;
done:
 if(w&&!DestroyWindow(w))code=1;
 if(!CloseHandle(capture))io_error=1;
 if(io_error)code=4;
 number("exit",code);text("result",code==0?"INVENTORY_OK":"FAILED");text("end","complete");if(!CloseHandle(log_file))io_error=1;ExitProcess(io_error?4:(UINT)code);
}
