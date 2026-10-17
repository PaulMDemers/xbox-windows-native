/* SPDX-License-Identifier: MIT
 * Original NT5 user-mode graphics samples. No driver changes or mode switches.
 * Build without a CRT; dynamically load DirectDraw so rung 00 has no dependency.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define DIRECTDRAW_VERSION 0x0700
#define COBJMACROS
#include <windows.h>
#include <ddraw.h>

#define SW 64
#define SH 48
#define DW 96
#define DH 80
#define SENTINEL 0x00132947UL
static const GUID dd7_iid = {0x15e65ec0,0x3b9c,0x11d2,{0xb9,0x2f,0x00,0x60,0x97,0x97,0xea,0x5b}};
static HANDLE report = INVALID_HANDLE_VALUE, source_file = INVALID_HANDLE_VALUE;
static HANDLE dest_file = INVALID_HANDLE_VALUE;
static DWORD source_pixels[SW*SH], dest_pixels[DW*DH];
static int io_failed, cancelled;

static void zero(void *p, DWORD size) {
    BYTE *b = (BYTE *)p;
    while (size--) *b++ = 0;
}
static int equal(const char *a, const char *b) { return lstrcmpA(a,b)==0; }
static int put(HANDLE f, const void *p, DWORD n) {
    DWORD written = 0;
    if (!WriteFile(f,p,n,&written,NULL) || written!=n) { io_failed=1; return 0; }
    return 1;
}
static void line(const char *key, const char *value) {
    if (report==INVALID_HANDLE_VALUE) return;
    put(report,key,(DWORD)lstrlenA(key)); put(report,"=",1);
    put(report,value,(DWORD)lstrlenA(value)); put(report,"\r\n",2);
    if (!FlushFileBuffers(report)) io_failed=1;
}
static void number(const char *key, DWORD n) {
    char b[32]; wsprintfA(b,"%lu",n); line(key,b);
}
static int call(const char *key, HRESULT hr) {
    char b[16]; wsprintfA(b,"%08lX",(DWORD)hr); line(key,b);
    return hr==DD_OK;
}
static int log_bool(const char *key, BOOL ok) {
    number(key,ok ? 1 : 0);
    if (!ok) number("win32.error",GetLastError());
    return ok!=0;
}
/* Token grammar: spaces delimit arguments; a whole token may be quoted.
 * Embedded quotes/escapes and oversized tokens are refused, never truncated. */
