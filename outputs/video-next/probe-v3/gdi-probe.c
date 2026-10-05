/* Bounded NT5 GDI baseline probe. No driver/mode changes or automatic reboot.
 * Output is CREATE_NEW: retain each run in a separate working directory.
 * Copyright 2026. SPDX-License-Identifier: MIT
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>

#define W 256
#define H 128
static HANDLE Log;
static HDC Screen, Source, Check;
static HWND Window;
static HBITMAP InputBitmap, CheckBitmap;
static HGDIOBJ OldInput, OldCheck;
static DWORD *Input, *Pixels;
static DWORD Failures;
static void zero(void *p,DWORD length) {
    volatile BYTE *b=(volatile BYTE*)p;
    while(length--)*b++=0;
}

static void record(const char *label, DWORD a, DWORD b, DWORD c) {
    char line[256]; DWORD length, written;
    length=(DWORD)wsprintfA(line,"%s %lu %lu %lu\r\n",label,a,b,c);
    if(!WriteFile(Log,line,length,&written,NULL)||written!=length||!FlushFileBuffers(Log))ExitProcess(3);
}
static BOOL messages(void) {
    MSG m;
    while(PeekMessageA(&m,NULL,0,0,PM_REMOVE)) {
        if(m.message==WM_QUIT)return FALSE;
        TranslateMessage(&m);DispatchMessageA(&m);
    }
    return IsWindow(Window) && !(GetAsyncKeyState(VK_ESCAPE)&0x8000);
}
static BOOL visible(void) {
    RECT r;int kind=GetClipBox(Screen,&r);
    return kind==SIMPLEREGION && r.left<=0 && r.top<=0 && r.right>=W+16 && r.bottom>=H+16;
}
static BOOL uncover(DWORD stage) {
    DWORD start=GetTickCount();
    do {
        if(!messages())return FALSE;
        if(!SetWindowPos(Window,HWND_TOPMOST,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_SHOWWINDOW)) {
            record("FAIL_TOPMOST",stage,GetLastError(),0);return FALSE;
        }
        Sleep(250);if(!messages())return FALSE;
        if(visible()){record("VISIBLE_stage",stage,1,0);return TRUE;}
    }while(GetTickCount()-start<10000);
    record("FAIL_OCCLUDED",stage,0,0);return FALSE;
}
static LRESULT CALLBACK windowproc(HWND window,UINT message,WPARAM w,LPARAM l) {
    if(message==WM_PAINT) {PAINTSTRUCT ps;BeginPaint(window,&ps);EndPaint(window,&ps);return 0;}
    if(message==WM_ERASEBKGND)return 1;
    if(message==WM_DESTROY){PostQuitMessage(0);return 0;}
    return DefWindowProcA(window,message,w,l);
}
static BOOL blit(DWORD stage,HDC dst,int x,int y,HDC src,int sx,int sy) {
    if(!BitBlt(dst,x,y,W,H,src,sx,sy,SRCCOPY)||!GdiFlush()) {
        record("FAIL_API_stage_error",stage,GetLastError(),0);return FALSE;
    }
    return TRUE;
}
static BOOL pixels(DWORD stage) {
    DWORD i;
    for(i=0;i<W*H;i++)if((Pixels[i]&0xffffff)!=(Input[i]&0xffffff)) {
        record("MISMATCH_stage_x_y",stage,i%W,i/W);
        record("MISMATCH_expected_actual",Input[i]&0xffffff,Pixels[i]&0xffffff,0);
        return FALSE;
    }
    return TRUE;
}
static BOOL copycheck(DWORD stage) {
    DWORD i;
    for(i=0;i<W*H;i++)Pixels[i]=0xdeadbeef;
    if(stage==0)return blit(stage,Check,0,0,Source,0,0)&&pixels(stage);
    if(!uncover(stage))return FALSE;
    if(stage==3) {
        if(!blit(stage,Screen,16,16,Source,0,0)||!blit(stage,Screen,0,0,Screen,16,16))return FALSE;
    } else {
        if(!blit(stage,Screen,0,0,Source,0,0))return FALSE;
        if(stage==2&&!blit(stage,Screen,16,16,Screen,0,0))return FALSE;
    }
    if(!blit(stage,Check,0,0,Screen,stage==2?16:0,stage==2?16:0))return FALSE;
    if(!visible()){record("FAIL_CLIP_CHANGED",stage,0,0);return FALSE;}
    return pixels(stage);
}
static void timed(DWORD kind) {
    DWORD start,elapsed,count=0; BOOL ok=TRUE;
    if(!uncover(kind+10)){++Failures;return;}
    if(!GdiFlush()) {++Failures;record("FAIL_PRE_FLUSH",kind,GetLastError(),0);return;}
    start=GetTickCount();
    do {
        switch(kind) {
        case 0:ok=PatBlt(Screen,0,0,W,H,(count&1)?BLACKNESS:WHITENESS);break;
        case 1:ok=BitBlt(Screen,0,0,W,H,Source,0,0,SRCCOPY);break;
        case 2:ok=BitBlt(Check,0,0,W,H,Screen,0,0,SRCCOPY);break;
        case 3:ok=BitBlt(Screen,16,16,W,H,Screen,0,0,SRCCOPY);break;
        default:ok=BitBlt(Screen,0,0,W,H,Screen,16,16,SRCCOPY);break;
        }
        if(!ok||!GdiFlush()) {++Failures;record("FAIL_GDI",kind,GetLastError(),count);break;}
        ++count;
        if(!messages()) {++Failures;record("CANCELLED",kind,count,0);break;}
        if(!visible()){++Failures;record("FAIL_TIMING_OCCLUDED",kind,count,0);break;}
        elapsed=GetTickCount()-start;
    }while(count<2000 && elapsed<1500);
    elapsed=GetTickCount()-start;
    record("TIMING_kind_count_ms",kind,count,elapsed);
}
void WINAPI mainCRTStartup(void) {
    BITMAPINFO bi;DEVMODEA mode;DWORD i,start;BOOL check;WNDCLASSA wc;RECT rect;int clip;
    const int caps[]={HORZRES,VERTRES,BITSPIXEL,PLANES,VREFRESH,HORZSIZE,VERTSIZE,RASTERCAPS,LOGPIXELSX,LOGPIXELSY};
    Log=CreateFileA("gdi-baseline.txt",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
    record("XWN_GDI_PROBE_VERSION",3,W,H);
    zero(&wc,sizeof(wc));wc.style=CS_OWNDC;wc.lpfnWndProc=windowproc;
    wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="XwnGdiProbeV3";
    if(!RegisterClassA(&wc)){record("FAIL_CLASS",GetLastError(),0,0);ExitProcess(1);}
    Window=CreateWindowExA(WS_EX_TOPMOST,wc.lpszClassName,"XWN video baseline v3 - Esc cancels",WS_OVERLAPPED|WS_CAPTION|WS_VISIBLE,
                           20,20,W+64,H+96,NULL,NULL,GetModuleHandleA(NULL),NULL);
    if(!Window){record("FAIL_WINDOW",GetLastError(),0,0);ExitProcess(1);}
    SetForegroundWindow(Window);UpdateWindow(Window);Screen=GetDC(Window);
    if(!Screen){record("FAIL_DC",GetLastError(),0,0);ExitProcess(1);}
    GdiSetBatchLimit(1);
    for(i=0;i<sizeof(caps)/sizeof(caps[0]);i++)record("CAP_index_value",(DWORD)caps[i],(DWORD)GetDeviceCaps(Screen,caps[i]),0);
    for(i=0;i<64;i++) {
        zero(&mode,sizeof(mode));mode.dmSize=sizeof(mode);
        if(!EnumDisplaySettingsA(NULL,i,&mode))break;
        record("MODE_index_width_height",i,mode.dmPelsWidth,mode.dmPelsHeight);
        record("MODE_bpp_hz_flags",mode.dmBitsPerPel,mode.dmDisplayFrequency,mode.dmDisplayFlags);
    }
    zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);
    bi.bmiHeader.biWidth=W;bi.bmiHeader.biHeight=-H;bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;
    Source=CreateCompatibleDC(Screen);Check=CreateCompatibleDC(Screen);
    InputBitmap=CreateDIBSection(Screen,&bi,DIB_RGB_COLORS,(void**)&Input,NULL,0);
    CheckBitmap=CreateDIBSection(Screen,&bi,DIB_RGB_COLORS,(void**)&Pixels,NULL,0);
    if(!Source||!Check||!InputBitmap||!CheckBitmap){record("FAIL_SURFACE",GetLastError(),0,0);ExitProcess(1);}
    OldInput=SelectObject(Source,InputBitmap);OldCheck=SelectObject(Check,CheckBitmap);
    if(!OldInput||!OldCheck||OldInput==HGDI_ERROR||OldCheck==HGDI_ERROR){record("FAIL_SELECT",GetLastError(),0,0);ExitProcess(1);}
    for(i=0;i<W*H;i++)Input[i]=((i%W)<<16)|((i/W)<<8)|((i*7)&255);
    start=GetTickCount();while(GetTickCount()-start<2000) {if(!messages()){++Failures;break;}Sleep(20);}
    zero(&rect,sizeof(rect));
    if(!GetClientRect(Window,&rect)||rect.right<W+16||rect.bottom<H+16) {
        record("FAIL_CLIENT",(DWORD)rect.right,(DWORD)rect.bottom,0);++Failures;
    }
    clip=GetClipBox(Screen,&rect);
    record("CLIP_type_width_height",(DWORD)clip,(DWORD)rect.right,(DWORD)rect.bottom);
    for(i=0;i<4&&!Failures;i++) {
        check=copycheck(i);record("COPY_stage_pass",i,check,0);if(!check)++Failures;
    }
    if(!Failures) {
        for(i=0;i<5 && messages();i++)timed(i);
        if(i<5)++Failures;
    }else record("TIMINGS_SKIPPED",Failures,0,0);
    SelectObject(Source,OldInput);SelectObject(Check,OldCheck);
    DeleteObject(InputBitmap);DeleteObject(CheckBitmap);DeleteDC(Source);DeleteDC(Check);
    ReleaseDC(Window,Screen);if(IsWindow(Window))DestroyWindow(Window);
    record(Failures?"FAIL":"PASS",Failures,0,0);CloseHandle(Log);ExitProcess(Failures?1:0);
}
