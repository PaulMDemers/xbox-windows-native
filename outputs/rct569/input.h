/* SPDX-License-Identifier: MIT. Owned-PID input, bounded private GDI captures.
 * Successful submissions are observations of the harness, not game PASS. */
static HWND gamewindow;
static DWORD capturecount;
static DEVMODEA originalmode;
static BOOL displaychanged;
static BOOL CALLBACK findgame(HWND w,LPARAM unused){
 DWORD pid=0;char c[80];(void)unused;GetWindowThreadProcessId(w,&pid);
 if(pid==gamepid&&IsWindowVisible(w)&&GetClassNameA(w,c,sizeof(c))&&lstrcmpA(c,"RollerCoaster Tycoon")==0)gamewindow=w;
 return TRUE;
}
static BOOL state(const char* tag){
 DWORD pid=0;RECT r;POINT p={0,0},cursor;char c[80],s[512];BOOL ok;
 zero(&r,sizeof(r));zero(&cursor,sizeof(cursor));zero(c,sizeof(c));
 GetWindowThreadProcessId(gamewindow,&pid);
 ok=IsWindow(gamewindow)&&pid==gamepid&&IsWindowVisible(gamewindow)&&!IsIconic(gamewindow)&&GetForegroundWindow()==gamewindow&&
    GetClassNameA(gamewindow,c,sizeof(c))&&lstrcmpA(c,"RollerCoaster Tycoon")==0&&GetClientRect(gamewindow,&r)&&ClientToScreen(gamewindow,&p)&&GetCursorPos(&cursor)&&
    r.right==640&&r.bottom==480&&p.x>=0&&p.y>=0&&p.x+640<=GetSystemMetrics(SM_CXSCREEN)&&p.y+480<=GetSystemMetrics(SM_CYSCREEN);
 wsprintfA(s,"input_state=%s tick=%lu valid=%lu pid=%lu foreground=%lu client=%ld,%ld,%ld,%ld cursor=%ld,%ld display=%d,%d\r\n",tag,GetTickCount(),(DWORD)ok,pid,(DWORD)(GetForegroundWindow()==gamewindow),p.x,p.y,r.right,r.bottom,cursor.x,cursor.y,GetSystemMetrics(SM_CXSCREEN),GetSystemMetrics(SM_CYSCREEN));
 bytes(logh,s,lstrlenA(s));return ok;
}
static void releaseinputs(void){
 INPUT i[4];zero(i,sizeof(i));i[0].type=INPUT_MOUSE;i[0].mi.dwFlags=MOUSEEVENTF_LEFTUP|MOUSEEVENTF_RIGHTUP;
 i[1].type=INPUT_KEYBOARD;i[1].ki.wVk=VK_RIGHT;i[1].ki.dwFlags=KEYEVENTF_KEYUP;
 i[2].type=INPUT_KEYBOARD;i[2].ki.wVk=VK_LEFT;i[2].ki.dwFlags=KEYEVENTF_KEYUP;
 i[3].type=INPUT_KEYBOARD;i[3].ki.wVk=VK_ESCAPE;i[3].ki.dwFlags=KEYEVENTF_KEYUP;
 number("release_submitted",SendInput(4,i,sizeof(INPUT)));
}
static BOOL point(int x,int y){POINT p={x,y};if(x<0||x>=640||y<0||y>=480||!state("point")||!ClientToScreen(gamewindow,&p))return FALSE;return SetCursorPos(p.x,p.y);}
static BOOL button(DWORD flag){INPUT i;zero(&i,sizeof(i));i.type=INPUT_MOUSE;i.mi.dwFlags=flag;return SendInput(1,&i,sizeof(i))==1;}
static BOOL click(int x,int y){BOOL down,up;if(!point(x,y))return FALSE;
 Sleep(150);if(!state("click"))return FALSE;down=button(MOUSEEVENTF_LEFTDOWN);Sleep(120);up=button(MOUSEEVENTF_LEFTUP);Sleep(1500);return down&&up;}