static int token(const char **cursor, char *out, unsigned cap) {
    const char *p=*cursor; unsigned n=0; int quoted=0;
    while (*p==' ' || *p=='\t') ++p;
    if (!*p) { *cursor=p; return 0; }
    if (*p=='"') { quoted=1; ++p; }
    while (*p && (quoted ? *p!='"' : (*p!=' ' && *p!='\t'))) {
        if (*p=='"' || n+1>=cap) return -1;
        out[n++]=*p++;
    }
    if (quoted) {
        if (*p!='"') return -1;
        ++p;
        if (*p && *p!=' ' && *p!='\t') return -1;
    }
    out[n]=0; *cursor=p; return n ? 1 : -1;
}
static HANDLE exclusive(const char *prefix, const char *suffix) {
    char path[256];
    if (lstrlenA(prefix)+lstrlenA(suffix)>=256) return INVALID_HANDLE_VALUE;
    lstrcpyA(path,prefix); lstrcatA(path,suffix);
    return CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,
                       FILE_ATTRIBUTE_NORMAL,NULL);
}
static DWORD pattern(unsigned x, unsigned y) {
    return (((x*17+y*3)&255UL)<<16) | (((x*5+y*11)&255UL)<<8) | ((x*7+y*19)&255UL);
}
static void initialize(DWORD *src, DWORD *dst) {
    unsigned x,y;
    for (y=0;y<SH;++y) for (x=0;x<SW;++x) src[y*SW+x]=pattern(x,y);
    for (y=0;y<DH;++y) for (x=0;x<DW;++x) dst[y*DW+x]=SENTINEL;
}
static DWORD mismatches(void) {
    unsigned x,y; DWORD bad=0, expected;
    for (y=0;y<SH;++y) for (x=0;x<SW;++x)
        if (source_pixels[y*SW+x]!=pattern(x,y)) ++bad;
    for (y=0;y<DH;++y) for (x=0;x<DW;++x) {
        expected=(x>=8 && x<56 && y>=10 && y<42) ? pattern(x-8+3,y-10+4) : SENTINEL;
        if (dest_pixels[y*DW+x]!=expected) ++bad;
    }
    return bad;
}
static BITMAPINFO bitmap(unsigned w, unsigned h) {
    BITMAPINFO b; zero(&b,sizeof(b)); b.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);
    b.bmiHeader.biWidth=(LONG)w; b.bmiHeader.biHeight=-(LONG)h;
    b.bmiHeader.biPlanes=1; b.bmiHeader.biBitCount=32; b.bmiHeader.biCompression=BI_RGB;
    return b;
}
static LRESULT CALLBACK window_proc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp) {
    if (msg==WM_CLOSE) { cancelled=1; DestroyWindow(hwnd); return 0; }
    if (msg==WM_PAINT) {
        PAINTSTRUCT ps; HDC dc=BeginPaint(hwnd,&ps); BITMAPINFO b=bitmap(DW,DH);
        SetDIBitsToDevice(dc,16,16,DW,DH,0,0,0,DH,dest_pixels,&b,DIB_RGB_COLORS);
        const char *a="Original RGB test: display appearance is a separate observation.";
        const char *btext="Auto-close in five seconds. No resolution or driver change.";
        TextOutA(dc,16,110,a,lstrlenA(a)); TextOutA(dc,16,135,btext,lstrlenA(btext));
        EndPaint(hwnd,&ps); return 0;
    }
    return DefWindowProcA(hwnd,msg,wp,lp);
}
static HWND make_window(void) {
    WNDCLASSA c; zero(&c,sizeof(c)); c.lpfnWndProc=window_proc;
    c.hInstance=GetModuleHandleA(NULL); c.lpszClassName="XWNGraphicsLadder1";
    c.hCursor=LoadCursorA(NULL,IDC_ARROW); c.hbrBackground=(HBRUSH)(COLOR_WINDOW+1);
    if (!RegisterClassA(&c)) return NULL;
    return CreateWindowA(c.lpszClassName,"XWN graphics ladder - owned sample",
        WS_OVERLAPPEDWINDOW,40,40,600,220,NULL,NULL,c.hInstance,NULL);
}
static void view(HWND hwnd) {
    DWORD start=GetTickCount(); MSG m;
    ShowWindow(hwnd,SW_SHOWNORMAL); UpdateWindow(hwnd);
    while (!cancelled && (DWORD)(GetTickCount()-start)<5000) {
        while (PeekMessageA(&m,NULL,0,0,PM_REMOVE)) { TranslateMessage(&m); DispatchMessageA(&m); }
        Sleep(10);
    }
}
static int gdi(void) {
    HDC a=NULL,b=NULL; HBITMAP sa=NULL,sb=NULL; HGDIOBJ olda=NULL,oldb=NULL;
    DWORD *pa=NULL,*pb=NULL; unsigned i; int ok=0, clean=1;
    BITMAPINFO ia=bitmap(SW,SH),ib=bitmap(DW,DH);
    a=CreateCompatibleDC(NULL); b=CreateCompatibleDC(NULL);
    if (!log_bool("gdi.dc",a && b)) goto done;
    sa=CreateDIBSection(a,&ia,DIB_RGB_COLORS,(void **)&pa,NULL,0);
    sb=CreateDIBSection(b,&ib,DIB_RGB_COLORS,(void **)&pb,NULL,0);
    if (!log_bool("gdi.dib",sa && sb && pa && pb)) goto done;
    olda=SelectObject(a,sa); oldb=SelectObject(b,sb);
    if (!log_bool("gdi.select",olda && olda!=HGDI_ERROR && oldb && oldb!=HGDI_ERROR)) goto done;
    initialize(pa,pb);
    if (!log_bool("gdi.blit",BitBlt(b,8,10,48,32,a,3,4,SRCCOPY))) goto done;
    if (!log_bool("gdi.flush",GdiFlush())) goto done;
    for (i=0;i<SW*SH;++i) source_pixels[i]=pa[i]&0xffffffUL;
    for (i=0;i<DW*DH;++i) dest_pixels[i]=pb[i]&0xffffffUL;
    ok=1;
done:
    if (olda && olda!=HGDI_ERROR) clean &= SelectObject(a,olda)!=NULL;
    if (oldb && oldb!=HGDI_ERROR) clean &= SelectObject(b,oldb)!=NULL;
    if (sa) clean &= DeleteObject(sa)!=0;
    if (sb) clean &= DeleteObject(sb)!=0;
    if (a) clean &= DeleteDC(a)!=0;
    if (b) clean &= DeleteDC(b)!=0;
    number("gdi.cleanup",clean); return ok && clean;
}
static void caps(const char *prefix, const DDCAPS *c) {
    char key[64];
#define CAP(field) lstrcpyA(key,prefix); lstrcatA(key,"." #field); number(key,c->field)
    CAP(dwCaps); CAP(dwCaps2); CAP(dwCKeyCaps); CAP(dwFXCaps);
    CAP(dwPalCaps); CAP(dwVidMemTotal); CAP(dwVidMemFree);
#undef CAP
}
static int memory_surface(IDirectDraw7 *dd, unsigned w, unsigned h,
                          IDirectDrawSurface7 **out, const char *label) {
    DDSURFACEDESC2 d; zero(&d,sizeof(d)); d.dwSize=sizeof(d);
    d.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT|DDSD_PIXELFORMAT;
    d.dwWidth=w; d.dwHeight=h; d.ddsCaps.dwCaps=DDSCAPS_OFFSCREENPLAIN|DDSCAPS_SYSTEMMEMORY;
    d.ddpfPixelFormat.dwSize=sizeof(DDPIXELFORMAT); d.ddpfPixelFormat.dwFlags=DDPF_RGB;
    d.ddpfPixelFormat.dwRGBBitCount=32; d.ddpfPixelFormat.dwRBitMask=0xff0000;
    d.ddpfPixelFormat.dwGBitMask=0xff00; d.ddpfPixelFormat.dwBBitMask=0xff;
    return call(label,IDirectDraw7_CreateSurface(dd,&d,out,NULL));
}
static int surface_pixels(IDirectDrawSurface7 *s, unsigned w, unsigned h,
                          DWORD *pixels, int write, const char *label) {
    DDSURFACEDESC2 d; DWORD flags=DDLOCK_DONOTWAIT|(write ? DDLOCK_WRITEONLY : DDLOCK_READONLY);
    char key[96]; unsigned x,y; int valid, unlocked;
    zero(&d,sizeof(d)); d.dwSize=sizeof(d);
    lstrcpyA(key,label); lstrcatA(key,".lock");
    if (!call(key,IDirectDrawSurface7_Lock(s,NULL,&d,flags,NULL))) return 0;
    valid=d.lpSurface && d.dwWidth==w && d.dwHeight==h && d.lPitch>0 &&
        (DWORD)d.lPitch>=w*4 && d.lPitch<=65536 && d.lPitch%4==0 &&
        d.ddpfPixelFormat.dwFlags==DDPF_RGB && d.ddpfPixelFormat.dwRGBBitCount==32 &&
        d.ddpfPixelFormat.dwRBitMask==0xff0000 && d.ddpfPixelFormat.dwGBitMask==0xff00 &&
        d.ddpfPixelFormat.dwBBitMask==0xff &&
        (d.ddsCaps.dwCaps&DDSCAPS_SYSTEMMEMORY)!=0 &&
        (d.ddsCaps.dwCaps&DDSCAPS_VIDEOMEMORY)==0;
    lstrcpyA(key,label); lstrcatA(key,".layout"); number(key,valid);
    lstrcpyA(key,label); lstrcatA(key,".pitch"); number(key,(DWORD)d.lPitch);
    if (valid) for (y=0;y<h;++y) {
        DWORD *row=(DWORD *)((BYTE *)d.lpSurface+y*d.lPitch);
        for (x=0;x<w;++x) {
            if (write) row[x]=pixels[y*w+x]; else pixels[y*w+x]=row[x]&0xffffffUL;
        }
    }
    /* No captured pointer is retained after Unlock, including refusal paths. */
    lstrcpyA(key,label); lstrcatA(key,".unlock");
    unlocked=call(key,IDirectDrawSurface7_Unlock(s,NULL));
    return valid && unlocked;
}
static int directdraw(HWND hwnd, const char *backend, int pixels) {
    typedef HRESULT (WINAPI *CREATE)(GUID *, void **, REFIID, IUnknown *);
    union { FARPROC generic; CREATE create; } proc;
    HMODULE mod=NULL; IDirectDraw7 *dd=NULL;
    IDirectDrawSurface7 *src=NULL,*dst=NULL; DDCAPS hw,hel; DDSURFACEDESC2 mode;
    GUID *choice=NULL; RECT from={3,4,51,36},to={8,10,56,42}; int ok=0;
    mod=LoadLibraryA("ddraw.dll");
    if (!log_bool("ddraw.load",mod!=NULL)) goto done;
    proc.generic=GetProcAddress(mod,"DirectDrawCreateEx");
    if (!log_bool("ddraw.entry",proc.generic!=NULL)) goto done;
    if (equal(backend,"hel")) choice=(GUID *)DDCREATE_EMULATIONONLY;
    if (equal(backend,"hal")) choice=(GUID *)DDCREATE_HARDWAREONLY;
    if (!call("ddraw.create",proc.create(choice,(void **)&dd,&dd7_iid,NULL))) goto done;
    if (!call("ddraw.cooperative",IDirectDraw7_SetCooperativeLevel(dd,hwnd,DDSCL_NORMAL))) goto done;
    zero(&hw,sizeof(hw)); zero(&hel,sizeof(hel)); hw.dwSize=sizeof(hw); hel.dwSize=sizeof(hel);
    if (!call("ddraw.caps",IDirectDraw7_GetCaps(dd,&hw,&hel))) goto done;
    caps("caps.hardware",&hw); caps("caps.hel",&hel);
    zero(&mode,sizeof(mode)); mode.dwSize=sizeof(mode);
    if (!call("ddraw.mode",IDirectDraw7_GetDisplayMode(dd,&mode))) goto done;
    number("mode.width",mode.dwWidth); number("mode.height",mode.dwHeight);
    number("mode.bpp",mode.ddpfPixelFormat.dwRGBBitCount);
    if (!pixels) { ok=1; goto done; }
    if (!memory_surface(dd,SW,SH,&src,"surface.source.create")) goto done;
    if (!memory_surface(dd,DW,DH,&dst,"surface.dest.create")) goto done;
    initialize(source_pixels,dest_pixels);
    if (!surface_pixels(src,SW,SH,source_pixels,1,"source.write")) goto done;
    if (!surface_pixels(dst,DW,DH,dest_pixels,1,"dest.write")) goto done;
    if (!call("surface.blit",IDirectDrawSurface7_Blt(dst,&to,src,&from,DDBLT_DONOTWAIT,NULL))) goto done;
    if (!surface_pixels(src,SW,SH,source_pixels,0,"source.read")) goto done;
    if (!surface_pixels(dst,DW,DH,dest_pixels,0,"dest.read")) goto done;
    ok=1;
done:
    if (dst) number("release.dest",IDirectDrawSurface7_Release(dst));
    if (src) number("release.source",IDirectDrawSurface7_Release(src));
    if (dd) number("release.ddraw",IDirectDraw7_Release(dd));
    if (mod && !log_bool("ddraw.unload",FreeLibrary(mod))) ok=0;
    return ok;
}
void __attribute__((stdcall)) mainCRTStartup(void) {
    const char *cursor=GetCommandLineA(); char exe[512],rung[8],backend[16],prefix[224],display[16],extra[2];
    OSVERSIONINFOA os; HWND hwnd=NULL; int ok=0, code=1, pixels=0; DWORD bad=0;
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    if (token(&cursor,exe,sizeof(exe))!=1 || token(&cursor,rung,sizeof(rung))!=1 ||
        token(&cursor,backend,sizeof(backend))!=1 || token(&cursor,prefix,sizeof(prefix))!=1 ||
        token(&cursor,display,sizeof(display))!=1 || token(&cursor,extra,sizeof(extra))!=0 ||
        (!equal(rung,"00") && !equal(rung,"01") && !equal(rung,"02")) ||
        (!equal(backend,"default") && !equal(backend,"hel") && !equal(backend,"hal")) ||
        (!equal(display,"view") && !equal(display,"quiet")) ||
        (equal(rung,"00") && !equal(backend,"default")) ||
        (equal(rung,"02") && equal(backend,"hal"))) {
        const char *help="Usage: ladder.exe 00|01|02 default|hel|hal fresh-prefix view|quiet\r\n00: default. 01: default/hel/hal. 02: default/hel only. No mode switch or reboot.\r\n";
        put(GetStdHandle(STD_ERROR_HANDLE),help,(DWORD)lstrlenA(help)); ExitProcess(2);
    }
    report=exclusive(prefix,".txt");
    if (report==INVALID_HANDLE_VALUE) ExitProcess(2);
    line("schema","xwn-graphics-ladder-1"); line("rung",rung); line("backend",backend);
    line("display",display); line("visual","UNVERIFIED"); line("scope","user-mode-sample");
    zero(&os,sizeof(os)); os.dwOSVersionInfoSize=sizeof(os);
    if (GetVersionExA(&os)) {
        number("os.api.major",os.dwMajorVersion); number("os.api.minor",os.dwMinorVersion);
        number("os.api.build",os.dwBuildNumber); number("os.api.platform",os.dwPlatformId);
    } else goto done;
    pixels=!equal(rung,"01");
    if (pixels) {
        source_file=exclusive(prefix,"-source.bin"); dest_file=exclusive(prefix,"-dest.bin");
        if (source_file==INVALID_HANDLE_VALUE || dest_file==INVALID_HANDLE_VALUE) { code=2; goto done; }
    }
    hwnd=make_window(); if (!log_bool("window.create",hwnd!=NULL)) goto done;
    ok=equal(rung,"00") ? gdi() : directdraw(hwnd,backend,pixels);
    if (!ok) goto done;
    if (pixels) {
        bad=mismatches(); number("pixels.mismatches",bad);
        put(source_file,source_pixels,sizeof(source_pixels)); put(dest_file,dest_pixels,sizeof(dest_pixels));
        if (!FlushFileBuffers(source_file) || !FlushFileBuffers(dest_file)) io_failed=1;
        if (bad) { code=3; goto done; }
    }
    if (equal(display,"view") && pixels) view(hwnd);
    code=cancelled ? 5 : 0;
done:
    if (hwnd && IsWindow(hwnd) && !DestroyWindow(hwnd)) code=1;
    if (source_file!=INVALID_HANDLE_VALUE && !CloseHandle(source_file)) io_failed=1;
    if (dest_file!=INVALID_HANDLE_VALUE && !CloseHandle(dest_file)) io_failed=1;
    if (io_failed) code=4;
    number("exit",(DWORD)code);
    line("result",code==0 ? (pixels ? "PIXELS_OK" : "INVENTORY_OK") : "FAILED");
    line("end","complete");
    if (!CloseHandle(report)) io_failed=1;
    ExitProcess(io_failed ? 4 : (UINT)code);
}
