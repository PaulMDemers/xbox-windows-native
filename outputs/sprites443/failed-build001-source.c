/* SPDX-License-Identifier: MIT
 * Rung04: owned system-memory sprites, palette updates and overlapping copies.
 * No primary surface, driver change, display-mode switch or GPU claim.
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
static HANDLE logf=INVALID_HANDLE_VALUE,files[4]={INVALID_HANDLE_VALUE,INVALID_HANDLE_VALUE,INVALID_HANDLE_VALUE,INVALID_HANDLE_VALUE};
static DWORD expected_src[SW*SH],expected_dst[DW*DH],saved[DW*DH],pixels[DW*DH];
static unsigned stage,bits;
static int io_error;
static DDPIXELFORMAT format;
static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static int eq(const char *a,const char *b){return lstrcmpA(a,b)==0;}
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
static DWORD encoded(unsigned n){return ((n&1)?format.dwRBitMask:0)|((n&2)?format.dwGBitMask:0)|((n&4)?format.dwBBitMask:0);}
static void palette_values(PALETTEENTRY *p,unsigned phase){unsigned i;for(i=0;i<256;i++){p[i].peRed=(BYTE)(i*17+phase*61);p[i].peGreen=(BYTE)(i*29+phase*37);p[i].peBlue=(BYTE)(i*43+phase*19);p[i].peFlags=0;}}
static DWORD rgb(DWORD v){
 if(bits==8)return (((v*17+(stage?61:0))&255)<<16)|(((v*29+(stage?37:0))&255)<<8)|((v*43+(stage?19:0))&255);
 return ((v&format.dwRBitMask)?0xff0000UL:0)|((v&format.dwGBitMask)?0xff00UL:0)|((v&format.dwBBitMask)?255:0);
}
static void initial(void){unsigned x,y;for(y=0;y<SH;y++)for(x=0;x<SW;x++)expected_src[y*SW+x]=(x+y)%5==0?0:bits==8?1+(x*3+y*7)%15:encoded(1+(x*3+y*7)%7);
 for(y=0;y<DH;y++)for(x=0;x<DW;x++)expected_dst[y*DW+x]=bits==8?200:encoded(5);
}
static void expected_keyed(void){unsigned x,y;for(y=5;y<15;y++)for(x=6;x<19;x++)if(x<12||x>=14){DWORD v=expected_src[(y-4)*SW+x-4];if(v)expected_dst[y*DW+x]=v;}}
static void expected_overlap(unsigned sx,unsigned sy,unsigned dx,unsigned dy){unsigned x,y;for(y=0;y<DH;y++)for(x=0;x<DW;x++)saved[y*DW+x]=expected_dst[y*DW+x];for(y=0;y<12;y++)for(x=0;x<16;x++)expected_dst[(dy+y)*DW+dx+x]=saved[(sy+y)*DW+sx+x];}
static int create_surface(IDirectDraw7 *dd,unsigned w,unsigned h,IDirectDrawSurface7 **s,const char *label){DDSURFACEDESC2 d;zero(&d,sizeof(d));d.dwSize=sizeof(d);d.dwFlags=DDSD_WIDTH|DDSD_HEIGHT|DDSD_CAPS|DDSD_PIXELFORMAT;d.dwWidth=w;d.dwHeight=h;d.ddsCaps.dwCaps=DDSCAPS_OFFSCREENPLAIN|DDSCAPS_SYSTEMMEMORY;d.ddpfPixelFormat=format;return call(label,IDirectDraw7_CreateSurface(dd,&d,s,0));}
static int access_pixels(IDirectDrawSurface7 *s,unsigned w,unsigned h,DWORD *expected,int write,HANDLE f,const char *label){DDSURFACEDESC2 d;unsigned x,y;int valid,unlocked;DWORD bad=0;char key[64];zero(&d,sizeof(d));d.dwSize=sizeof(d);
 wsprintfA(key,"%s.lock",label);if(!scall(key,IDirectDrawSurface7_Lock(s,0,&d,DDLOCK_DONOTWAIT|(write?DDLOCK_WRITEONLY:DDLOCK_READONLY),0)))return 0;
 valid=d.lpSurface&&d.dwWidth==w&&d.dwHeight==h&&d.lPitch>0&&(DWORD)d.lPitch>=w*(bits/8)&&d.lPitch<=65536&&d.lPitch%(bits/8)==0&&d.ddpfPixelFormat.dwFlags==format.dwFlags&&d.ddpfPixelFormat.dwRGBBitCount==bits&&d.ddpfPixelFormat.dwRBitMask==format.dwRBitMask&&d.ddpfPixelFormat.dwGBitMask==format.dwGBitMask&&d.ddpfPixelFormat.dwBBitMask==format.dwBBitMask&&(d.ddsCaps.dwCaps&DDSCAPS_SYSTEMMEMORY)&&!(d.ddsCaps.dwCaps&DDSCAPS_VIDEOMEMORY);
 wsprintfA(key,"%s.layout",label);snum(key,valid);wsprintfA(key,"%s.pitch",label);snum(key,(DWORD)d.lPitch);
 if(valid)for(y=0;y<h;y++)for(x=0;x<w;x++){BYTE *p=(BYTE*)d.lpSurface+y*d.lPitch+x*(bits/8);DWORD v=expected[y*w+x];if(write){if(bits==8)*p=(BYTE)v;else if(bits==16)*(WORD*)p=(WORD)v;else *(DWORD*)p=v;}else{v=bits==8?*p:bits==16?*(WORD*)p:*(DWORD*)p;pixels[y*w+x]=v;if(v!=expected[y*w+x])bad++;}}
 wsprintfA(key,"%s.unlock",label);unlocked=scall(key,IDirectDrawSurface7_Unlock(s,0));
 if(!write){wsprintfA(key,"%s.mismatches",label);snum(key,bad);if(valid&&!put(f,pixels,w*h*4))valid=0;}
 return valid&&unlocked&&!bad;
}
static int converted(IDirectDrawSurface7 *s){HDC dc=0,mem=0;HBITMAP bitmap=0;HGDIOBJ old=0;BITMAPINFO info;DWORD *data=0,bad=0;unsigned i;int ok=0,clean=1;zero(&info,sizeof(info));info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);info.bmiHeader.biWidth=DW;info.bmiHeader.biHeight=-DH;info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;
 if(!scall("gdi.getdc",IDirectDrawSurface7_GetDC(s,&dc)))goto done;
 mem=CreateCompatibleDC(dc);if(!mem)goto done;bitmap=CreateDIBSection(mem,&info,DIB_RGB_COLORS,(void**)&data,0,0);if(!bitmap||!data)goto done;
 old=SelectObject(mem,bitmap);if(!old||old==HGDI_ERROR)goto done;
 if(!BitBlt(mem,0,0,DW,DH,dc,0,0,SRCCOPY)||!GdiFlush())goto done;
 for(i=0;i<DW*DH;i++){pixels[i]=data[i]&0xffffffUL;if(pixels[i]!=rgb(expected_dst[i]))bad++;}
 ok=put(files[2],pixels,sizeof(pixels));
done:
 if(old&&old!=HGDI_ERROR)clean&=SelectObject(mem,old)!=0;
 if(bitmap)clean&=DeleteObject(bitmap)!=0;
 if(mem)clean&=DeleteDC(mem)!=0;
 if(dc)clean&=scall("gdi.releasedc",IDirectDrawSurface7_ReleaseDC(s,dc));
 snum("gdi.capture",ok&&clean);snum("gdi.mismatches",bad);return ok&&clean&&!bad;
}
static int palette_read(IDirectDrawPalette *p){PALETTEENTRY actual[256],expected[256];unsigned i;int same=1;palette_values(expected,stage?1:0);zero(actual,sizeof(actual));if(!scall("palette.get",IDirectDrawPalette_GetEntries(p,0,0,256,actual)))return 0;
 for(i=0;i<256;i++)if(actual[i].peRed!=expected[i].peRed||actual[i].peGreen!=expected[i].peGreen||actual[i].peBlue!=expected[i].peBlue||actual[i].peFlags!=0)same=0;
 snum("palette.exact",same);return put(files[3],actual,sizeof(actual))&&same;
}
static int run(HWND window,const char *backend){typedef HRESULT(WINAPI *CREATE)(GUID*,void**,REFIID,IUnknown*);union{FARPROC raw;CREATE create;}fn;HMODULE module=0;IDirectDraw7 *dd=0;IDirectDrawSurface7 *src=0,*dst=0;IDirectDrawPalette *pal=0;IDirectDrawClipper *clipper=0;DDSURFACEDESC2 mode;DDCOLORKEY key={0,0},got;PALETTEENTRY colors[256];struct{RGNDATAHEADER h;RECT r[2];}region,observed;DWORD size;RECT from={0,0,16,12},to={4,4,20,16};int ok=0,clean=1;unsigned i;
 module=LoadLibraryA("ddraw.dll");number("ddraw.load",module!=0);if(!module)goto done;fn.raw=GetProcAddress(module,"DirectDrawCreateEx");number("ddraw.entry",fn.raw!=0);if(!fn.raw)goto done;
 if(!call("ddraw.create",fn.create(eq(backend,"hel")?(GUID*)DDCREATE_EMULATIONONLY:0,(void**)&dd,&iid7,0)))goto done;
 if(!call("ddraw.cooperative",IDirectDraw7_SetCooperativeLevel(dd,window,DDSCL_NORMAL)))goto done;
 zero(&mode,sizeof(mode));mode.dwSize=sizeof(mode);if(!call("ddraw.mode",IDirectDraw7_GetDisplayMode(dd,&mode)))goto done;number("mode.width",mode.dwWidth);number("mode.height",mode.dwHeight);number("mode.bpp",mode.ddpfPixelFormat.dwRGBBitCount);
 if(!create_surface(dd,SW,SH,&src,"source.create")||!create_surface(dd,DW,DH,&dst,"dest.create"))goto done;
 if(bits==8){palette_values(colors,0);if(!call("palette.create",IDirectDraw7_CreatePalette(dd,DDPCAPS_8BIT|DDPCAPS_ALLOW256,colors,&pal,0)))goto done;if(!call("source.palette",IDirectDrawSurface7_SetPalette(src,pal))||!call("dest.palette",IDirectDrawSurface7_SetPalette(dst,pal)))goto done;}
 if(!call("key.set",IDirectDrawSurface7_SetColorKey(src,DDCKEY_SRCBLT,&key)))goto done;
 zero(&got,sizeof(got));if(!call("key.get",IDirectDrawSurface7_GetColorKey(src,DDCKEY_SRCBLT,&got)))goto done;number("key.low",got.dwColorSpaceLowValue);number("key.high",got.dwColorSpaceHighValue);if(got.dwColorSpaceLowValue||got.dwColorSpaceHighValue)goto done;
 if(!call("clipper.create",IDirectDraw7_CreateClipper(dd,0,&clipper,0)))goto done;
 zero(&region,sizeof(region));region.h.dwSize=sizeof(RGNDATAHEADER);region.h.iType=RDH_RECTANGLES;region.h.nCount=2;region.h.nRgnSize=sizeof(region.r);SetRect(&region.h.rcBound,6,5,19,15);SetRect(&region.r[0],6,5,12,15);SetRect(&region.r[1],14,5,19,15);
 if(!call("clipper.set",IDirectDrawClipper_SetClipList(clipper,(RGNDATA*)&region,0)))goto done;
 zero(&observed,sizeof(observed));size=sizeof(observed);if(!call("clipper.get",IDirectDrawClipper_GetClipList(clipper,0,(RGNDATA*)&observed,&size)))goto done;
 {int exact=size==sizeof(region);for(i=0;i<sizeof(region);i++)if(((BYTE*)&observed)[i]!=((BYTE*)&region)[i])exact=0;number("clipper.exact",exact);if(!exact)goto done;}
 if(!call("dest.clipper",IDirectDrawSurface7_SetClipper(dst,clipper)))goto done;
 initial();stage=0;if(!access_pixels(src,SW,SH,expected_src,1,files[0],"source.write")||!access_pixels(dst,DW,DH,expected_dst,1,files[1],"dest.write"))goto done;
 for(stage=0;stage<4;stage++){
  if(stage==0){if(!scall("blit.keyed",IDirectDrawSurface7_Blt(dst,&to,src,&from,DDBLT_DONOTWAIT|DDBLT_KEYSRC,0)))goto done;expected_keyed();}
  else if(stage==1){if(bits==8){palette_values(colors,1);if(!scall("palette.set",IDirectDrawPalette_SetEntries(pal,0,0,256,colors)))goto done;}else snum("palette.not_applicable",1);}
  else{if(stage==2){if(!scall("clipper.detach",IDirectDrawSurface7_SetClipper(dst,0)))goto done;SetRect(&from,4,4,20,16);SetRect(&to,7,6,23,18);}else{SetRect(&from,7,6,23,18);SetRect(&to,3,3,19,15);}if(!scall("blit.overlap",IDirectDrawSurface7_Blt(dst,&to,dst,&from,DDBLT_DONOTWAIT,0)))goto done;expected_overlap(from.left,from.top,to.left,to.top);}
  if(bits==8&&!palette_read(pal))goto done;
  if(!access_pixels(src,SW,SH,expected_src,0,files[0],"source.read")||!access_pixels(dst,DW,DH,expected_dst,0,files[1],"dest.read")||!converted(dst))goto done;
  snum("complete",1);
 }
 ok=1;
done:
 if(dst&&clipper)clean&=call("cleanup.clipper",IDirectDrawSurface7_SetClipper(dst,0));
 if(src&&pal)clean&=call("cleanup.source.palette",IDirectDrawSurface7_SetPalette(src,0));
 if(dst&&pal)clean&=call("cleanup.dest.palette",IDirectDrawSurface7_SetPalette(dst,0));
 if(dst)number("release.dest",IDirectDrawSurface7_Release(dst));
 if(src)number("release.source",IDirectDrawSurface7_Release(src));
 if(pal)number("release.palette",IDirectDrawPalette_Release(pal));
 if(clipper)number("release.clipper",IDirectDrawClipper_Release(clipper));
 if(dd)number("release.ddraw",IDirectDraw7_Release(dd));
 if(module){int unloaded=FreeLibrary(module)!=0;number("ddraw.unload",unloaded);clean&=unloaded;}
 return ok&&clean;
}
void WINAPI mainCRTStartup(void){const char *s=GetCommandLineA();char exe[512],backend[16],kind[16],prefix[224],extra[2];WNDCLASSA cls;HWND window=0;OSVERSIONINFOA os;int code=1;unsigned i;
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
 if(token(&s,exe,sizeof(exe))!=1||token(&s,backend,sizeof(backend))!=1||token(&s,kind,sizeof(kind))!=1||token(&s,prefix,sizeof(prefix))!=1||token(&s,extra,sizeof(extra))!=0||(!eq(backend,"default")&&!eq(backend,"hel"))||(!eq(kind,"index8")&&!eq(kind,"rgb565")&&!eq(kind,"rgb32")))ExitProcess(2);
 logf=fresh(prefix,".txt");if(logf==INVALID_HANDLE_VALUE)ExitProcess(2);
 text("schema","xwn-sprites-1");text("rung","04");text("backend",backend);text("format",kind);text("scope","owned-system-memory");text("visual","UNVERIFIED");
 files[0]=fresh(prefix,"-source.bin");files[1]=fresh(prefix,"-dest.bin");files[2]=fresh(prefix,"-rgb.bin");files[3]=fresh(prefix,"-palette.bin");for(i=0;i<4;i++)if(files[i]==INVALID_HANDLE_VALUE){code=2;goto done;}
 bits=eq(kind,"index8")?8:eq(kind,"rgb565")?16:32;zero(&format,sizeof(format));format.dwSize=sizeof(format);format.dwFlags=DDPF_RGB|(bits==8?DDPF_PALETTEINDEXED8:0);format.dwRGBBitCount=bits;
 if(bits!=8){format.dwRBitMask=bits==16?0xf800:0xff0000;format.dwGBitMask=bits==16?0x7e0:0xff00;format.dwBBitMask=bits==16?31:255;}
 zero(&os,sizeof(os));os.dwOSVersionInfoSize=sizeof(os);if(!GetVersionExA(&os))goto done;number("os.major",os.dwMajorVersion);number("os.minor",os.dwMinorVersion);number("os.build",os.dwBuildNumber);
 zero(&cls,sizeof(cls));cls.lpfnWndProc=DefWindowProcA;cls.hInstance=GetModuleHandleA(0);cls.lpszClassName="XWNSprites04";if(!RegisterClassA(&cls))goto done;window=CreateWindowA(cls.lpszClassName,"XWN sprites",WS_OVERLAPPEDWINDOW,0,0,128,128,0,0,cls.hInstance,0);number("window.create",window!=0);if(!window)goto done;
 if(run(window,backend))code=0;
done:
 if(window&&!DestroyWindow(window))code=1;
 for(i=0;i<4;i++)if(files[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(files[i]))io_error=1;
 if(io_error)code=4;
 number("exit",code);text("result",code==0?"SPRITES_OK":"FAILED");text("end","complete");
 if(!CloseHandle(logf))io_error=1;
 ExitProcess(io_error?4:(UINT)code);
}
