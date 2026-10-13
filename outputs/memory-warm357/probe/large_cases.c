/* New327 large-area probe only. Driver, framebuffer mapping and clocks unchanged. */
#include "large_oracle.h"
static BOOL lg_visible(DWORD cw,DWORD ch) {
    RECT clip,client;POINT origin={0,0};
    return GetClientRect(Window,&client)&&client.left==0&&client.top==0&&
           client.right==(LONG)cw&&client.bottom==(LONG)ch&&
           ClientToScreen(Window,&origin)&&origin.x>=0&&origin.y>=0&&
           origin.x+(LONG)cw<=GetDeviceCaps(Screen,HORZRES)&&
           origin.y+(LONG)ch<=GetDeviceCaps(Screen,VERTRES)&&
           GetClipBox(Screen,&clip)==SIMPLEREGION&&clip.left==0&&clip.top==0&&
           clip.right==(LONG)cw&&clip.bottom==(LONG)ch;
}
static BOOL lg_stats(DWORD id,DWORD phase,DWORD data[32]) {
    DWORD i;int rc;
    zero(data,128);
    if(!GdiFlush())return FALSE;
    rc=ExtEscape(Screen,0x58574432,0,NULL,128,(LPSTR)data);
    record("LARGE_STATS_CALL",id,phase,(DWORD)rc);
    for(i=0;i<32;i++)record(phase?"LARGE_STATS_AFTER":"LARGE_STATS_BEFORE",id,i,data[i]);
    if(rc!=1||data[0]!=0x53525758||data[1]!=112||data[19]||data[20]!=1)return FALSE;
    for(i=21;i<32;i++)if(data[i])return FALSE;
    return TRUE;
}
/* Capture without log I/O. Both packets publish only after the timed loop. */
static BOOL lg_phase(DWORD data[32]) {
    DWORD i;int rc;
    zero(data,128);rc=ExtEscape(Screen,0x58574433,0,NULL,128,(LPSTR)data);
    if(rc!=1||data[0]!=0x544d5758||data[1]!=113||data[2]!=128||data[3]>1||
       (!data[4]&&!data[5])||data[5]>=0x80000000||data[6]!=128||data[11]||data[12]||data[13])return FALSE;
    for(i=27;i<32;i++)if(data[i])return FALSE;
    return TRUE;
}
static void lg_phase_emit(DWORD id,DWORD phase,const DWORD data[32]) {
    DWORD i;record("PHASE344_PACKET",id,phase,1);
    for(i=0;i<32;i++)record(phase?"PHASE344_AFTER":"PHASE344_BEFORE",id,i,data[i]);
}
/* New348 coverage packets are outside the timed interval. */
static BOOL pc_capture(DWORD data[32]) {
 DWORD i;zero(data,128);
 if(ExtEscape(Screen,0x58574439,0,NULL,128,(LPSTR)data)!=1 ||
    data[0]!=0x50435758 || data[1]!=351 || data[2]!=128 || data[3]>1 || data[11])return FALSE;
 for(i=15;i<32;i++)if(data[i])return FALSE;
 return TRUE;
}
static void pc_emit(DWORD id,DWORD phase,const DWORD data[32]) {
 DWORD i;record("PRIMARY351_PACKET",id,phase,1);
 for(i=0;i<32;i++)record(phase?"PRIMARY351_AFTER":"PRIMARY351_BEFORE",id,i,data[i]);
}
static BOOL lg_pixels(DWORD id,DWORD kind,DWORD count,DWORD cw,DWORD ch,DWORD *source,DWORD *actual) {
    DWORD x,y,wanted,i;BOOL ok=TRUE;
    for(y=0;y<ch&&ok;y++)for(x=0;x<cw;x++) {
        i=y*cw+x;wanted=lg_expected(kind,count,LargeW,LargeH,x,y);
        if(source[i]!=lg_pixel(x,y)) {
            record("MISMATCH_LARGE_SOURCE",id,x,y);ok=FALSE;break;
        }
        if((actual[i]&0xffffff)!=wanted) {
            record("MISMATCH_LARGE_PIXEL",id,x,y);
            record("MISMATCH_LARGE_VALUES",id,wanted,actual[i]&0xffffff);ok=FALSE;break;
        }
    }
    record("LARGE_PIXEL_CHECK",id,cw*ch,ok);return ok;
}
static BOOL lg_operation(DWORD kind,DWORD count) {
    RECT area={16,16,16+(LONG)LargeW,16+(LONG)LargeH};
    switch(kind) {
    case 0:return PatBlt(Screen,16,16,LargeW,LargeH,(count&1)?BLACKNESS:WHITENESS);
    case 1:return BitBlt(Screen,16,16,LargeW,LargeH,LargeSource,16,16,SRCCOPY);
    case 2:return BitBlt(Screen,32,32,LargeW,LargeH,Screen,16,16,SRCCOPY);
    case 3:return BitBlt(Screen,16,16,LargeW,LargeH,Screen,32,32,SRCCOPY);
    case 4:return InvalidateRect(Window,&area,FALSE)&&UpdateWindow(Window)&&!LargePaintFailed;
    default:return FALSE;
    }
}
static BOOL lg_size(DWORD size,DWORD w,DWORD h) {
    uint32_t cw,ch,bytes;DWORD x,y,kind,id,count,start,elapsed,before[32],after[32];
    DWORD phases[2][32],primary[2][32];DWORD *source=NULL,*actual=NULL;RECT outer={0,0,0,0};BITMAPINFO bi;
    HDC readback=NULL;HBITMAP input=NULL,output=NULL;HGDIOBJ oldin=NULL,oldout=NULL;
    BOOL ok=FALSE;ULONGLONG b,a,minimum;
    if(!lg_layout(w,h,&cw,&ch,&bytes))return FALSE;
    LargeW=w;LargeH=h;
    outer.right=(LONG)cw;outer.bottom=(LONG)ch;
    if(!AdjustWindowRect(&outer,WS_OVERLAPPED|WS_CAPTION,FALSE))goto done;
    if(outer.right-outer.left+20>GetDeviceCaps(Screen,HORZRES)||
       outer.bottom-outer.top+20>GetDeviceCaps(Screen,VERTRES))goto done;
    if(!SetWindowPos(Window,HWND_TOPMOST,20,20,outer.right-outer.left,outer.bottom-outer.top,SWP_SHOWWINDOW))goto done;
    Sleep(250);if(!messages()||!lg_visible(cw,ch))goto done;
    zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);
    bi.bmiHeader.biWidth=cw;bi.bmiHeader.biHeight=-(LONG)ch;
    bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;
    LargeSource=CreateCompatibleDC(Screen);readback=CreateCompatibleDC(Screen);
    input=CreateDIBSection(Screen,&bi,DIB_RGB_COLORS,(void**)&source,NULL,0);
    output=CreateDIBSection(Screen,&bi,DIB_RGB_COLORS,(void**)&actual,NULL,0);
    if(!LargeSource||!readback||!input||!output)goto done;
    oldin=SelectObject(LargeSource,input);oldout=SelectObject(readback,output);
    if(!oldin||oldin==HGDI_ERROR||!oldout||oldout==HGDI_ERROR)goto done;
    for(y=0;y<ch;y++)for(x=0;x<cw;x++)source[y*cw+x]=lg_pixel(x,y);
    record("LARGE_SIZE",size,w,h);record("LARGE_LAYOUT",size,cw*4,bytes);
    record("LARGE_CLIENT",size,cw,ch);
    for(kind=0;kind<5;kind++) {
        id=size*5+kind;
        if(!messages()||!lg_visible(cw,ch)||
           !BitBlt(Screen,0,0,cw,ch,LargeSource,0,0,SRCCOPY)||!GdiFlush())goto done;
        /* Full source/guard oracle BEFORE timing. */
        if(!BitBlt(readback,0,0,cw,ch,Screen,0,0,SRCCOPY)||!GdiFlush()||
           !lg_pixels(id,kind,0,cw,ch,source,actual))goto done;
        if(!lg_stats(id,0,before)||!lg_phase(phases[0])||!pc_capture(primary[0]))goto done;
        LargePaintFailed=FALSE;LargePaintCount=0;LargePaint=(kind==4);
        count=0;start=GetTickCount();
        do {
            if(!lg_operation(kind,count)||!GdiFlush()||!messages()||!lg_visible(cw,ch))goto done;
            ++count;elapsed=GetTickCount()-start;
        }while(count<20000&&elapsed<750);
        elapsed=GetTickCount()-start;LargePaint=FALSE;
        if(!lg_phase(phases[1])||!pc_capture(primary[1]))goto done;
        lg_phase_emit(id,0,phases[0]);lg_phase_emit(id,1,phases[1]);
        pc_emit(id,0,primary[0]);pc_emit(id,1,primary[1]);
        record("LARGE_TIMING",id,count,elapsed);
        record("LARGE_PAINTS",id,LargePaintCount,LargePaintFailed);
        if(!count||elapsed<750||elapsed>30000||LargePaintFailed||
           (kind==4&&LargePaintCount!=count)||(kind!=4&&LargePaintCount))goto done;
        if(!lg_stats(id,1,after))goto done;
        b=(ULONGLONG)before[17]|((ULONGLONG)before[18]<<32);
        a=(ULONGLONG)after[17]|((ULONGLONG)after[18]<<32);
        minimum=(ULONGLONG)w*h*4*count;
        if(after[16]<before[16]||after[16]-before[16]<count||a<b||a-b<minimum)goto done;
        record("LARGE_UPLOADS",id,after[16]-before[16],0);
        record("LARGE_BYTES",id,(DWORD)(a-b),(DWORD)((a-b)>>32));
        if(!BitBlt(readback,0,0,cw,ch,Screen,0,0,SRCCOPY)||!GdiFlush()||
           !lg_visible(cw,ch)||!lg_pixels(id,kind,count,cw,ch,source,actual))goto done;
        record("LARGE_CASE_PASS",id,1,0);
    }
    ok=TRUE;
done:
    LargePaint=FALSE;
    if(LargeSource&&oldin&&oldin!=HGDI_ERROR)SelectObject(LargeSource,oldin);
    if(readback&&oldout&&oldout!=HGDI_ERROR)SelectObject(readback,oldout);
    if(input)DeleteObject(input);if(output)DeleteObject(output);
    if(LargeSource)DeleteDC(LargeSource);if(readback)DeleteDC(readback);LargeSource=NULL;
    if(!ok)record("FAIL_LARGE_SIZE",size,GetLastError(),0);
    return ok;
}
static BOOL large_cases(void) {
    DWORD i;const DWORD sizes[3][2]={{256,128},{640,360},{960,540}};
    record("PHASE344_VERSION",344,15,2);
    record("LARGE_VERSION",327,3,5);
    for(i=0;i<3;i++)if(!lg_size(i,sizes[i][0],sizes[i][1]))return FALSE;
    record("LARGE_COMPLETE",3,15,0);
    record("PHASE344_COMPLETE",15,30,0);return TRUE;
}
