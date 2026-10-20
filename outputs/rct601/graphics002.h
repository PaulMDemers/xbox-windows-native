/* MIT. Real GDI pixel control and DirectDraw interface/surface control. */
#define COBJMACROS
#include <ddraw.h>
#include <stddef.h>
typedef char desc_size601[sizeof(DDSURFACEDESC)==108?1:-1];
typedef char dd_coop_slot601[offsetof(IDirectDrawVtbl,SetCooperativeLevel)==20*4?1:-1];
typedef char dd_surface_slot601[offsetof(IDirectDrawVtbl,CreateSurface)==6*4?1:-1];
typedef char surface_desc_slot601[offsetof(IDirectDrawSurfaceVtbl,GetSurfaceDesc)==22*4?1:-1];
typedef char surface_blt_slot601[offsetof(IDirectDrawSurfaceVtbl,Blt)==5*4?1:-1];
typedef BOOL (WINAPI *BLIT601)(HDC,int,int,int,int,HDC,int,int,DWORD);
typedef HBITMAP (WINAPI *DIB601)(HDC,const BITMAPINFO*,UINT,void**,HANDLE,DWORD);
typedef int (WINAPI *STRETCH601)(HDC,int,int,int,int,int,int,int,int,const void*,const BITMAPINFO*,UINT,DWORD);
typedef HRESULT (WINAPI *DD601)(GUID*,LPDIRECTDRAW*,IUnknown*);
static void zero601(void *p,DWORD n) {BYTE *b=p;while(n--)*b++=0;}
static void number601(const char *name,DWORD v) {char s[100];wsprintfA(s,"%s=%08lx\r\n",name,v);record(s);}
static BOOL graphics601(void) {
    HMODULE g=0,d=0;BLIT601 blit;DIB601 dib;STRETCH601 stretch;DD601 create;
    union {FARPROC generic;DIB601 dib;} dib_address;
    HDC src=0,dst=0;HBITMAP a=0,b=0;HGDIOBJ olda=0,oldb=0;DWORD *sa=0,*sb=0;
    BITMAPINFO info,bad;DWORD i,j;BOOL ok=FALSE;HWND window=0;
    LPDIRECTDRAW dd=0,invalid=0;LPDIRECTDRAWSURFACE surface=0;
    DDSURFACEDESC desc,got;DDBLTFX fx;HRESULT hr;
    GUID invalid_guid={0x60160160,0x1601,0x2601,{1,2,3,4,5,6,7,8}};
    g=LoadLibraryA("GDI32.DLL");d=LoadLibraryA("DDRAW.DLL");
    if(!g||!d)goto end;
    blit=(BLIT601)GetProcAddress(g,"BitBlt");dib_address.generic=GetProcAddress(g,"CreateDIBSection");dib=dib_address.dib;
    stretch=(STRETCH601)GetProcAddress(g,"StretchDIBits");create=(DD601)GetProcAddress(d,"DirectDrawCreate");
    if(!blit||!dib||!stretch||!create)goto end;
    zero601(&info,sizeof(info));info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);
    info.bmiHeader.biWidth=8;info.bmiHeader.biHeight=-8;info.bmiHeader.biPlanes=1;
    info.bmiHeader.biBitCount=32;info.bmiHeader.biCompression=BI_RGB;
    bad=info;bad.bmiHeader.biSize=0;
    if(dib(0,&bad,DIB_RGB_COLORS,(void**)&sa,0,0)||sa)goto end;
    a=dib(0,&info,DIB_RGB_COLORS,(void**)&sa,0,0);
    b=dib(0,&info,DIB_RGB_COLORS,(void**)&sb,0,0);
    if(!a||!b||!sa||!sb)goto end;
    src=CreateCompatibleDC(0);dst=CreateCompatibleDC(0);if(!src||!dst)goto end;
    olda=SelectObject(src,a);oldb=SelectObject(dst,b);if(!olda||!oldb)goto end;
    if(blit(0,0,0,8,8,src,0,0,SRCCOPY))goto end;
    for(j=0;j<33;j++) {
        for(i=0;i<64;i++){sa[i]=(i*0x010203u+j*0x010101u)&0xffffffu;sb[i]=0;}
        if(!blit(dst,0,0,8,8,src,0,0,SRCCOPY)||!GdiFlush())goto end;
        for(i=0;i<64;i++)if(sb[i]!=sa[i])goto end;
    }
    number601("bitblt_pixel_rounds",33);
    for(i=0;i<64;i++)sb[i]=0;
    if(stretch(dst,0,0,8,8,0,0,8,8,sa,&info,DIB_RGB_COLORS,SRCCOPY)!=8||!GdiFlush())goto end;
    for(i=0;i<64;i++)if(sb[i]!=sa[i])goto end;
    number601("stretch_pixels",64);
    hr=create(&invalid_guid,&invalid,0);number601("invalid_dd_hresult",(DWORD)hr);
    if(SUCCEEDED(hr)||invalid)goto end;
    hr=create(0,&dd,0);number601("dd_hresult",(DWORD)hr);if(FAILED(hr)||!dd)goto end;
    window=CreateWindowExA(0,"STATIC","XWN601 owned graphics control",WS_OVERLAPPED,0,0,160,120,0,0,GetModuleHandleA(0),0);
    if(!window)goto end;
    hr=IDirectDraw_SetCooperativeLevel(dd,window,DDSCL_NORMAL);number601("cooperative_hresult",(DWORD)hr);if(FAILED(hr))goto end;
    zero601(&desc,sizeof(desc));desc.dwSize=sizeof(desc);
    desc.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT;desc.dwWidth=8;desc.dwHeight=8;
    desc.ddsCaps.dwCaps=DDSCAPS_SYSTEMMEMORY|DDSCAPS_OFFSCREENPLAIN;
    hr=IDirectDraw_CreateSurface(dd,&desc,&surface,0);number601("surface_hresult",(DWORD)hr);if(FAILED(hr)||!surface)goto end;
    zero601(&got,sizeof(got));got.dwSize=sizeof(got);
    hr=IDirectDrawSurface_GetSurfaceDesc(surface,&got);number601("desc_hresult",(DWORD)hr);
    if(FAILED(hr)||got.dwWidth!=8||got.dwHeight!=8||!(got.ddsCaps.dwCaps&DDSCAPS_SYSTEMMEMORY))goto end;
    number601("surface_caps",got.ddsCaps.dwCaps);number601("surface_bpp",got.ddpfPixelFormat.dwRGBBitCount);
    zero601(&fx,sizeof(fx));fx.dwSize=sizeof(fx);fx.dwFillColor=0;
    hr=IDirectDrawSurface_Blt(surface,0,0,0,DDBLT_COLORFILL|DDBLT_WAIT,&fx);
    number601("surface_blt_hresult",(DWORD)hr);if(FAILED(hr))goto end;
    ok=TRUE;
end:
    if(surface)IDirectDrawSurface_Release(surface);
    if(dd)IDirectDraw_Release(dd);
    if(invalid)IDirectDraw_Release(invalid);
    if(window)DestroyWindow(window);
    if(src&&olda)SelectObject(src,olda);
    if(dst&&oldb)SelectObject(dst,oldb);
    if(a)DeleteObject(a);
    if(b)DeleteObject(b);
    if(src)DeleteDC(src);
    if(dst)DeleteDC(dst);
    /* Retain module references: code stays mapped until process exit. */
    record(ok?"GRAPHICS601 PASS\r\n":"GRAPHICS601 FAIL\r\n");return ok;
}
