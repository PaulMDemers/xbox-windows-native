/* SPDX-License-Identifier: MIT. Owned-PID input, bounded private GDI captures.
 * Successful submissions are observations of the harness, not game PASS. */
static HWND gamewindow;
static DWORD capturecount,gamewindowcount;
static int initialwidth,initialheight;
#include "title_signature.h"
static BOOL CALLBACK findgame(HWND w,LPARAM unused){
 DWORD pid=0;char c[80];(void)unused;GetWindowThreadProcessId(w,&pid);
 if(pid==gamepid&&IsWindowVisible(w)&&GetClassNameA(w,c,sizeof(c))&&lstrcmpA(c,"RollerCoaster Tycoon")==0){gamewindow=w;gamewindowcount++;}
 return TRUE;
}
static BOOL state(const char* tag){
 DWORD pid=0,foregroundpid=0;RECT r;POINT p={0,0},cursor;char c[80],fc[80],s[640];BOOL ok,rectread,pointread,cursorread;HWND foreground;
 {DWORD prior=welcome_closed;if(!welcome_clear())return FALSE;if(prior!=welcome_closed&&IsWindow(gamewindow)){number("foreground_after_welcome",SetForegroundWindow(gamewindow));Sleep(250);}}
 zero(&r,sizeof(r));zero(&cursor,sizeof(cursor));zero(c,sizeof(c));
 zero(fc,sizeof(fc));foreground=GetForegroundWindow();GetWindowThreadProcessId(foreground,&foregroundpid);GetClassNameA(foreground,fc,sizeof(fc));
 GetWindowThreadProcessId(gamewindow,&pid);
 GetClassNameA(gamewindow,c,sizeof(c));rectread=GetClientRect(gamewindow,&r);pointread=ClientToScreen(gamewindow,&p);cursorread=GetCursorPos(&cursor);
 ok=IsWindow(gamewindow)&&pid==gamepid&&IsWindowVisible(gamewindow)&&!IsIconic(gamewindow)&&foreground==gamewindow&&
    lstrcmpA(c,"RollerCoaster Tycoon")==0&&rectread&&pointread&&cursorread&&
    r.right==640&&r.bottom==480&&p.x>=0&&p.y>=0&&p.x+640<=GetSystemMetrics(SM_CXSCREEN)&&p.y+480<=GetSystemMetrics(SM_CYSCREEN);
 wsprintfA(s,"input_state=%s tick=%lu valid=%lu pid=%lu foreground=%lu foreground_pid=%lu foreground_class=%s rect_read=%lu origin_read=%lu cursor_read=%lu client=%ld,%ld,%ld,%ld cursor=%ld,%ld display=%d,%d\r\n",tag,GetTickCount(),(DWORD)ok,pid,(DWORD)(foreground==gamewindow),foregroundpid,fc,(DWORD)rectread,(DWORD)pointread,(DWORD)cursorread,p.x,p.y,r.right,r.bottom,cursor.x,cursor.y,GetSystemMetrics(SM_CXSCREEN),GetSystemMetrics(SM_CYSCREEN));
 bytes(logh,s,lstrlenA(s));if(!ok&&foreground!=gamewindow)blocker(foreground);return ok;
}
static BOOL exposed(int x,int y);
static BOOL reacquire(const char* tag){
 DWORD started=GetTickCount();
 do{gamewindow=0;gamewindowcount=0;EnumWindows(findgame,0);
  number("owned_window_count",gamewindowcount);
  if(gamewindowcount==1&&state(tag)){number("reacquired_hwnd",(DWORD)gamewindow);return TRUE;}
  Sleep(250);
 }while(GetTickCount()-started<10000);
 number("reacquire_timeout",1);return FALSE;
}
static void keyevent(INPUT* i,WORD vk,BOOL up){
 zero(i,sizeof(*i));i->type=INPUT_KEYBOARD;i->ki.wScan=(WORD)MapVirtualKeyA(vk,0);
 i->ki.dwFlags=KEYEVENTF_SCANCODE|(vk==VK_LEFT||vk==VK_RIGHT?KEYEVENTF_EXTENDEDKEY:0)|(up?KEYEVENTF_KEYUP:0);
}
static void releaseinputs(void){
 INPUT i[4];zero(i,sizeof(i));i[0].type=INPUT_MOUSE;i[0].mi.dwFlags=MOUSEEVENTF_LEFTUP|MOUSEEVENTF_RIGHTUP;
 keyevent(&i[1],VK_RIGHT,TRUE);
 keyevent(&i[2],VK_LEFT,TRUE);
 keyevent(&i[3],VK_ESCAPE,TRUE);
 number("release_submitted",SendInput(4,i,sizeof(INPUT)));
}
static BOOL exposed(int x,int y){
 POINT p={x,y};HWND hit;BOOL ok;
 if(!ClientToScreen(gamewindow,&p))return FALSE;
 hit=WindowFromPoint(p);ok=hit==gamewindow||IsChild(gamewindow,hit);
 if(!ok)number("target_occluded",1);
 return ok;
}
static BOOL point(int x,int y){POINT p={x,y};if(x<0||x>=640||y<0||y>=480||!state("point")||!exposed(x,y)||!ClientToScreen(gamewindow,&p))return FALSE;return SetCursorPos(p.x,p.y);}
static BOOL button(DWORD flag){INPUT i;zero(&i,sizeof(i));i.type=INPUT_MOUSE;i.mi.dwFlags=flag;return SendInput(1,&i,sizeof(i))==1;}
static BOOL click(int x,int y){BOOL down,up;if(!point(x,y))return FALSE;
 Sleep(150);if(!state("click")||!exposed(x,y))return FALSE;down=button(MOUSEEVENTF_LEFTDOWN);Sleep(120);up=button(MOUSEEVENTF_LEFTUP);Sleep(1500);return down&&up;}