static BOOL keyhold(WORD vk,DWORD ms){INPUT i;BOOL down,up;if(!state("key"))return FALSE;zero(&i,sizeof(i));i.type=INPUT_KEYBOARD;i.ki.wVk=vk;down=SendInput(1,&i,sizeof(i))==1;Sleep(ms);i.ki.dwFlags=KEYEVENTF_KEYUP;up=SendInput(1,&i,sizeof(i))==1;return down&&up&&state("key_end");}
static BOOL capture(const char* tag){
 HDC screen=0,mem=0;HBITMAP bmp=0;HGDIOBJ prior=0;HANDLE file=INVALID_HANDLE_VALUE;BITMAPINFO info;BITMAPFILEHEADER header;void* bits=0;POINT p={0,0};BOOL ok=FALSE;char path[160],line[240];
 if(capturecount>=32||!state(tag)||!ClientToScreen(gamewindow,&p))return FALSE;
 zero(&info,sizeof(info));info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);info.bmiHeader.biWidth=640;info.bmiHeader.biHeight=-480;info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;info.bmiHeader.biCompression=BI_RGB;info.bmiHeader.biSizeImage=640*480*4;
 screen=GetDC(0);if(!screen)goto done;mem=CreateCompatibleDC(screen);if(!mem)goto done;
 bmp=CreateDIBSection(screen,&info,DIB_RGB_COLORS,&bits,0,0);if(!bmp||!bits)goto done;prior=SelectObject(mem,bmp);if(!prior||prior==HGDI_ERROR)goto done;
 if(!BitBlt(mem,0,0,640,480,screen,p.x,p.y,SRCCOPY)||!GdiFlush())goto done;
 wsprintfA(path,"C:\\xwn569\\%02lu-%s.bmp",capturecount,tag);
 file=CreateFileA(path,GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(file==INVALID_HANDLE_VALUE)goto done;
 zero(&header,sizeof(header));header.bfType=0x4d42;header.bfOffBits=sizeof(header)+sizeof(BITMAPINFOHEADER);header.bfSize=header.bfOffBits+info.bmiHeader.biSizeImage;
 ok=bytes(file,&header,sizeof(header))&&bytes(file,&info.bmiHeader,sizeof(BITMAPINFOHEADER))&&bytes(file,bits,info.bmiHeader.biSizeImage);
done:
 if(file!=INVALID_HANDLE_VALUE)CloseHandle(file);
 if(prior&&prior!=HGDI_ERROR)SelectObject(mem,prior);
 if(bmp)DeleteObject(bmp);
 if(mem)DeleteDC(mem);
 if(screen)ReleaseDC(0,screen);
 wsprintfA(line,"capture=%s index=%lu success=%lu error=%lu\r\n",tag,capturecount,(DWORD)ok,GetLastError());bytes(logh,line,lstrlenA(line));capturecount++;return ok;
}
static BOOL scrollcases(const char* before,const char* edge,const char* arrow,const char* drag){
 int i;BOOL ok;
 if(!point(320,240)||!capture(before)||!point(639,240))return FALSE;
 Sleep(2500);if(!state("edge_end")||!point(320,240))return FALSE;
 Sleep(500);if(!capture(edge)||!keyhold(VK_RIGHT,1500))return FALSE;
 Sleep(500);if(!capture(arrow)||!point(320,240))return FALSE;
 if(!button(MOUSEEVENTF_RIGHTDOWN))return FALSE;
 Sleep(150);
 ok=TRUE;for(i=1;i<=10;i++){if(!point(320-i*10,240-i*5)){ok=FALSE;break;}Sleep(100);}
 ok=button(MOUSEEVENTF_RIGHTUP)&&ok;Sleep(500);return ok&&point(320,240)&&capture(drag);
}
static BOOL options(void){return click(44,14)&&click(76,100);}
static BOOL runinputs(void){
 DWORD start=GetTickCount();
 do{gamewindow=0;EnumWindows(findgame,0);if(gamewindow&&GetForegroundWindow()==gamewindow&&state("ready"))break;Sleep(500);}while(GetTickCount()-start<60000);
 if(!gamewindow||!state("start"))return FALSE;
 Sleep(8000);
 if(!capture("title")||!click(197,415))return FALSE;
 Sleep(3000);
 if(!capture("scenarios")||!click(312,136))return FALSE;
 Sleep(10000);
 if(!capture("objective")||!click(427,157)||!click(15,15))return FALSE;
 if(!options()||!capture("window-options")||!click(292,39))return FALSE;
 if(!scrollcases("window-before","window-edge","window-arrow","window-drag"))return FALSE;
 if(!options()||!click(179,286)||!capture("mode-menu")||!click(107,314))return FALSE;
 Sleep(3000);
 if(GetSystemMetrics(SM_CXSCREEN)!=640||GetSystemMetrics(SM_CYSCREEN)!=480){number("fullscreen_dimensions_failed",1);return FALSE;}
 if(!capture("full-options")||!click(292,39))return FALSE;
 if(!scrollcases("full-before","full-edge","full-arrow","full-drag"))return FALSE;
 if(!options()||!click(179,286)||!click(74,302))return FALSE;
 Sleep(3000);
 if(!capture("restored-options")||!click(292,39)||!capture("restored-window"))return FALSE;
 return TRUE;
}
static BOOL pcdisplay(void){
 DEVMODEA mode;char* cmd=GetCommandLineA();BOOL requested=FALSE;DWORD i;
 for(i=0;cmd[i];i++)if(lstrlenA(cmd+i)==6&&lstrcmpA(cmd+i,"/pc800")==0)requested=TRUE;
 number("pc_display_requested",requested);if(!requested)return TRUE;
 zero(&originalmode,sizeof(originalmode));originalmode.dmSize=sizeof(originalmode);
 if(!EnumDisplaySettingsA(0,ENUM_CURRENT_SETTINGS,&originalmode))return FALSE;
 zero(&mode,sizeof(mode));mode.dmSize=sizeof(mode);mode.dmPelsWidth=800;mode.dmPelsHeight=600;mode.dmBitsPerPel=originalmode.dmBitsPerPel;mode.dmFields=DM_PELSWIDTH|DM_PELSHEIGHT|DM_BITSPERPEL;
 if(ChangeDisplaySettingsA(&mode,CDS_TEST)!=DISP_CHANGE_SUCCESSFUL||ChangeDisplaySettingsA(&mode,0)!=DISP_CHANGE_SUCCESSFUL)return FALSE;
 displaychanged=TRUE;Sleep(2000);return GetSystemMetrics(SM_CXSCREEN)==800&&GetSystemMetrics(SM_CYSCREEN)==600;
}
