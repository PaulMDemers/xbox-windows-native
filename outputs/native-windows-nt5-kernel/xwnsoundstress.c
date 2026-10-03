/* Bounded native Win2000 waveOut diagnostic, low-amplitude stereo test tone. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <mmsystem.h>
static HANDLE Log;
static short Samples[48000*2*2];
static void line(const char *s) { DWORD n; WriteFile(Log,s,lstrlenA(s),&n,NULL); FlushFileBuffers(Log); }
static void number(const char *s,DWORD n) { char b[16]; unsigned i=sizeof(b);b[--i]=0;b[--i]='\n';b[--i]='\r';do{b[--i]='0'+n%10;n/=10;}while(n);line(s);line(b+i); }
static DWORD playback(void)
{
    WAVEFORMATEX f={WAVE_FORMAT_PCM,2,48000,192000,4,16,0};
    WAVEHDR h={0}; HWAVEOUT wave=NULL; HANDLE event; MMRESULT r; DWORD i,n,wait,start; BOOL complete;
    MMTIME position={TIME_SAMPLES};
    WAVEOUTCAPSA caps;
    n=waveOutGetNumDevs();number("Output devices: ",n);
    for(i=0;i<n;i++) { r=waveOutGetDevCapsA(i,&caps,sizeof(caps));number("Caps result: ",r);if(!r){line(caps.szPname);line("\r\n");number("Channels: ",caps.wChannels);} }
    event=CreateEventA(NULL,FALSE,FALSE,NULL); if(!event)return 1;
    r=waveOutOpen(&wave,WAVE_MAPPER,&f,(DWORD_PTR)event,0,CALLBACK_EVENT);number("Open 48k stereo 16-bit: ",r);if(r)ExitProcess(2);
    ResetEvent(event);
    for(i=0;i<48000*2;i++){int v=(int)(i%120);if(v>=60)v=119-v;v=(v-30)*64;Samples[i*2]=Samples[i*2+1]=(short)v;}
    h.lpData=(LPSTR)Samples;h.dwBufferLength=sizeof(Samples);
    r=waveOutPrepareHeader(wave,&h,sizeof(h));number("Prepare: ",r);if(r)ExitProcess(3);
    r=waveOutWrite(wave,&h,sizeof(h));number("Write: ",r);if(r)ExitProcess(4);
    start=GetTickCount();wait=WAIT_TIMEOUT;
    while (!(h.dwFlags&WHDR_DONE) && GetTickCount()-start<10000) {
        wait=WaitForSingleObject(event,250);if(wait==WAIT_FAILED)break;
    }
    complete=(h.dwFlags&WHDR_DONE)!=0;
    number("Wait result: ",wait);number("Header flags before reset: ",h.dwFlags);
    r=waveOutGetPosition(wave,&position,sizeof(position));number("Position result: ",r);
    number("Position type: ",position.wType);number("Position value: ",position.u.sample);
    r=waveOutReset(wave);number("Reset: ",r);
    r=waveOutUnprepareHeader(wave,&h,sizeof(h));number("Unprepare: ",r);
    r=waveOutClose(wave);number("Close: ",r);
    line(complete?"Playback completed\r\n":"Playback did not complete\r\n");
    CloseHandle(event);return complete && position.wType == TIME_SAMPLES && position.u.sample == 96000 ? 0 : 5;
}

void WINAPI mainCRTStartup(void)
{
    DWORD cycle, result, failures=0;
    Log=CreateFileA("C:\\xwn-sound-stress.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,
                    CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(9);
    line("XWN native waveOut repeated open/play/close test\r\n");
    for(cycle=1;cycle<=30;++cycle) {
        number("Cycle: ",cycle);result=playback();number("Cycle result: ",result);
        if(result)++failures;
        Sleep(500);
    }
    number("Failures: ",failures);CloseHandle(Log);ExitProcess(failures?1:0);
}
