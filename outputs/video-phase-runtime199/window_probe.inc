/* Real owned-window move/WM_PAINT/TextOut lifecycle, not simulated desktop FPS. */
static BOOL windowpacket(DWORD phase,DWORD escape,const char *label) {
    DWORD d[32],i;int answer;
    zero(d,sizeof(d));if(!GdiFlush())return FALSE;
    answer=ExtEscape(Screen,escape,0,NULL,sizeof(d),(LPSTR)d);
    record(escape==0x58574432?"WINDOW_STATS_CALL":"WINDOW_PROFILE_CALL",phase,(DWORD)answer,0);
    for(i=0;i<32;i++)record(label,phase,i,d[i]);
    if(answer!=1)return FALSE;
    if(escape==0x58574432)return d[0]==0x53525758&&d[1]==112&&d[19]==0&&d[20]==1;
    return d[0]==0x544d5758&&d[1]==113&&d[2]==128&&d[3]<=1&&
           (d[4]||d[5])&&d[5]<0x80000000&&d[6]==128&&!d[11]&&!d[12];
}
static BOOL windowcase(void) {
    BITMAPINFO bi;HDC ref=NULL;HBITMAP bm=NULL;HGDIOBJ old=NULL,font=NULL,oldfont=NULL;
    DWORD *expected=NULL,i,j,start,elapsed,previous;BOOL ok=FALSE;
    int oldmode;COLORREF oldcolor;
    zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);
    bi.bmiHeader.biWidth=W;bi.bmiHeader.biHeight=-H;bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;
    ref=CreateCompatibleDC(Screen);bm=CreateDIBSection(Screen,&bi,DIB_RGB_COLORS,(void**)&expected,NULL,0);
    if(!ref||!bm)goto done;
    old=SelectObject(ref,bm);if(!old||old==HGDI_ERROR)goto done;
    font=GetStockObject(SYSTEM_FONT);oldfont=SelectObject(Screen,font);
    if(!font||!oldfont||oldfont==HGDI_ERROR)goto done;
    SelectObject(ref,font);oldmode=SetBkMode(Screen,TRANSPARENT);oldcolor=SetTextColor(Screen,RGB(23,189,62));
    if(!oldmode||oldcolor==CLR_INVALID)goto restore;
    if(!SetBkMode(ref,TRANSPARENT)||SetTextColor(ref,RGB(23,189,62))==CLR_INVALID)goto restore;
    if(!BitBlt(ref,0,0,W,H,Source,0,0,SRCCOPY)||!TextOutA(ref,5,5,"XWN phase window",16)||!GdiFlush())goto restore;
    if(!uncover(200))goto restore;
    if(!windowpacket(0,0x58574432,"WINDOW_STATS_index_value")||
       !windowpacket(0,0x58574433,"WINDOW_PROFILE_index_value"))goto restore;
    PaintPattern=TRUE;PaintFailed=FALSE;previous=PaintRounds;start=GetTickCount();
    for(i=0;i<40;i++) {
        if(!messages()||!SetWindowPos(Window,HWND_TOPMOST,40+(i&1)*32,40+(i&1)*16,0,0,SWP_NOSIZE|SWP_SHOWWINDOW)||
           !InvalidateRect(Window,NULL,FALSE)||!UpdateWindow(Window)||!GdiFlush()||!visible()||PaintFailed)break;
        if(!blit(200+i,Check,0,0,Screen,0,0))break;
        for(j=0;j<W*H;j++)if((Pixels[j]&0xffffff)!=(expected[j]&0xffffff))break;
        if(j!=W*H) {record("MISMATCH_WINDOW_round_index",i,j,0);break;}
    }
    elapsed=GetTickCount()-start;PaintPattern=FALSE;
    record("WINDOW_ROUNDS_paints_ms",i,PaintRounds-previous,elapsed);
    ok=i==40&&PaintRounds-previous>=40&&!PaintFailed;
    if(!windowpacket(1,0x58574432,"WINDOW_STATS_index_value")||
       !windowpacket(1,0x58574433,"WINDOW_PROFILE_index_value"))ok=FALSE;
restore:
    PaintPattern=FALSE;SetBkMode(Screen,oldmode);SetTextColor(Screen,oldcolor);
    if(oldfont&&oldfont!=HGDI_ERROR)SelectObject(Screen,oldfont);
done:
    if(ref&&old&&old!=HGDI_ERROR)SelectObject(ref,old);
    if(bm)DeleteObject(bm);
    if(ref)DeleteDC(ref);
    record("WINDOW_CASE_pass",ok,40,0);return ok;
}
