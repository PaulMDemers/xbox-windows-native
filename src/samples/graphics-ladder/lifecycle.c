/* SPDX-License-Identifier: MIT
 * Rung05 bounded system-memory churn. No mode change, primary or GPU access.
 * IsLost==DD_OK is NOT a demonstrated lost-surface/Restore path.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define DIRECTDRAW_VERSION 0x0700
#define PSAPI_VERSION 1
#define COBJMACROS
#include <windows.h>
#include <ddraw.h>
#include <psapi.h>
#define WIDTH 128
#define HEIGHT 96
#define WARMUP 8
#define CYCLES 64
#define BUDGET 1048576UL
static const GUID iid7={0x15e65ec0,0x3b9c,0x11d2,{0xb9,0x2f,0,0x60,0x97,0x97,0xea,0x5b}};
typedef BOOL(WINAPI *MEMORY)(HANDLE,PPROCESS_MEMORY_COUNTERS,DWORD);
static MEMORY memory_info;
static HANDLE log_file=INVALID_HANDLE_VALUE,capture=INVALID_HANDLE_VALUE;
static DWORD pixels[WIDTH*HEIGHT],focus_count;
static HWND focus_a,focus_b;
static int focus(HWND w,const char *key);
static unsigned cycle;
static int io_error,measured;
static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static int eq(const char *a,const char *b){return lstrcmpA(a,b)==0;}
static int put(HANDLE h,const void *p,DWORD n){DWORD w=0;if(!WriteFile(h,p,n,&w,0)||w!=n||!FlushFileBuffers(h)){io_error=1;return 0;}return 1;}
static void text(const char *key,const char *v){char b[256];wsprintfA(b,"%s=%s\r\n",key,v);put(log_file,b,lstrlenA(b));}
static void number(const char *key,DWORD v){char b[32];wsprintfA(b,"%lu",v);text(key,b);}
static void item(const char *key,DWORD v){char b[96];wsprintfA(b,"%s%u.%s",measured?"c":"w",cycle,key);number(b,v);}
static int call(const char *key,HRESULT hr){item(key,(DWORD)hr);return hr==DD_OK;}
static int token(const char **cursor,char *out,unsigned cap){const char *p=*cursor;unsigned n=0;int q=0;
 while(*p==' '||*p=='\t')p++;
 if(!*p){*cursor=p;return 0;}if(*p=='"'){q=1;p++;}
 while(*p&&(q?*p!='"':(*p!=' '&&*p!='\t'))){if(*p=='"'||n+1>=cap)return -1;out[n++]=*p++;}
 if(q){if(*p!='"')return -1;p++;if(*p&&*p!=' '&&*p!='\t')return -1;}
 out[n]=0;*cursor=p;return n?1:-1;
}
static HANDLE fresh(const char *prefix,const char *suffix){char b[256];if(lstrlenA(prefix)+lstrlenA(suffix)>=256)return INVALID_HANDLE_VALUE;lstrcpyA(b,prefix);lstrcatA(b,suffix);return CreateFileA(b,GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);}
static DWORD pattern(unsigned x,unsigned y){unsigned n=cycle+(measured?WARMUP:0);return (((n*13+x*5)&255)<<16)|(((n*7+y*11)&255)<<8)|((x^y^n)&255);}
static DWORD expected(unsigned x,unsigned y,int source,int copied){if(source)return pattern(x,y);if(copied&&x>=9&&x<105&&y>=11&&y<83)return pattern(x-6,y-6);return 0x19243b;}
static int access_surface(IDirectDrawSurface7 *s,int source,int write,int copied){DDSURFACEDESC2 d;DWORD bad=0;unsigned x,y;int valid,unlocked;char key[64];const char *label=source?(write?"src.write":"src.read"):(write?"dst.write":"dst.read");
 zero(&d,sizeof(d));d.dwSize=sizeof(d);wsprintfA(key,"%s.lock",label);
 if(!call(key,IDirectDrawSurface7_Lock(s,0,&d,DDLOCK_DONOTWAIT|(write?DDLOCK_WRITEONLY:DDLOCK_READONLY),0)))return 0;
 valid=d.lpSurface&&d.dwWidth==WIDTH&&d.dwHeight==HEIGHT&&d.lPitch>=WIDTH*4&&d.lPitch<=65536&&d.lPitch%4==0&&d.ddpfPixelFormat.dwFlags==DDPF_RGB&&d.ddpfPixelFormat.dwRGBBitCount==32&&d.ddpfPixelFormat.dwRBitMask==0xff0000&&d.ddpfPixelFormat.dwGBitMask==0xff00&&d.ddpfPixelFormat.dwBBitMask==255&&(d.ddsCaps.dwCaps&DDSCAPS_SYSTEMMEMORY)&&!(d.ddsCaps.dwCaps&DDSCAPS_VIDEOMEMORY);
 wsprintfA(key,"%s.layout",label);item(key,valid);wsprintfA(key,"%s.pitch",label);item(key,(DWORD)d.lPitch);
 if(valid)for(y=0;y<HEIGHT;y++)for(x=0;x<WIDTH;x++){DWORD *p=(DWORD*)((BYTE*)d.lpSurface+y*d.lPitch)+x,v=expected(x,y,source,copied);if(write)*p=v;else{pixels[y*WIDTH+x]=*p;if(*p!=v)bad++;}}
 wsprintfA(key,"%s.unlock",label);unlocked=call(key,IDirectDrawSurface7_Unlock(s,0));
 if(!write){wsprintfA(key,"%s.bad",label);item(key,bad);if(valid&&measured&&!put(capture,pixels,sizeof(pixels)))valid=0;}
 return valid&&unlocked&&!bad;
}
static int create(IDirectDraw7 *dd,IDirectDrawSurface7 **s,const char *key){DDSURFACEDESC2 d;zero(&d,sizeof(d));d.dwSize=sizeof(d);d.dwFlags=DDSD_WIDTH|DDSD_HEIGHT|DDSD_CAPS|DDSD_PIXELFORMAT;d.dwWidth=WIDTH;d.dwHeight=HEIGHT;d.ddsCaps.dwCaps=DDSCAPS_OFFSCREENPLAIN|DDSCAPS_SYSTEMMEMORY;d.ddpfPixelFormat.dwSize=sizeof(d.ddpfPixelFormat);d.ddpfPixelFormat.dwFlags=DDPF_RGB;d.ddpfPixelFormat.dwRGBBitCount=32;d.ddpfPixelFormat.dwRBitMask=0xff0000;d.ddpfPixelFormat.dwGBitMask=0xff00;d.ddpfPixelFormat.dwBBitMask=255;return call(key,IDirectDraw7_CreateSurface(dd,&d,s,0));}
static int one(IDirectDraw7 *dd){IDirectDrawSurface7 *src=0,*dst=0;RECT from={3,5,99,77},to={9,11,105,83};int ok=0;ULONG refs;
 if(!create(dd,&src,"src.create")||!create(dd,&dst,"dst.create"))goto done;
 if(!access_surface(src,1,1,0)||!access_surface(dst,0,1,0))goto done;
 if(measured&&cycle==0&&(!focus(focus_a,"focus.a")||!focus(focus_b,"focus.b")||!focus(focus_a,"focus.return")))goto done;
 if(!call("src.islost",IDirectDrawSurface7_IsLost(src))||!call("dst.islost",IDirectDrawSurface7_IsLost(dst)))goto done;
 if(!call("blt",IDirectDrawSurface7_Blt(dst,&to,src,&from,DDBLT_DONOTWAIT,0)))goto done;
 if(!access_surface(src,1,0,1)||!access_surface(dst,0,0,1))goto done;
 ok=1;
done:
 if(dst){refs=IDirectDrawSurface7_Release(dst);item("dst.release",refs);ok&=refs==0;}
 if(src){refs=IDirectDrawSurface7_Release(src);item("src.release",refs);ok&=refs==0;}
 item("complete",ok);return ok;
}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM a,LPARAM b){if(m==WM_SETFOCUS)focus_count++;return DefWindowProcA(w,m,a,b);}
static int focus(HWND w,const char *key){DWORD previous=focus_count;SetActiveWindow(w);SetFocus(w);{int ok=GetActiveWindow()==w&&GetFocus()==w&&focus_count>previous;number(key,ok);return ok;}}
static int memory(DWORD *commit){PROCESS_MEMORY_COUNTERS m;zero(&m,sizeof(m));m.cb=sizeof(m);if(!memory_info(GetCurrentProcess(),&m,sizeof(m)))return 0;*commit=(DWORD)m.PagefileUsage;item("memory.commit",(DWORD)m.PagefileUsage);item("memory.working",(DWORD)m.WorkingSetSize);return 1;}
static int run(HWND a,HWND b,const char *backend){typedef HRESULT(WINAPI *CREATE)(GUID*,void**,REFIID,IUnknown*);union{FARPROC raw;CREATE create;}fn;union{FARPROC raw;MEMORY query;}mem;HMODULE module=0,psapi=0;IDirectDraw7 *dd=0;DDSURFACEDESC2 mode,bad;IDirectDrawSurface7 *unexpected=0;DWORD base=0,current=0,max_growth=0;HRESULT hr;int ok=0,clean=1;
 module=LoadLibraryA("ddraw.dll");number("ddraw.load",module!=0);if(!module)goto done;fn.raw=GetProcAddress(module,"DirectDrawCreateEx");number("ddraw.entry",fn.raw!=0);if(!fn.raw)goto done;
 psapi=LoadLibraryA("psapi.dll");number("psapi.load",psapi!=0);if(!psapi)goto done;mem.raw=GetProcAddress(psapi,"GetProcessMemoryInfo");number("psapi.entry",mem.raw!=0);if(!mem.raw)goto done;memory_info=mem.query;
 hr=fn.create(eq(backend,"hel")?(GUID*)DDCREATE_EMULATIONONLY:0,(void**)&dd,&iid7,0);number("ddraw.create",(DWORD)hr);if(hr!=DD_OK)goto done;
 hr=IDirectDraw7_SetCooperativeLevel(dd,a,DDSCL_NORMAL);number("ddraw.cooperative",(DWORD)hr);if(hr!=DD_OK)goto done;
 zero(&mode,sizeof(mode));mode.dwSize=sizeof(mode);hr=IDirectDraw7_GetDisplayMode(dd,&mode);number("ddraw.mode",(DWORD)hr);if(hr!=DD_OK)goto done;number("mode.width",mode.dwWidth);number("mode.height",mode.dwHeight);number("mode.bpp",mode.ddpfPixelFormat.dwRGBBitCount);
 zero(&bad,sizeof(bad));hr=IDirectDraw7_CreateSurface(dd,&bad,&unexpected,0);number("invalid.hr",(DWORD)hr);number("invalid.null",unexpected==0);
 if(unexpected){IDirectDrawSurface7_Release(unexpected);goto done;}if(SUCCEEDED(hr))goto done;
 focus_a=a;focus_b=b;
 measured=0;for(cycle=0;cycle<WARMUP;cycle++)if(!one(dd))goto done;
 if(!memory(&base))goto done;
 number("memory.base",base);
 measured=1;for(cycle=0;cycle<CYCLES;cycle++){if(!one(dd)||!memory(&current))goto done;if(current>base&&current-base>max_growth)max_growth=current-base;if(max_growth>BUDGET)goto done;}
 number("memory.max_growth",max_growth);number("memory.budget",BUDGET);number("completed_cycles",cycle);number("restore_exercised",0);ok=1;
done:
 if(dd){ULONG refs=IDirectDraw7_Release(dd);number("release.ddraw",refs);clean&=refs==0;}
 if(psapi)clean&=FreeLibrary(psapi)!=0;
 if(module)clean&=FreeLibrary(module)!=0;
 number("cleanup.modules",clean);return ok&&clean;
}
void WINAPI mainCRTStartup(void){const char *s=GetCommandLineA();char exe[512],backend[16],prefix[224],extra[2];WNDCLASSA cls;HWND a=0,b=0;OSVERSIONINFOA os;int code=1;
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
 if(token(&s,exe,sizeof(exe))!=1||token(&s,backend,sizeof(backend))!=1||token(&s,prefix,sizeof(prefix))!=1||token(&s,extra,sizeof(extra))!=0||(!eq(backend,"default")&&!eq(backend,"hel")))ExitProcess(2);
 log_file=fresh(prefix,".txt");if(log_file==INVALID_HANDLE_VALUE)ExitProcess(2);capture=fresh(prefix,"-pixels.bin");if(capture==INVALID_HANDLE_VALUE){CloseHandle(log_file);ExitProcess(2);}
 text("schema","xwn-lifecycle-1");text("backend",backend);text("scope","system-memory-churn");text("focus.scope","calling-thread-only");number("warmup",WARMUP);number("cycles",CYCLES);
 zero(&os,sizeof(os));os.dwOSVersionInfoSize=sizeof(os);if(!GetVersionExA(&os))goto done;number("os.major",os.dwMajorVersion);number("os.minor",os.dwMinorVersion);number("os.build",os.dwBuildNumber);
 zero(&cls,sizeof(cls));cls.lpfnWndProc=proc;cls.hInstance=GetModuleHandleA(0);cls.lpszClassName="XWNLifecycle05";if(!RegisterClassA(&cls))goto done;
 a=CreateWindowA(cls.lpszClassName,"XWN lifecycle A",WS_OVERLAPPEDWINDOW,80,80,240,120,0,0,cls.hInstance,0);b=CreateWindowA(cls.lpszClassName,"XWN lifecycle B",WS_OVERLAPPEDWINDOW,100,100,240,120,0,0,cls.hInstance,0);number("windows.created",a!=0&&b!=0);if(!a||!b)goto done;
 ShowWindow(a,SW_SHOWNOACTIVATE);ShowWindow(b,SW_SHOWNOACTIVATE);if(run(a,b,backend))code=0;
done:
 if(b&&!DestroyWindow(b))code=1;
 if(a&&!DestroyWindow(a))code=1;
 if(!CloseHandle(capture))io_error=1;
 if(io_error)code=4;
 number("exit",code);text("result",code==0?"LIFECYCLE_OK":"FAILED");text("end","complete");if(!CloseHandle(log_file))io_error=1;ExitProcess(io_error?4:(UINT)code);
}