#include "park_phase.h"
static BOOL gamecapture(const char* tag);
static BOOL capture(const char* tag){
 HDC screen=0,mem=0;HBITMAP bmp=0;HGDIOBJ prior=0;HANDLE file=INVALID_HANDLE_VALUE;BITMAPINFO info;BITMAPFILEHEADER header;void* bits=0;POINT p={0,0};BOOL ok=FALSE;char path[160],line[240];
 if(tag[0]=='f'&&tag[1]=='u'&&tag[2]=='l'&&tag[3]=='l')return gamecapture(tag);
 if(capturecount>=32||!state(tag)||!ClientToScreen(gamewindow,&p)||!exposed(5,5)||!exposed(635,5)||!exposed(5,475)||!exposed(635,475)||!exposed(320,240))return FALSE;
 zero(&info,sizeof(info));info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);info.bmiHeader.biWidth=640;info.bmiHeader.biHeight=-480;info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;info.bmiHeader.biCompression=BI_RGB;info.bmiHeader.biSizeImage=640*480*4;
 screen=GetDC(0);if(!screen)goto done;mem=CreateCompatibleDC(screen);if(!mem)goto done;
 bmp=CreateDIBSection(screen,&info,DIB_RGB_COLORS,&bits,0,0);if(!bmp||!bits)goto done;prior=SelectObject(mem,bmp);if(!prior||prior==HGDI_ERROR)goto done;
 if(!BitBlt(mem,0,0,640,480,screen,p.x,p.y,SRCCOPY)||!GdiFlush())goto done;
 wsprintfA(path,"C:\\xwn606\\%02lu-%s.bmp",capturecount,tag);
 file=CreateFileA(path,GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(file==INVALID_HANDLE_VALUE)goto done;
 zero(&header,sizeof(header));header.bfType=0x4d42;header.bfOffBits=sizeof(header)+sizeof(BITMAPINFOHEADER);header.bfSize=header.bfOffBits+info.bmiHeader.biSizeImage;
 ok=bytes(file,&header,sizeof(header))&&bytes(file,&info.bmiHeader,sizeof(BITMAPINFOHEADER))&&bytes(file,bits,info.bmiHeader.biSizeImage);
 if(ok&&(lstrcmpA(tag,"park-loaded")==0||lstrcmpA(tag,"park-loaded-stable")==0)){ok=parkhash606((const BYTE*)bits);number("park_reference_match",ok);if(ok)park_verified=TRUE;}
done:
 if(file!=INVALID_HANDLE_VALUE)CloseHandle(file);
 if(prior&&prior!=HGDI_ERROR)SelectObject(mem,prior);
 if(bmp)DeleteObject(bmp);
 if(mem)DeleteDC(mem);
 if(screen)ReleaseDC(0,screen);
 wsprintfA(line,"capture=%s index=%lu success=%lu error=%lu\r\n",tag,capturecount,(DWORD)ok,GetLastError());bytes(logh,line,lstrlenA(line));capturecount++;return ok;
}
#include "game_capture.h"
static BOOL options(void){return click(44,14)&&click(76,100);}
static BOOL titlematch(void){
 HDC dc;POINT origin={0,0};DWORD n,x,y,h;COLORREF c;BOOL ok=TRUE;
 if(!state("title_poll")||!ClientToScreen(gamewindow,&origin))return FALSE;
 dc=GetDC(0);if(!dc)return FALSE;
 for(n=0;n<2;n++){
  h=2166136261UL;
  if(!exposed(title_signatures[n][0],title_signatures[n][1])){ok=FALSE;break;}
  for(y=0;y<16;y++)for(x=0;x<16;x++){
   c=GetPixel(dc,origin.x+title_signatures[n][0]+x,origin.y+title_signatures[n][1]+y);
   if(c==CLR_INVALID)ok=FALSE;
   h=(h^(GetRValue(c)>>4))*16777619UL;
   h=(h^(GetGValue(c)>>4))*16777619UL;
   h=(h^(GetBValue(c)>>4))*16777619UL;
  }
  number(n?"title_hash_b":"title_hash_a",h);if(h!=title_signatures[n][2])ok=FALSE;
 }
 ReleaseDC(0,dc);return ok;
}

