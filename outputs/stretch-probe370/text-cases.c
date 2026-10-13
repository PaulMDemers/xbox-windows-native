/* Real NT5 glyph/opaque/clip oracle. Included after the existing199 functions. */
static HWND Backdrop;
static LRESULT CALLBACK backdrop(HWND w,UINT message,WPARAM a,LPARAM b) {
    if(message==WM_PAINT) {
        PAINTSTRUCT ps;BeginPaint(w,&ps);FillRect(ps.hdc,&ps.rcPaint,(HBRUSH)GetStockObject(BLACK_BRUSH));EndPaint(w,&ps);return 0;
    }
    if(message==WM_ERASEBKGND)return 1;
    return DefWindowProcA(w,message,a,b);
}
static BOOL backdropcreate(void) {
    WNDCLASSA wc;HDC dc;int width,height;
    zero(&wc,sizeof(wc));wc.lpfnWndProc=backdrop;wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="XwnTextBackdrop204";
    if(!RegisterClassA(&wc))return FALSE;
    dc=GetDC(NULL);if(!dc)return FALSE;width=GetDeviceCaps(dc,HORZRES);height=GetDeviceCaps(dc,VERTRES);ReleaseDC(NULL,dc);
    Backdrop=CreateWindowExA(WS_EX_TOPMOST,wc.lpszClassName,"XWN owned neutral backdrop",WS_POPUP|WS_VISIBLE,0,0,width,height,NULL,NULL,wc.hInstance,NULL);
    if(!Backdrop)return FALSE;UpdateWindow(Backdrop);return TRUE;
}
/* No file/log/API text between these two packet reads. */
static BOOL textsnapshot(DWORD *d) {
    zero(d,160);return ExtEscape(Screen,0x58574437,0,NULL,160,(LPSTR)d)==1;
}
static BOOL textinside(DWORD stage,int x,int y) {
    if(stage==10)return x>=10&&x<133&&y>=12&&y<73;
    if(stage==11)return (x>=5&&x<85&&y>=5&&y<70)||(x>=140&&x<245&&y>=18&&y<117);
    return TRUE;
}
static BOOL textdraw(HDC dc,DWORD stage) {
    RECT opaque={2,2,235,110};int x=18,y=28;
    if(stage==8){x=-12;y=-5;}
    if(stage==9){x=235;y=112;}
    if(stage==7){x=80;y=95;}
    if(stage==10){x=5;y=5;}
    if(stage==11){x=5;y=25;}
    if(stage==2||stage==3||stage==11)return ExtTextOutA(dc,x,y,ETO_OPAQUE,&opaque,stage==3?"":"Bounds Wjgy",stage==3?0:11,NULL);
    if(stage==12)return ExtTextOutW(dc,x,y,0,NULL,L"\x00c5g\x00e9\x03a9",4,NULL);
    return TextOutA(dc,x,y,"Bounds Wjgy",11);
}
static BOOL textcase(DWORD stage) {
    HDC ref=NULL;HBITMAP bm=NULL;HGDIOBJ old=NULL,font=NULL,oldscreen=NULL;DWORD *expected=NULL;
    BITMAPINFO bi;TEXTMETRICA tm;RECT client,whole={0,0,W,H};POINT origin={0,0};
    HRGN clip=NULL,second=NULL;HBRUSH brush=NULL;DWORD before[40],after[40],coherence[32],i,expectedbytes=0,delta=0;
    DWORD changed=0,guard=0;int x,y,a;BOOL madefont=FALSE,ok=FALSE,drawok=FALSE,packetok=FALSE;
    int previousmode=0;COLORREF previouscolor=CLR_INVALID,previousbk=CLR_INVALID;
    if(!uncover(300+stage)||!GetClientRect(Window,&client)||!ClientToScreen(Window,&origin))goto done;
    if(client.left||client.top||client.right>1024||client.bottom>1024||client.right<W||client.bottom<H)goto done;
    zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);bi.bmiHeader.biWidth=W;bi.bmiHeader.biHeight=-H;
    bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;
    ref=CreateCompatibleDC(Screen);bm=CreateDIBSection(Screen,&bi,DIB_RGB_COLORS,(void**)&expected,NULL,0);
    if(!ref||!bm)goto done;old=SelectObject(ref,bm);if(!old||old==HGDI_ERROR)goto done;
    font=GetStockObject(SYSTEM_FONT);
    if(stage>=4&&stage<=7) {
        font=CreateFontA(-22,0,stage==7?900:0,stage==7?900:0,FW_NORMAL,stage==4,stage==5,stage==6,ANSI_CHARSET,
                        OUT_DEFAULT_PRECIS,CLIP_DEFAULT_PRECIS,NONANTIALIASED_QUALITY,DEFAULT_PITCH|FF_SWISS,"Arial");madefont=TRUE;
    }
    if(!font)goto done;oldscreen=SelectObject(Screen,font);
    if(!oldscreen||oldscreen==HGDI_ERROR||!SelectObject(ref,font))goto done;
    previousmode=SetBkMode(Screen,stage==1?OPAQUE:TRANSPARENT);previouscolor=SetTextColor(Screen,RGB(23,189,62));previousbk=SetBkColor(Screen,RGB(178,25,90));
    if(!previousmode||previouscolor==CLR_INVALID||previousbk==CLR_INVALID||!SetBkMode(ref,stage==1?OPAQUE:TRANSPARENT)||
       SetTextColor(ref,RGB(23,189,62))==CLR_INVALID||SetBkColor(ref,RGB(178,25,90))==CLR_INVALID)goto done;
    zero(&tm,sizeof(tm));if(!GetTextMetricsA(Screen,&tm))goto done;
    record("TEXT_FONT_case_italic_underline",stage,tm.tmItalic,tm.tmUnderlined);
    record("TEXT_FONT_case_strike_height",stage,tm.tmStruckOut,(DWORD)tm.tmHeight);
    if((stage==4&&!tm.tmItalic)||(stage==5&&!tm.tmUnderlined)||(stage==6&&!tm.tmStruckOut))goto done;
    brush=CreateSolidBrush(RGB(0x42,0x65,0x8b));
    if(!brush||!FillRect(Screen,&client,brush)||!FillRect(ref,&whole,brush)||!GdiFlush())goto done;
    if(stage==10)clip=CreateRectRgn(10,12,133,73);
    if(stage==11) {
        clip=CreateRectRgn(5,5,85,70);second=CreateRectRgn(140,18,245,117);
        if(!clip||!second||CombineRgn(clip,clip,second,RGN_OR)!=COMPLEXREGION)goto done;
    }
    if((stage==10||stage==11)&&(!clip||SelectClipRgn(Screen,clip)==ERROR||SelectClipRgn(ref,clip)==ERROR))goto done;
    if(!textdraw(ref,stage)||!GdiFlush())goto done;
    record("TEXT_CLIENT_case_width_height",stage,(DWORD)client.right,(DWORD)client.bottom);
    record("TEXT_ORIGIN_case_x_y",stage,(DWORD)origin.x,(DWORD)origin.y);
    if(!textsnapshot(before))goto done;
    drawok=textdraw(Screen,stage);if(!GdiFlush())drawok=FALSE;
    packetok=textsnapshot(after);
    /* Logging begins only after paired device snapshots. */
    record("TEXT_DRAW_case_result_packets",stage,drawok,packetok);
    for(i=0;i<40;i++)record("TEXT_BEFORE_case_index_value",stage,i,before[i]);
    for(i=0;i<40;i++)record("TEXT_AFTER_case_index_value",stage,i,after[i]);
    if(!drawok||!packetok||before[0]!=0x54585758||after[0]!=0x54585758||before[1]!=118||after[1]!=118||
       before[2]!=160||after[2]!=160||before[3]>1||before[3]!=after[3]||before[11]||after[11]||after[29]||after[30]||after[31]||after[38]||after[39]||after[37]>1)goto done;
    delta=after[4]-before[4];
    /* GDI can implement an empty opaque call through BitBlt instead of TextOut. */
    if(delta!=1&&!(stage==3&&delta==0))goto done;
    if(delta==1) {
        if(after[20]>1||after[21]!=after[3]||after[10]!=before[10]||after[28])goto done;
        if(after[9]-before[9]!=after[27]||after[8]-before[8]!=after[26])goto done;
        for(y=0;y<client.bottom;y++)for(x=0;x<client.right;x++) {
            BOOL inside=textinside(stage,x,y);
            if(after[37])inside=inside&&x+origin.x>=(LONG)after[32]&&x+origin.x<(LONG)after[34]&&y+origin.y>=(LONG)after[33]&&y+origin.y<(LONG)after[35];
            if(after[3])inside=inside&&x+origin.x>=(LONG)after[22]&&x+origin.x<(LONG)after[24]&&y+origin.y>=(LONG)after[23]&&y+origin.y<(LONG)after[25];
            if(inside)expectedbytes+=4;
        }
        if(after[3]&&after[20]==1)expectedbytes=0;
        if(after[27]!=expectedbytes)goto done;
    }
    if(SelectClipRgn(Screen,NULL)==ERROR)goto done;
    zero(coherence,sizeof(coherence));a=ExtEscape(Screen,0x58574432,0,NULL,128,(LPSTR)coherence);
    record("TEXT_SCANOUT_case_result_mismatches",stage,(DWORD)a,coherence[19]);
    if(a!=1||coherence[0]!=0x53525758||coherence[1]!=112||coherence[19]||coherence[20]!=1)goto done;
    if(!blit(300+stage,Check,0,0,Screen,0,0)||!visible())goto done;
    for(i=0;i<W*H;i++) {
        if((expected[i]&0xffffff)!=0x42658b)++changed;else ++guard;
        if((Pixels[i]&0xffffff)!=(expected[i]&0xffffff)) {
            record("MISMATCH_TEXT_case_x_y",stage,i%W,i/W);record("MISMATCH_TEXT_expected_actual",expected[i]&0xffffff,Pixels[i]&0xffffff,0);goto done;
        }
    }
    if(!changed||!guard)goto done;
    ok=TRUE;
done:
    SelectClipRgn(Screen,NULL);
    if(previousmode)SetBkMode(Screen,previousmode);
    if(previouscolor!=CLR_INVALID)SetTextColor(Screen,previouscolor);
    if(previousbk!=CLR_INVALID)SetBkColor(Screen,previousbk);
    if(oldscreen&&oldscreen!=HGDI_ERROR)SelectObject(Screen,oldscreen);
    if(ref&&old&&old!=HGDI_ERROR)SelectObject(ref,old);
    if(madefont&&font)DeleteObject(font);
    if(bm)DeleteObject(bm);if(ref)DeleteDC(ref);
    if(clip)DeleteObject(clip);if(second)DeleteObject(second);if(brush)DeleteObject(brush);
    record("TEXT_EXPECTED_case_bytes_delta",stage,expectedbytes,delta);
    record("TEXT_PIXELS_case_changed_guard",stage,changed,guard);
    record("TEXT_CASE_case_pass",stage,ok,0);return ok;
}
