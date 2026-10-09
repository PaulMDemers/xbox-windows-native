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
/* Existing RAM0112 escapes. Full-screen comparison runs OUTSIDE the timer. */
static BOOL snapshot(DWORD kind,DWORD phase) {
    DWORD data[32],start,elapsed,i;int result;
    zero(data,sizeof(data));
    if(!GdiFlush()){record("FAIL_STATS_FLUSH",kind,phase,GetLastError());return FALSE;}
    start=GetTickCount();
    result=ExtEscape(Screen,0x58574432,0,NULL,sizeof(data),(LPSTR)data);
    elapsed=GetTickCount()-start;
    record("STATS_CALL_kind_phase_result",kind,phase,(DWORD)result);
    record("STATS_LATENCY_kind_phase_ms",kind,phase,elapsed);
    for(i=0;i<32;i++)record(phase?"STATS_AFTER_kind_index_value":"STATS_BEFORE_kind_index_value",kind,i,data[i]);
    if(result!=1||data[0]!=0x53525758||data[1]!=112||data[20]!=1) {
        record("FAIL_STATS_IDENTITY",kind,phase,0);return FALSE;
    }
    if(data[19]){record("FAIL_SCANOUT_MISMATCH",kind,phase,data[19]);return FALSE;}
    for(i=21;i<32;i++)if(data[i]){record("FAIL_STATS_RESERVED",kind,phase,i);return FALSE;}
    return TRUE;
}
static BOOL identity(void) {
    DWORD data[8],i;int result;
    zero(data,sizeof(data));result=ExtEscape(Screen,0x58574431,0,NULL,sizeof(data),(LPSTR)data);
    record("IDENTITY_RESULT",(DWORD)result,0,0);
    for(i=0;i<8;i++)record("IDENTITY_index_value",i,data[i],0);
    if(result!=1||data[0]!=0x44525758||data[1]!=112||data[2]!=(DWORD)GetDeviceCaps(Screen,HORZRES)||
       data[3]!=(DWORD)GetDeviceCaps(Screen,VERTRES)||data[4]!=data[2]*4||data[5]!=32||
       data[6]!=data[4]*data[3]||data[7]!=1) {
        record("FAIL_IDENTITY",(DWORD)result,0,0);return FALSE;
    }
    return TRUE;
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

static BOOL dibsnapshot(DWORD tag,DWORD phase,DWORD *data) {
    DWORD i;int result;zero(data,128);
    if(!GdiFlush())return FALSE;
    result=ExtEscape(Screen,0x58574435,0,NULL,128,(LPSTR)data);
    record("DIB_CALL_tag_phase_result",tag,phase,(DWORD)result);
    for(i=0;i<32;i++)record(phase?"DIB_AFTER_tag_index_value":"DIB_BEFORE_tag_index_value",tag,i,data[i]);
    if(result!=1||data[0]!=0x57525758||data[1]!=115||data[2]!=128||data[3]>1)return FALSE;
    for(i=11;i<32;i++)if(data[i])return FALSE;
    return TRUE;
}
static BOOL dibcase(DWORD stage) {
    BITMAPINFO bi;HDC dc;HBITMAP bm;HGDIOBJ old;void *bits;
    HRGN region,second;HBRUSH brush;RECT area={0,0,W,H};
    DWORD before[32],after[32],i,actual,wanted,source,rop;
    BOOL ok=TRUE,inside;int x,y,row;
    zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);
    bi.bmiHeader.biWidth=W;bi.bmiHeader.biHeight=(stage==1||stage==3)?H:-H;
    bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=stage==4?24:32;
    dc=CreateCompatibleDC(Screen);bm=CreateDIBSection(Screen,&bi,DIB_RGB_COLORS,&bits,NULL,0);
    if(!dc||!bm)return FALSE;
    old=SelectObject(dc,bm);if(!old||old==HGDI_ERROR)return FALSE;
    for(y=0;y<H;y++)for(x=0;x<W;x++) {
        source=Input[y*W+x];row=(stage==1||stage==3)?H-1-y:y;
        if(stage==4) {BYTE *at=(BYTE*)bits+(row*W+x)*3;at[0]=(BYTE)source;at[1]=(BYTE)(source>>8);at[2]=(BYTE)(source>>16);}
        else ((DWORD*)bits)[row*W+x]=source;
    }
    if(!uncover(stage+30))ok=FALSE;
    brush=CreateSolidBrush(RGB(0x42,0x65,0x8b));
    if(!brush||!FillRect(Screen,&area,brush)||!GdiFlush())ok=FALSE;
    if(brush)DeleteObject(brush);
    region=CreateRectRgn(30,20,217,107);second=NULL;
    if(stage==2||stage==3){second=CreateRectRgn(2,2,20,60);if(!second||CombineRgn(region,region,second,RGN_OR)==ERROR)ok=FALSE;}
    if(!region||SelectClipRgn(Screen,region)==ERROR)ok=FALSE;
    if(!dibsnapshot(stage+10,0,before))ok=FALSE;
    rop=stage==5?SRCINVERT:SRCCOPY;
    if(ok&&(!BitBlt(Screen,9,11,W-16,H-16,dc,3,5,rop)||!GdiFlush()))ok=FALSE;
    if(!dibsnapshot(stage+10,1,after))ok=FALSE;
    if(SelectClipRgn(Screen,NULL)==ERROR)ok=FALSE;
    if(!blit(stage+30,Check,0,0,Screen,0,0))ok=FALSE;
    for(i=0;i<W*H&&ok;i++) {
        x=i%W;y=i/W;wanted=0x42658b;
        inside=x>=9&&x<W-7&&y>=11&&y<H-5&&
            ((x>=30&&x<217&&y>=20&&y<107)||((stage==2||stage==3)&&x>=2&&x<20&&y>=2&&y<60));
        if(inside){wanted=Input[(y-11+5)*W+x-9+3]&0xffffff;if(stage==5)wanted^=0x42658b;}
        actual=Pixels[i]&0xffffff;
        if(actual!=wanted){record("MISMATCH_DIB_stage_x_y",stage,x,y);record("MISMATCH_DIB_expected_actual",wanted,actual,0);ok=FALSE;}
    }
    if(ok&&before[3]&&after[5]<=before[5]) {
        record("FAIL_ROW_COVERAGE",stage,before[5],after[5]);ok=FALSE;
    }
    record("DIB_CASE_stage_pass",stage,ok,0);
    if(region)DeleteObject(region);
    if(second)DeleteObject(second);
    SelectObject(dc,old);DeleteObject(bm);DeleteDC(dc);return ok;
}