#include "load_dialog002.h"
static BOOL runinputs(void){
 DWORD start=GetTickCount();BOOL requested=FALSE;
 do{
  gamewindow=0;gamewindowcount=0;EnumWindows(findgame,0);
  if(gamewindow){
   if(!requested){number("foreground_request",SetForegroundWindow(gamewindow));requested=TRUE;}
   if(gamewindowcount==1&&state("ready"))break;
  }
  Sleep(500);
 }while(GetTickCount()-start<60000);
 if(!gamewindow||!reacquire("start"))return FALSE;
 start=GetTickCount();
 while(!titlematch()){
  if(GetTickCount()-start>=90000){number("title_ready_timeout",1);capture("title-not-ready");return FALSE;}
  Sleep(2000);
 }
 number("title_ready",1);
 start=GetTickCount();
 while(!(state("title_exposure_wait")&&exposed(5,5)&&exposed(635,5)&&exposed(5,475)&&exposed(635,475)&&exposed(320,240))){if(GetTickCount()-start>=90000){number("title_exposure_timeout",1);return FALSE;}Sleep(1000);}

 if(!capture("title")||!click(197,415))return FALSE;
 Sleep(3000);
 if(!capture("scenarios")||!click(312,136))return FALSE;
 Sleep(10000);
 if(!capture("objective")||!click(427,157)||!click(15,15))return FALSE;
 if(!options()||!capture("window-options")||!click(292,39))return FALSE;
 if(!capture("park-before-move")||!point(5,5))return FALSE;
 {INPUT i;BOOL down,up;keyevent(&i,VK_RIGHT,FALSE);down=SendInput(1,&i,sizeof(i))==1;Sleep(2000);
 keyevent(&i,VK_RIGHT,TRUE);up=SendInput(1,&i,sizeof(i))==1;number("camera_right_submitted",down&&up);if(!down||!up)return FALSE;}
 Sleep(1000);
 if(!capture("camera-moved")||!click(44,14)||!capture("load-menu")||!click(76,40))return FALSE;
 if(!load_owned_park())return FALSE;
 if(!point(5,5)||!capture("park-loaded"))return FALSE;
 if(!parkphase606())return FALSE;
 Sleep(10000);
 return capture("park-loaded-stable");
}
