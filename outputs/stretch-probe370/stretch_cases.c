/* Actual stretch dispatch and full-window reference/guard checks.
 * Positive orientation has a separate geometric constant-color oracle.
 * Mirrored orientation uses GDI DIB reference, independent of this driver but
 * not an independent software rasterizer. No reference from screen pixels. */
static DWORD StretchExpected[W*H];
static BOOL stretch_stats(DWORD id,DWORD phase,DWORD data[32]) {
    DWORD i;int rc;
    zero(data,128);if(!GdiFlush())return FALSE;
    rc=ExtEscape(Screen,0x58574432,0,NULL,128,(LPSTR)data);
    if(rc!=1||data[0]!=0x53525758||data[1]!=112||data[19]||data[20]!=1)return FALSE;
    for(i=21;i<32;i++)if(data[i])return FALSE;
    for(i=0;i<32;i++)record(phase?"STRETCH_AFTER":"STRETCH_BEFORE",id,i,data[i]);
    return TRUE;
}
static BOOL stretch_cases(void) {
    RECT outer={0,0,W,H};DWORD id,i,x,y,orientation,clipkind,before[32],after[32],start,elapsed;
    HRGN region=NULL,a=NULL,b=NULL;BOOL ok=FALSE;int dx,dy,dw,dh;ULONGLONG ba,bb;
    record("STRETCH_VERSION",370,12,16);
    if(!AdjustWindowRect(&outer,WS_OVERLAPPED|WS_CAPTION,FALSE)||
       !SetWindowPos(Window,HWND_TOPMOST,20,20,outer.right-outer.left,outer.bottom-outer.top,SWP_SHOWWINDOW))goto done;
    Sleep(250);if(!messages()||!lg_visible(W,H))goto done;
    for(i=0;i<W*H;i++)Input[i]=0x00369123;
    if(!SetStretchBltMode(Screen,COLORONCOLOR)||!SetStretchBltMode(Check,COLORONCOLOR))goto done;
    for(id=0;id<12;id++) {
        orientation=id%4;clipkind=id/4;
        dx=(orientation&1)?96:32;dy=(orientation&2)?56:24;
        dw=(orientation&1)?-64:64;dh=(orientation&2)?-32:32;
        if(SelectClipRgn(Screen,NULL)==ERROR||SelectClipRgn(Check,NULL)==ERROR||
           !PatBlt(Screen,0,0,W,H,BLACKNESS)||!PatBlt(Check,0,0,W,H,BLACKNESS)||!GdiFlush())goto done;
        if(clipkind==1)region=CreateRectRgn(40,28,88,52);
        if(clipkind==2){a=CreateRectRgn(40,28,56,52);b=CreateRectRgn(72,28,88,52);region=CreateRectRgn(0,0,0,0);
            if(!a||!b||!region||CombineRgn(region,a,b,RGN_OR)==ERROR)goto done;}
        if(clipkind&&(!region||SelectClipRgn(Screen,region)==ERROR||SelectClipRgn(Check,region)==ERROR))goto done;
        if(!StretchBlt(Check,dx,dy,dw,dh,Source,0,0,16,8,SRCCOPY)||!GdiFlush())goto done;
        for(i=0;i<W*H;i++)StretchExpected[i]=Pixels[i]&0xffffff;
        if(!orientation)for(y=0;y<H;y++)for(x=0;x<W;x++){
            BOOL changed=x>=32&&x<96&&y>=24&&y<56;
            if(clipkind)changed=changed&&x>=40&&x<88&&y>=28&&y<52;
            if(clipkind==2)changed=changed&&(x<56||x>=72);
            if(StretchExpected[y*W+x]!=(changed?0x00369123:0)){
                record("FAIL_STRETCH_REFERENCE",id,x,y);goto done;}
        }
        if(!stretch_stats(id,0,before))goto done;
        start=GetTickCount();
        for(i=0;i<16;i++)if(!StretchBlt(Screen,dx,dy,dw,dh,Source,0,0,16,8,SRCCOPY)||!GdiFlush())goto done;
        elapsed=GetTickCount()-start;
        if(!stretch_stats(id,1,after))goto done;
        record("STRETCH_TIMING",id,16,elapsed);
        if(after[10]<before[10]||after[11]<before[11]||
           after[10]-before[10]+after[11]-before[11]<16){record("FAIL_STRETCH_COVERAGE",id,after[10]-before[10],after[11]-before[11]);goto done;}
        ba=(ULONGLONG)after[17]|((ULONGLONG)after[18]<<32);
        bb=(ULONGLONG)before[17]|((ULONGLONG)before[18]<<32);
        if(ba<bb||after[16]<before[16])goto done;
        record("STRETCH_BYTES",id,(DWORD)(ba-bb),(DWORD)((ba-bb)>>32));
        record("STRETCH_DISPATCH",id,after[10]-before[10],after[11]-before[11]);
        if(SelectClipRgn(Screen,NULL)==ERROR||SelectClipRgn(Check,NULL)==ERROR||
           !BitBlt(Check,0,0,W,H,Screen,0,0,SRCCOPY)||!GdiFlush()||!lg_visible(W,H))goto done;
        for(i=0;i<W*H;i++)if((Pixels[i]&0xffffff)!=StretchExpected[i]||Input[i]!=0x00369123){
            record("FAIL_STRETCH_PIXELS",id,i,Pixels[i]&0xffffff);goto done;}
        record("STRETCH_CASE_PASS",id,W*H,!orientation);
        if(region){DeleteObject(region);region=NULL;}if(a){DeleteObject(a);a=NULL;}if(b){DeleteObject(b);b=NULL;}
    }
    record("STRETCH_COMPLETE",12,192,0);ok=TRUE;
done:
    SelectClipRgn(Screen,NULL);SelectClipRgn(Check,NULL);
    if(region)DeleteObject(region);if(a)DeleteObject(a);if(b)DeleteObject(b);
    if(!ok)record("FAIL_STRETCH",GetLastError(),0,0);
    return ok;
}
