/* Translated geometry and fixed-height width sweep on unchanged RAM0112. GPL-2.0-or-later. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#define W 768
#define H 384
#define BYTES (W*H*4)
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
typedef struct {HDC dc;HBITMAP bm;HGDIOBJ old;DWORD *bits;} IMAGE;
static HANDLE Log;
static HWND Window;
static HDC Screen;
static IMAGE Ref,Readback;
static DWORD Failures,Stage;
static HBRUSH Brushes[2];
static LARGE_INTEGER Frequency;
static const DWORD Widths[15]={192,192,192,192,192,192,192,192,192,64,128,192,256,320,384};
static const DWORD Heights[15]={96,96,96,96,96,96,96,96,96,96,96,96,96,96,96};
static const DWORD Kinds[15]={0,0,0,3,3,3,4,4,4,0,0,0,0,0,0};
static const DWORD Xs[15]={0,128,0,0,128,0,0,128,0,320,320,320,320,320,320};
static const DWORD Ys[15]={0,0,160,0,0,160,0,0,160,64,64,64,64,64,64};
static RECT LastClip;
static int LastClipType;
static void zero(void *p,DWORD n){volatile BYTE *b=p;while(n--)*b++=0;}
static DWORD hash(const void *p,DWORD n){const BYTE *b=p;DWORD v=2166136261u;while(n--)v=(v^*b++)*16777619u;return v;}
static void record(const char *s,DWORD a,DWORD b,DWORD c){char t[160];DWORD n,w;n=wsprintfA(t,"%s %lu %lu %lu\r\n",s,a,b,c);if(!WriteFile(Log,t,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM a,LPARAM b){if(m==WM_SETCURSOR){SetCursor(NULL);return TRUE;}if(m==WM_PAINT){PAINTSTRUCT p;BeginPaint(w,&p);EndPaint(w,&p);return 0;}if(m==WM_ERASEBKGND)return 1;return DefWindowProcA(w,m,a,b);}
static BOOL visible(void){MSG m;while(PeekMessageA(&m,NULL,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessageA(&m);}LastClipType=GetClipBox(Screen,&LastClip);return LastClipType==SIMPLEREGION&&LastClip.left<=0&&LastClip.top<=0&&LastClip.right>=W&&LastClip.bottom>=H;}
static BOOL uncover(void){DWORD start=GetTickCount();do{visible();if(!SetWindowPos(Window,HWND_TOPMOST,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_SHOWWINDOW))return FALSE;Sleep(200);if(visible())return TRUE;}while(GetTickCount()-start<10000);return FALSE;}
static BOOL image(IMAGE *im,int w,int h){BITMAPINFO bi;zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);bi.bmiHeader.biWidth=w;bi.bmiHeader.biHeight=-h;bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;im->dc=CreateCompatibleDC(Screen);im->bm=CreateDIBSection(Screen,&bi,DIB_RGB_COLORS,(void**)&im->bits,NULL,0);if(!im->dc||!im->bm)return FALSE;im->old=SelectObject(im->dc,im->bm);return im->old&&im->old!=HGDI_ERROR;}
static BOOL release(IMAGE *im){BOOL ok=SelectObject(im->dc,im->old)!=NULL;ok=DeleteObject(im->bm)&&ok;return DeleteDC(im->dc)&&ok;}
static DWORD base(int x,int y){return (((x*3+y*5)&255)<<16)|(((x*7+y*11)&255)<<8)|((x*13+y*17)&255);}
static BOOL stats(DWORD *d){zero(d,128);return GdiFlush()&&ExtEscape(Screen,0x58574432,0,NULL,128,(LPSTR)d)==1&&d[0]==0x53525758&&d[1]==112&&d[19]==0&&d[20]==1;}

static BOOL clock_start(void){LARGE_INTEGER a,b,d,minimum,maximum;DWORD i,zeros=0,negatives=0,tick,dt,tmin=0xffffffff,tlast;
 if(!QueryPerformanceFrequency(&Frequency)||Frequency.QuadPart<=0||!QueryPerformanceCounter(&a))return FALSE;
 record("CLOCK_FREQUENCY",Frequency.LowPart,Frequency.HighPart,0);minimum.QuadPart=0x7fffffffffffffffLL;maximum.QuadPart=0;tlast=GetTickCount();
 for(i=0;i<8192;i++){if(!QueryPerformanceCounter(&b))return FALSE;d.QuadPart=b.QuadPart-a.QuadPart;if(d.QuadPart<0)negatives++;else if(!d.QuadPart)zeros++;else if(d.QuadPart<minimum.QuadPart)minimum=d;if(d.QuadPart>maximum.QuadPart)maximum=d;a=b;tick=GetTickCount();dt=tick-tlast;if(dt&&dt<tmin)tmin=dt;tlast=tick;}
 record("CLOCK_MIN",minimum.LowPart,minimum.HighPart,0);record("CLOCK_MAX",maximum.LowPart,maximum.HighPart,0);record("CLOCK_READS",8192,zeros,negatives);record("TICK_MIN",tmin,0,0);
 for(i=0;i<3;i++){tick=GetTickCount();if(!QueryPerformanceCounter(&a))return FALSE;Sleep(200);if(!QueryPerformanceCounter(&b))return FALSE;dt=GetTickCount()-tick;d.QuadPart=b.QuadPart-a.QuadPart;record("SLEEP_QPC",d.LowPart,d.HighPart,i);record("SLEEP_TICK",i,dt,0);}
 return negatives==0&&minimum.QuadPart>0&&minimum.QuadPart!=0x7fffffffffffffffLL;
}
static HRGN region(DWORD size,DWORD kind){HRGN all=CreateRectRgn(0,0,0,0),part;DWORD i,n=kind==0?1:(kind<=2?4:16),w=Widths[size],h=Heights[size];BOOL vertical=kind==2||kind==4;
 if(!all)return NULL;
 for(i=0;i<n;i++){DWORD l=0,t=0,r=w,b=h;if(kind){if(vertical){l=i*2*(w/n);r=l+w/n;}else{t=i*2*(h/n);b=t+h/n;}}
  part=CreateRectRgn(l+Xs[size],t+Ys[size],r+Xs[size],b+Ys[size]);if(!part||CombineRgn(all,all,part,RGN_OR)==ERROR){if(part)DeleteObject(part);DeleteObject(all);return NULL;}DeleteObject(part);
 }
 return all;
}
static BOOL batch(HDC dc,DWORD loops,LARGE_INTEGER *duration,DWORD *elapsed){LARGE_INTEGER a,b;DWORD i,start=GetTickCount();BOOL ok=TRUE;
 if(!QueryPerformanceCounter(&a))return FALSE;
 for(i=0;i<loops;i++){if(!SelectObject(dc,Brushes[i&1])||!PatBlt(dc,0,0,W,H,PATCOPY)){ok=FALSE;break;}}
 ok=GdiFlush()&&ok;if(!QueryPerformanceCounter(&b))return FALSE;duration->QuadPart=b.QuadPart-a.QuadPart;*elapsed=GetTickCount()-start;return ok&&duration->QuadPart>=0;
}
static BOOL phase(HDC dc,DWORD sample,DWORD target){DWORD n=32,cal=0,elapsed,i,quiet[32],pre[32],post[32];LARGE_INTEGER duration;BOOL reached=FALSE;
 if(!batch(dc,8,&duration,&elapsed))return FALSE;
 do{if(!batch(dc,n,&duration,&elapsed))return FALSE;cal+=n;if(elapsed>=500){reached=TRUE;break;}n*=2;}while(n<=65536);
 if(!reached){record("CALIBRATION_SHORT",sample,target,cal);return FALSE;}
 if(!stats(quiet)||!stats(pre))return FALSE;
 if(!batch(dc,n,&duration,&elapsed)||!stats(post))return FALSE;
 record("PHASE",sample,target,n);record("CALIBRATION",8,cal,500);record("DURATION_QPC",duration.LowPart,duration.HighPart,0);record("DURATION_MS",elapsed,0,0);
 for(i=2;i<=18;i++){record("QUIET_COUNTER",i,quiet[i],pre[i]);record("DRAW_COUNTER",i,pre[i],post[i]);}
 record("COHERENCE_ACTIVE",post[19],post[20],0);return TRUE;
}
static BOOL save(const char *prefix,DWORD n,const void *bytes){char path[96];HANDLE f;DWORD written;BOOL ok;wsprintfA(path,"C:\\xwnpos140\\%s%02lu.rgb",prefix,n);f=CreateFileA(path,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(f==INVALID_HANDLE_VALUE)return FALSE;ok=WriteFile(f,bytes,BYTES,&written,NULL)&&written==BYTES&&FlushFileBuffers(f);return CloseHandle(f)&&ok;}
static BOOL one(DWORD sample){DWORD rep=sample/15,cell=(sample%15+rep*5)%15,size=cell,kind=Kinds[cell],i,x,y,bad=0,changed=0,digest,n=kind==0?1:(kind<=2?4:16);HRGN clip;BOOL ok;HGDIOBJ olds,oldr;
 Stage=1;if(!uncover())return FALSE;
 record("CASE",sample,size,kind);record("LAYOUT",Widths[size],Heights[size],n);record("ORIGIN",Xs[size],Ys[size],size);record("CLIP_TYPE_LEFT_TOP",LastClipType,LastClip.left,LastClip.top);record("CLIP_RIGHT_BOTTOM",LastClip.right,LastClip.bottom,sample);
 for(y=0;y<H;y++)for(x=0;x<W;x++)Ref.bits[y*W+x]=base(x,y);
 Stage=2;if(!BitBlt(Screen,0,0,W,H,Ref.dc,0,0,SRCCOPY)||!GdiFlush())return FALSE;
 clip=region(size,kind);if(!clip||SelectClipRgn(Screen,clip)==ERROR||SelectClipRgn(Ref.dc,clip)==ERROR)return FALSE;
 olds=SelectObject(Screen,Brushes[0]);oldr=SelectObject(Ref.dc,Brushes[0]);if(!olds||!oldr)return FALSE;
 Stage=3;if(sample&1)ok=phase(Screen,sample,1)&&phase(Ref.dc,sample,0);else ok=phase(Ref.dc,sample,0)&&phase(Screen,sample,1);
 Stage=4;ok=SelectObject(Screen,olds)!=NULL&&ok;ok=SelectObject(Ref.dc,oldr)!=NULL&&ok;ok=SelectClipRgn(Screen,NULL)!=ERROR&&ok;ok=SelectClipRgn(Ref.dc,NULL)!=ERROR&&ok;ok=DeleteObject(clip)&&ok;if(!ok)return FALSE;
 if(!BitBlt(Readback.dc,0,0,W,H,Screen,0,0,SRCCOPY)||!GdiFlush())return FALSE;
 for(y=0;y<H;y++)for(x=0;x<W;x++){i=y*W+x;bad+=((Ref.bits[i]^Readback.bits[i])&0xffffff)!=0;changed+=(Ref.bits[i]&0xffffff)!=base(x,y);}
 digest=hash(Ref.bits,BYTES);record("PIXELS_BAD_CHANGED",W*H,bad,changed);record("REFERENCE_HASH_BYTES",digest,BYTES,hash(Ref.bits,BYTES));
 if(bad||changed!=Widths[size]*Heights[size])Failures++;
 Stage=5;return save("ref",sample,Ref.bits)&&save("got",sample,Readback.bits);
}
static BOOL restart(void){HANDLE t,v;TOKEN_PRIVILEGES p;v=CreateFileA("\\\\.\\C:",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);if(v==INVALID_HANDLE_VALUE)return FALSE;if(!FlushFileBuffers(v)){CloseHandle(v);return FALSE;}CloseHandle(v);if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&t))return FALSE;p.PrivilegeCount=1;p.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&p.Privileges[0].Luid)){CloseHandle(t);return FALSE;}SetLastError(0);if(!AdjustTokenPrivileges(t,FALSE,&p,0,NULL,NULL)||GetLastError()){CloseHandle(t);return FALSE;}CloseHandle(t);record("NORMAL_RESTART_REQUEST",0,0,0);return FlushFileBuffers(Log)&&ExitWindowsEx(EWX_REBOOT,0);}

void WINAPI mainCRTStartup(void){WNDCLASSA wc;WAIT_INSTALL wait_install;DWORD wait,i,start,id[8];BOOL ok;LARGE_INTEGER endfreq;
 Log=CreateFileA("C:\\xwnpos140\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);if(Log==INVALID_HANDLE_VALUE)ExitProcess(91);record("ATTEMPT_ONCE",140,45,W*H);
 wait_install=(WAIT_INSTALL)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");if(!wait_install)ExitProcess(1);wait=wait_install(30000);record("INSTALL_IDLE_START",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(2);
 zero(&wc,sizeof(wc));wc.style=CS_OWNDC;wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="XwnPos140";if(!RegisterClassA(&wc))ExitProcess(3);
 Window=CreateWindowExA(WS_EX_TOPMOST,wc.lpszClassName,"XWN RAM0112 position and width controls",WS_POPUP|WS_VISIBLE,0,0,1024,576,NULL,NULL,wc.hInstance,NULL);if(!Window)ExitProcess(4);SetForegroundWindow(Window);UpdateWindow(Window);Screen=GetDC(Window);if(!Screen)ExitProcess(5);GdiSetBatchLimit(1);SetCursor(NULL);
 zero(id,sizeof(id));if(ExtEscape(Screen,0x58574431,0,NULL,sizeof(id),(LPSTR)id)!=1||id[0]!=0x44525758||id[1]!=112||id[2]!=1024||id[3]!=576||id[4]!=4096||id[5]!=32||id[6]!=2359296||id[7]!=1)ExitProcess(6);record("DRIVER_REVISION_GEOMETRY",id[1],id[2],id[3]);
 if(!image(&Ref,W,H)||!image(&Readback,W,H)){ExitProcess(7);}Brushes[0]=CreateSolidBrush(RGB(199,43,87));Brushes[1]=CreateSolidBrush(RGB(43,199,87));if(!Brushes[0]||!Brushes[1])ExitProcess(8);
 start=GetTickCount();while(GetTickCount()-start<2000){visible();Sleep(20);}if(!clock_start())ExitProcess(9);
 for(i=0;i<45;i++)if(!one(i)){record("HARNESS_FAILURE",i,GetLastError(),Stage);if(restart()){CloseHandle(Log);ExitProcess(10);}record("FAIL_RESTART",GetLastError(),0,0);ExitProcess(11);}
 ok=release(&Ref);ok=release(&Readback)&&ok;ok=DeleteObject(Brushes[0])&&ok;ok=DeleteObject(Brushes[1])&&ok;ok=(ReleaseDC(Window,Screen)!=0)&&ok;ok=DestroyWindow(Window)&&ok;record("RELEASED",ok,0,0);if(!ok)Failures++;
 if(!QueryPerformanceFrequency(&endfreq)){ExitProcess(12);}record("CLOCK_FREQUENCY_END",endfreq.LowPart,endfreq.HighPart,0);
 record("COMPLETE",Failures,45,45*W*H);wait=wait_install(30000);record("INSTALL_IDLE_END",wait,0,0);if(wait!=WAIT_OBJECT_0)ExitProcess(13);
 if(!restart()){record("RESTART_FAILURE",GetLastError(),0,0);ExitProcess(14);}CloseHandle(Log);ExitProcess(0);
}
