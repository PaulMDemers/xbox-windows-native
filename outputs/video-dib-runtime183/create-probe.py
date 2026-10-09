"""V6 exact DIB orientation/clip/format/ROP cases and114 coverage, v4 timing."""
import shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'device-settled-reboot181';assert not (k/'gdi-probe.c').exists()
s=(old/'gdi-probe.c').read_text().replace('XWN_GDI_PROBE_VERSION",4','XWN_GDI_PROBE_VERSION",6').replace('XwnGdiProbeV4','XwnGdiProbeV6').replace('XWN existing driver counters v4 - Esc cancels','XWN bounded DIB copy114 - Esc cancels')
extra='''
static BOOL dibsnapshot(DWORD tag,DWORD phase,DWORD *data) {
    DWORD i;int result;zero(data,128);
    if(!GdiFlush())return FALSE;
    result=ExtEscape(Screen,0x58574434,0,NULL,128,(LPSTR)data);
    record("DIB_CALL_tag_phase_result",tag,phase,(DWORD)result);
    for(i=0;i<32;i++)record(phase?"DIB_AFTER_tag_index_value":"DIB_BEFORE_tag_index_value",tag,i,data[i]);
    if(result!=1||data[0]!=0x42445758||data[1]!=114||data[2]!=128||data[3]>1)return FALSE;
    for(i=14;i<32;i++)if(data[i])return FALSE;
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
    if(ok&&before[3]&&(stage==0||stage==1)&&after[5]<=before[5]) {
        record("FAIL_DIB_FAST_COVERAGE",stage,before[5],after[5]);ok=FALSE;
    }
    record("DIB_CASE_stage_pass",stage,ok,0);
    if(region)DeleteObject(region);
    if(second)DeleteObject(second);
    SelectObject(dc,old);DeleteObject(bm);DeleteDC(dc);return ok;
}
'''
marker='static void timed(DWORD kind) {';assert s.count(marker)==1;s=s.replace(marker,extra+'\n'+marker)
s=s.replace('DWORD start,elapsed,count=0; BOOL ok=TRUE;','DWORD start,elapsed,count=0,before[32],after[32]; BOOL ok=TRUE;')
s=s.replace('    start=GetTickCount();\n    do {','    if(!dibsnapshot(kind,0,before)){++Failures;return;}\n    start=GetTickCount();\n    do {')
s=s.replace('    if(!snapshot(kind,1))++Failures;','''    if(!dibsnapshot(kind,1,after))++Failures;
    if(kind==1&&before[3]&&after[5]-before[5]<count){record("FAIL_DIB_TIMED_COVERAGE",kind,count,after[5]-before[5]);++Failures;}
    if(!snapshot(kind,1))++Failures;''')
s=s.replace('    if(!Failures) {\n        for(i=0;i<5','    for(i=0;i<6&&!Failures;i++)if(!dibcase(i))++Failures;\n    if(!Failures) {\n        for(i=0;i<5')
(k/'gdi-probe.c').write_bytes(s.encode())
for n in ['runner.c','restart_gate.h','test-gate.c']:shutil.copyfile(old/n,k/n)
(k/'artifacts').mkdir(exist_ok=False);shutil.copyfile(old/'artifacts/runner.exe',k/'artifacts/runner.exe')
print('New v6 cases generated; unchanged compiled restart guard; not launched')