static void timed(DWORD kind) {
    DWORD start,elapsed,count=0,before[32],after[32]; BOOL ok=TRUE;
    if(!uncover(kind+10)){++Failures;return;}
    if(!GdiFlush()) {++Failures;record("FAIL_PRE_FLUSH",kind,GetLastError(),0);return;}
    if(!snapshot(kind,0)){++Failures;return;}
    if(!dibsnapshot(kind,0,before)){++Failures;return;}
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
    }while(count<20000 && elapsed<1500);
    elapsed=GetTickCount()-start;
    record("TIMING_kind_count_ms",kind,count,elapsed);
    if(!dibsnapshot(kind,1,after))++Failures;
    if(kind==1&&before[3]&&after[5]-before[5]<count){record("FAIL_ROW_TIMED_COVERAGE",kind,count,after[5]-before[5]);++Failures;}
    if(!snapshot(kind,1))++Failures;
    if(kind<3) {
        DWORD i,wanted;BOOL exact=TRUE;
        if(kind<2&&!blit(kind+100,Check,0,0,Screen,0,0))exact=FALSE;
        for(i=0;i<W*H&&exact;i++) {
            wanted=kind==0?(((count-1)&1)?0:0xffffff):(Input[i]&0xffffff);
            if((Pixels[i]&0xffffff)!=wanted){record("MISMATCH_POST_kind_x_y",kind,i%W,i/W);record("MISMATCH_POST_expected_actual",wanted,Pixels[i]&0xffffff,0);exact=FALSE;}
        }
        record("POST_TIMING_kind_pass",kind,exact,0);if(!exact)++Failures;
    }
}
void WINAPI mainCRTStartup(void) {
    BITMAPINFO bi;DEVMODEA mode;DWORD i,start;BOOL check;WNDCLASSA wc;RECT rect;int clip;
    const int caps[]={HORZRES,VERTRES,BITSPIXEL,PLANES,VREFRESH,HORZSIZE,VERTSIZE,RASTERCAPS,LOGPIXELSX,LOGPIXELSY};
    Log=CreateFileA("gdi-baseline.txt",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
    record("XWN_GDI_PROBE_VERSION",8,W,H);
    zero(&wc,sizeof(wc));wc.style=CS_OWNDC;wc.lpfnWndProc=windowproc;
    wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="XwnGdiProbeV8";
    if(!RegisterClassA(&wc)){record("FAIL_CLASS",GetLastError(),0,0);ExitProcess(1);}
    Window=CreateWindowExA(WS_EX_TOPMOST,wc.lpszClassName,"XWN scalar row stores115 longer - Esc cancels",WS_OVERLAPPED|WS_CAPTION|WS_VISIBLE,
                           20,20,W+64,H+96,NULL,NULL,GetModuleHandleA(NULL),NULL);
    if(!Window){record("FAIL_WINDOW",GetLastError(),0,0);ExitProcess(1);}
    SetForegroundWindow(Window);UpdateWindow(Window);Screen=GetDC(Window);
    if(!Screen){record("FAIL_DC",GetLastError(),0,0);ExitProcess(1);}
    GdiSetBatchLimit(1);
    if(!identity())++Failures;
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
    for(i=0;i<6&&!Failures;i++)if(!dibcase(i))++Failures;
    if(!Failures) {
        for(i=0;i<5 && messages();i++)timed(i);
        if(i<5)++Failures;
    }else record("TIMINGS_SKIPPED",Failures,0,0);
    SelectObject(Source,OldInput);SelectObject(Check,OldCheck);
    DeleteObject(InputBitmap);DeleteObject(CheckBitmap);DeleteDC(Source);DeleteDC(Check);
    ReleaseDC(Window,Screen);if(IsWindow(Window))DestroyWindow(Window);
    record(Failures?"FAIL":"PASS",Failures,0,0);CloseHandle(Log);ExitProcess(Failures?1:0);
}
