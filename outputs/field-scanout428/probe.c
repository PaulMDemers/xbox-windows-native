/* SPDX-License-Identifier: MIT
 * NT5 user-mode observation only. No driver, register, mode or setting writes.
 * Static checks compare independent pixels AND the installed driver's actual
 * mapped scanout against its shadow. That is not an atomic field/signal capture.
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include "pattern.h"
static HANDLE logFile;
static HWND window;
static HDC draw,source,readback;
static DWORD *input,*pixels,phase,failures;
static BOOL paintFailed;
static void clear(void *p,DWORD n){volatile BYTE *b=p;while(n--)*b++=0;}
static void record(const char *s,DWORD a,DWORD b,DWORD c){
 char line[256];DWORD n,w;
 n=wsprintfA(line,"%s %lu %lu %lu\r\n",s,a,b,c);
 if(!WriteFile(logFile,line,n,&w,NULL)||w!=n||!FlushFileBuffers(logFile))ExitProcess(9);
}
static BOOL paint(HDC dc){
 RECT r={0,FH,FW,FH+64};
 const char *label="428: one-line | two-line | binary row number | parity. Text: Windows 2000 MmWw 0123456789";
 if(!BitBlt(dc,0,0,FW,FH,source,0,0,SRCCOPY))return FALSE;
 if(!FillRect(dc,&r,(HBRUSH)GetStockObject(WHITE_BRUSH)))return FALSE;
 SetBkColor(dc,RGB(255,255,255));SetTextColor(dc,0);
 return TextOutA(dc,8,FH+12,label,lstrlenA(label));
}
static LRESULT CALLBACK proc(HWND h,UINT m,WPARAM w,LPARAM l){
 if(m==WM_PAINT){PAINTSTRUCT p;HDC d=BeginPaint(h,&p);if(source&&!paint(d))paintFailed=TRUE;EndPaint(h,&p);return 0;}
 if(m==WM_CLOSE){PostQuitMessage(1);return 0;}
 return DefWindowProcA(h,m,w,l);
}
static BOOL messages(void){MSG m;while(PeekMessageA(&m,NULL,0,0,PM_REMOVE)){if(m.message==WM_QUIT)return FALSE;TranslateMessage(&m);DispatchMessageA(&m);}return !paintFailed;}
static BOOL visible(void){RECT r;POINT p={0,0};return GetClientRect(window,&r)&&r.right==FW&&r.bottom==FH+64&&ClientToScreen(window,&p)&&p.x>=0&&p.y>=0&&p.x+FW<=(unsigned)GetSystemMetrics(SM_CXSCREEN)&&p.y+FH+64<=(unsigned)GetSystemMetrics(SM_CYSCREEN);}
static BOOL check(DWORD checkpoint){
 DWORD x,y,bad=0,d[32],i,w;int rc;char path[64];HANDLE f;
 if(!messages()||!visible()||!GdiFlush())return FALSE;
 clear(d,sizeof(d));rc=ExtEscape(draw,0x58574432,0,NULL,sizeof(d),(LPSTR)d);
 record("SCANOUT",checkpoint,rc,d[19]);
 for(i=0;i<32;i++)record("SCANOUT_WORD",checkpoint,i,d[i]);
 if(rc!=1||d[0]!=0x53525758||d[1]!=112||d[19]||d[20]!=1)return FALSE;
 for(i=21;i<32;i++)if(d[i])return FALSE;
 if(!BitBlt(readback,0,0,FW,FH,draw,0,0,SRCCOPY)||!GdiFlush())return FALSE;
 for(y=0;y<FH;y++)for(x=0;x<FW;x++)if((pixels[y*FW+x]&0xffffff)!=field_pixel(x,y,phase)||input[y*FW+x]!=field_pixel(x,y,phase))++bad;
 record("PIXELS",checkpoint,FW*FH,bad);
 wsprintfA(path,"capture-%02lu.bgrx",checkpoint);f=CreateFileA(path,GENERIC_WRITE,0,NULL,CREATE_NEW,0,NULL);
 if(f==INVALID_HANDLE_VALUE)return FALSE;
 if(!WriteFile(f,pixels,FW*FH*4,&w,NULL)||w!=FW*FH*4||!FlushFileBuffers(f)){CloseHandle(f);return FALSE;}
 if(!CloseHandle(f))return FALSE;
 return !bad;
}
void WINAPI mainCRTStartup(void){
 WNDCLASSA wc;BITMAPINFO bi;HBITMAP a,b;HGDIOBJ olda,oldb;DWORD x,y,start,tick,step,sw,sh,id[8];
 logFile=CreateFileA("result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,0,NULL);
 if(logFile==INVALID_HANDLE_VALUE)ExitProcess(2);
 sw=GetSystemMetrics(SM_CXSCREEN);sh=GetSystemMetrics(SM_CYSCREEN);record("START428",sw,sh,GetTickCount());
 if(!((sw==1280&&sh==720)||(sw==1920&&sh==1080)))goto failed;
 clear(&wc,sizeof(wc));wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="Field428";
 if(!RegisterClassA(&wc))goto failed;
 window=CreateWindowExA(WS_EX_TOPMOST,"Field428","Field scanout 428",WS_POPUP,32,32,FW,FH+64,NULL,NULL,wc.hInstance,NULL);
 if(!window)goto failed;
 draw=GetDC(window);source=CreateCompatibleDC(draw);readback=CreateCompatibleDC(draw);
 clear(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);bi.bmiHeader.biWidth=FW;bi.bmiHeader.biHeight=-(LONG)FH;bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;
 a=CreateDIBSection(draw,&bi,DIB_RGB_COLORS,(void**)&input,NULL,0);b=CreateDIBSection(draw,&bi,DIB_RGB_COLORS,(void**)&pixels,NULL,0);
 if(!draw||!source||!readback||!a||!b)goto failed;
 olda=SelectObject(source,a);oldb=SelectObject(readback,b);if(!olda||olda==HGDI_ERROR||!oldb||oldb==HGDI_ERROR)goto failed;
 clear(id,sizeof(id));if(ExtEscape(draw,0x58574431,0,NULL,sizeof(id),(LPSTR)id)!=1)goto failed;
 for(x=0;x<8;x++)record("IDENTITY",x,id[x],0);
 if(id[0]!=0x44525758||id[1]!=112||id[2]!=sw||id[3]!=sh||id[4]!=sw*4||id[5]!=32||id[6]!=sw*sh*4||id[7]!=1)goto failed;
 ShowCursor(FALSE);ShowWindow(window,SW_SHOW);SetForegroundWindow(window);
 for(phase=0;phase<4;phase++){
  for(y=0;y<FH;y++)for(x=0;x<FW;x++)input[y*FW+x]=field_pixel(x,y,phase);
  if(!paint(draw)||!GdiFlush()||!check(phase*2))goto failed;
  record("PHASE",phase,GetTickCount(),phase==2?1:0);start=GetTickCount();step=0;
  do{
   if(!messages())goto failed;
   if(phase==2){
    /* Actual USER window movement, source pixels unchanged. */
    x=32+(step%80);y=32+((step*3)%64);
    if(!SetWindowPos(window,HWND_TOPMOST,x,y,0,0,SWP_NOSIZE|SWP_NOACTIVATE)||!GdiFlush())goto failed;
    ++step;
   }
   Sleep(40);tick=GetTickCount()-start;
  }while(tick<15000);
  if(!check(phase*2+1))goto failed;
  record("PHASE_DONE",phase,step,tick);
 }
 ShowCursor(TRUE);SelectObject(source,olda);SelectObject(readback,oldb);DeleteObject(a);DeleteObject(b);DeleteDC(source);source=NULL;DeleteDC(readback);ReleaseDC(window,draw);DestroyWindow(window);
 record("COMPLETE",4,8,0);CloseHandle(logFile);ExitProcess(0);
failed:
 failures++;record("FAILED",phase,failures,GetLastError());CloseHandle(logFile);ExitProcess(1);
}
