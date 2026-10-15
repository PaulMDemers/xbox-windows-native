/* SPDX-License-Identifier: MIT
 * Fresh-assembly witness: ordinary APIs, exact persistence, no device suppression. */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#include <winsock2.h>
#include <windows.h>
#include <mmsystem.h>
static HANDLE logFile;
static BYTE payload[32768],back[32768];
static short pcm[16000];
static void zero(void *p,DWORD n){volatile BYTE *b=p;while(n--)*b++=0;}
static void number(const char *key,DWORD v){char b[192];DWORD n,w;n=wsprintfA(b,"%s=%lu\r\n",key,v);if(!WriteFile(logFile,b,n,&w,0)||w!=n||!FlushFileBuffers(logFile))ExitProcess(90);}
static BOOL persist(void){HANDLE h;DWORD i,n;BOOL ok;
    for(i=0;i<sizeof(payload);i++)payload[i]=(BYTE)(i*37+(i>>8)+0x5a);
    h=CreateFileA("C:\\XWN407\\data.tmp",GENERIC_READ|GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
    if(h==INVALID_HANDLE_VALUE)return FALSE;
    ok=WriteFile(h,payload,sizeof(payload),&n,0)&&n==sizeof(payload)&&FlushFileBuffers(h);CloseHandle(h);
    if(!ok||!MoveFileA("C:\\XWN407\\data.tmp","C:\\XWN407\\data.bin"))return FALSE;
    h=CreateFileA("C:\\XWN407\\data.bin",GENERIC_READ,0,0,OPEN_EXISTING,0,0);if(h==INVALID_HANDLE_VALUE)return FALSE;
    ok=ReadFile(h,back,sizeof(back),&n,0)&&n==sizeof(back);CloseHandle(h);
    for(i=0;i<sizeof(back);i++)if(payload[i]!=back[i])ok=FALSE;
    return ok;
}
static BOOL graphics(HDC screen){HDC a=CreateCompatibleDC(screen),b=CreateCompatibleDC(screen);HBITMAP aa,bb,oa,ob;HBRUSH brush;RECT r={0,0,64,32};DWORD x,y;BOOL ok=TRUE;
    if(!a||!b)return FALSE;
    aa=CreateCompatibleBitmap(screen,64,32);bb=CreateCompatibleBitmap(screen,64,32);if(!aa||!bb)return FALSE;
    oa=SelectObject(a,aa);ob=SelectObject(b,bb);brush=CreateSolidBrush(RGB(31,93,177));
    ok=FillRect(a,&r,brush)&&BitBlt(b,0,0,64,32,a,0,0,SRCCOPY);GdiFlush();
    for(y=0;y<32;y++)for(x=0;x<64;x++)if(GetPixel(b,x,y)!=RGB(31,93,177))ok=FALSE;
    SelectObject(a,oa);SelectObject(b,ob);DeleteObject(aa);DeleteObject(bb);DeleteObject(brush);DeleteDC(a);DeleteDC(b);return ok;
}
static DWORD audio(void){WAVEFORMATEX fmt;WAVEHDR hdr;HWAVEOUT out;DWORD i,start;MMRESULT err;
    zero(&fmt,sizeof(fmt));zero(&hdr,sizeof(hdr));fmt.wFormatTag=WAVE_FORMAT_PCM;fmt.nChannels=2;fmt.nSamplesPerSec=8000;fmt.wBitsPerSample=16;fmt.nBlockAlign=4;fmt.nAvgBytesPerSec=32000;
    for(i=0;i<8000;i++){short sample=(i%16<8)?2000:-2000;pcm[2*i]=sample;pcm[2*i+1]=sample;}
    err=waveOutOpen(&out,WAVE_MAPPER,&fmt,0,0,CALLBACK_NULL);if(err)return err;
    hdr.lpData=(LPSTR)pcm;hdr.dwBufferLength=sizeof(pcm);err=waveOutPrepareHeader(out,&hdr,sizeof(hdr));
    if(!err){err=waveOutWrite(out,&hdr,sizeof(hdr));start=GetTickCount();while(!err&&!(hdr.dwFlags&WHDR_DONE)&&GetTickCount()-start<10000)Sleep(20);if(!(hdr.dwFlags&WHDR_DONE))err=999;waveOutReset(out);waveOutUnprepareHeader(out,&hdr,sizeof(hdr));}
    waveOutClose(out);return err;
}
#include "network004.inc"
void WINAPI mainCRTStartup(void){HDC dc;DWORD start;HANDLE token;TOKEN_PRIVILEGES tp;BOOL priv=FALSE;
    logFile=CreateFileA("C:\\XWN407\\result.log",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(logFile==INVALID_HANDLE_VALUE)ExitProcess(90);
    number("BEGIN",405);number("PERSISTENCE",persist());
    dc=GetDC(0);number("WIDTH",GetDeviceCaps(dc,HORZRES));number("HEIGHT",GetDeviceCaps(dc,VERTRES));number("BPP",GetDeviceCaps(dc,BITSPIXEL));number("MEMORY_GDI",graphics(dc));ReleaseDC(0,dc);
    start=GetTickCount();while(GetTickCount()-start<90000)Sleep(1000);
    number("NETWORK_RESULT",network());
    number("WAVE_DEVICES",waveOutGetNumDevs());number("AUDIO_RESULT",audio());
    if(OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){
        tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
        if(LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){SetLastError(ERROR_SUCCESS);priv=AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)&&GetLastError()==ERROR_SUCCESS;}
        CloseHandle(token);
    }
    number("SHUTDOWN_PRIVILEGE",priv);number("COMPLETE",405);Sleep(3000);
    number("NORMAL_RESTART_REQUEST",priv&&ExitWindowsEx(EWX_REBOOT,0));CloseHandle(logFile);ExitProcess(0);
}
