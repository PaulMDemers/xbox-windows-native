/* MIT. Original pixel-checked GDI workload, with an external timed-work gate. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
typedef HBITMAP (WINAPI *DIBFN)(HDC,const BITMAPINFO*,UINT,void**,HANDLE,DWORD);
typedef int (WINAPI *STRETCHFN)(HDC,int,int,int,int,int,int,int,int,const void*,const BITMAPINFO*,UINT,DWORD);
static void zero(void*p,DWORD n){BYTE*b=p;while(n--)*b++=0;}
void WINAPI mainCRTStartup(void){
 const char *cmd=GetCommandLineA();DWORD n=lstrlenA(cmd),which,i,j=0,written,start=0,end=0;
 HANDLE ready=0,go=0,done=0,release=0,request=0,ack=0,file=INVALID_HANDLE_VALUE;
 HMODULE g;DIBFN dib;STRETCHFN stretch;HBITMAP a=0,b=0;HDC dc=0;HGDIOBJ old=0;
 DWORD *sa=0,*sb=0;BITMAPINFO info;BOOL ok=FALSE;char name[100],buf[200];
 if(!n||(cmd[n-1]!='0'&&cmd[n-1]!='1'))ExitProcess(80);
 which=cmd[n-1]-'0';
 wsprintfA(name,"C:\\xwn616\\subject%lu.txt",which);
 file=CreateFileA(name,GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(file==INVALID_HANDLE_VALUE)ExitProcess(81);
 wsprintfA(name,"XWN616_READY_%lu",which);ready=OpenEventA(EVENT_MODIFY_STATE,FALSE,name);
 wsprintfA(name,"XWN616_GO_%lu",which);go=OpenEventA(SYNCHRONIZE,FALSE,name);
 wsprintfA(name,"XWN616_DONE_%lu",which);done=OpenEventA(EVENT_MODIFY_STATE,FALSE,name);
 wsprintfA(name,"XWN616_RELEASE_%lu",which);release=OpenEventA(SYNCHRONIZE,FALSE,name);
 request=OpenEventA(EVENT_MODIFY_STATE,FALSE,"XWN616PhaseRequest");
 ack=OpenEventA(SYNCHRONIZE|EVENT_MODIFY_STATE,FALSE,"XWN616PhaseAck");
 if(!ready||!go||!done||!release||!request||!ack)goto finish;
 g=LoadLibraryA("gdi32.dll");if(!g)goto finish;
 dib=(DIBFN)GetProcAddress(g,"CreateDIBSection");stretch=(STRETCHFN)GetProcAddress(g,"StretchDIBits");
 if(!dib||!stretch)goto finish;
 zero(&info,sizeof(info));info.bmiHeader.biSize=40;info.bmiHeader.biWidth=8;info.bmiHeader.biHeight=-8;
 info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;
 a=dib(0,&info,0,(void**)&sa,0,0);b=dib(0,&info,0,(void**)&sb,0,0);
 if(!a||!b||!sa||!sb)goto finish;
 dc=CreateCompatibleDC(0);if(!dc)goto finish;old=SelectObject(dc,b);if(!old||old==HGDI_ERROR)goto finish;
 for(j=0;j<75;j++){
  if(j==35){
   if(!SetEvent(ready)||WaitForSingleObject(go,30000)!=WAIT_OBJECT_0)goto finish;
   start=GetTickCount();
   if(!SetEvent(request)||(!which&&!SetEvent(ack)))goto finish;
  }
  for(i=0;i<64;i++){sa[i]=(i*0x020301u+j*0x010101u)&0xffffffu;sb[i]=0;}
  if(stretch(dc,0,0,8,8,0,0,8,8,sa,&info,0,SRCCOPY)!=8||!GdiFlush())goto finish;
  for(i=0;i<64;i++)if(sa[i]!=sb[i])goto finish;
  if(j>=35)Sleep(125);
 }
 end=GetTickCount();
 if(WaitForSingleObject(ack,0)!=WAIT_OBJECT_0||!SetEvent(done)||WaitForSingleObject(release,30000)!=WAIT_OBJECT_0)goto finish;
 ok=TRUE;
finish:
 wsprintfA(buf,"SUBJECT %lu PID %lu START %lu END %lu COPIES %lu PASS %lu\r\n",which,GetCurrentProcessId(),start,end,j,(DWORD)ok);
 if(!WriteFile(file,buf,lstrlenA(buf),&written,0)||written!=(DWORD)lstrlenA(buf)||!FlushFileBuffers(file))ok=FALSE;
 if(old&&old!=HGDI_ERROR)SelectObject(dc,old);
 if(dc)DeleteDC(dc);
 if(a)DeleteObject(a);
 if(b)DeleteObject(b);
 if(ready)CloseHandle(ready);
 if(go)CloseHandle(go);
 if(done)CloseHandle(done);
 if(release)CloseHandle(release);
 if(request)CloseHandle(request);
 if(ack)CloseHandle(ack);
 CloseHandle(file);ExitProcess(ok?0:1);
}
