/* MIT. Original known sleep/arithmetic/copy/GDI subjects. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
extern DWORD __cdecl arith619(DWORD);
extern void __cdecl arith_end619(void);
extern void __cdecl copy619(void*,const void*,DWORD);
extern void __cdecl copy_end619(void);
static void zero(void*p,DWORD n){BYTE*b=p;while(n--)*b++=0;}
void WINAPI mainCRTStartup(void){
 const char*cmd=GetCommandLineA();DWORD n=lstrlenA(cmd),id,mode,w,start,loops=0,value=1,i;
 HANDLE ready=0,release=0,file=INVALID_HANDLE_VALUE;char path[180],buf[256];BOOL ok=FALSE;
 DWORD *a=0,*b=0;BITMAPINFO info;HBITMAP ba=0,bb=0;HDC dc=0;HGDIOBJ old=0;
 if(!n||cmd[n-1]<'0'||cmd[n-1]>'7')ExitProcess(80);
 id=cmd[n-1]-'0';mode=id%4;
 wsprintfA(path,"C:\\xwn620\\subject%lu.txt",id);
 file=CreateFileA(path,GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
 if(file==INVALID_HANDLE_VALUE)ExitProcess(81);
 ready=OpenEventA(EVENT_MODIFY_STATE,FALSE,"XWN620_READY");release=OpenEventA(SYNCHRONIZE,FALSE,"XWN620_RELEASE");
 if(!ready||!release)goto end;

 a=VirtualAlloc(0,1024*1024,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
 b=VirtualAlloc(0,1024*1024,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
 if(!a||!b)goto end;

 for(i=0;i<262144;i++)a[i]=i*0x020301u;
 if(mode==3){
  VirtualFree(a,0,MEM_RELEASE);VirtualFree(b,0,MEM_RELEASE);a=0;b=0;
  zero(&info,sizeof(info));info.bmiHeader.biSize=40;info.bmiHeader.biWidth=512;
  info.bmiHeader.biHeight=-512;info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;
  ba=CreateDIBSection(0,&info,0,(void**)&a,0,0);bb=CreateDIBSection(0,&info,0,(void**)&b,0,0);
  if(!ba||!bb||!a||!b)goto end;

  for(i=0;i<262144;i++)a[i]=(i*0x020301u)&0xffffffu;
  dc=CreateCompatibleDC(0);
 if(!dc)goto end;
old=SelectObject(dc,bb);
 if(!old||old==HGDI_ERROR)goto end;

 }
 wsprintfA(buf,"RANGES %08lx %08lx %08lx %08lx\r\n",(DWORD)arith619,(DWORD)arith_end619,(DWORD)copy619,(DWORD)copy_end619);
 if(!WriteFile(file,buf,lstrlenA(buf),&w,0)||w!=(DWORD)lstrlenA(buf)||!FlushFileBuffers(file))goto end;

 start=GetTickCount();
 if(!SetEvent(ready))goto end;

 while(WaitForSingleObject(release,0)==WAIT_TIMEOUT){
  if(GetTickCount()-start>40000)goto end;

  if(mode==0)Sleep(100);
  else if(mode==1)value=arith619(value);
  else if(mode==2)copy619(b,a,262144);
  else if(StretchDIBits(dc,0,0,512,512,0,0,512,512,a,&info,0,SRCCOPY)!=512||!GdiFlush())goto end;

  loops++;
 if(loops==0)goto end;

 }
 if(mode>=2)for(i=0;i<262144;i++)if(a[i]!=b[i])goto end;

 ok=loops>0;
end:
 wsprintfA(buf,"SUBJECT %lu MODE %lu PID %lu TID %lu LOOPS %lu VALUE %lu PASS %lu\r\n",id,mode,GetCurrentProcessId(),GetCurrentThreadId(),loops,value,(DWORD)ok);
 if(!WriteFile(file,buf,lstrlenA(buf),&w,0)||w!=(DWORD)lstrlenA(buf)||!FlushFileBuffers(file))ok=FALSE;
 if(old&&old!=HGDI_ERROR)SelectObject(dc,old);
 if(dc)DeleteDC(dc);
 if(ba)DeleteObject(ba);
 if(bb)DeleteObject(bb);
 if(mode!=3){if(a)VirtualFree(a,0,MEM_RELEASE);
 if(b)VirtualFree(b,0,MEM_RELEASE);}
 if(ready)CloseHandle(ready);
 if(release)CloseHandle(release);
 CloseHandle(file);
 ExitProcess(ok?0:1);
}
