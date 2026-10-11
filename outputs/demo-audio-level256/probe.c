/* Audio207: ordinary NT5 waveOut lifecycle and channel-identifiable capture.
 * SPDX-License-Identifier: MIT
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <mmsystem.h>
#include "waveform.h"
static HANDLE Log;
static void rec(const char *tag,DWORD a,DWORD b);
static void visible(const char *text) {
    DWORD written=0, length=lstrlenA(text), error=0; HANDLE console=GetStdHandle(STD_OUTPUT_HANDLE);
    if(console==NULL || console==INVALID_HANDLE_VALUE)error=ERROR_INVALID_HANDLE;
    else if(!WriteFile(console,text,length,&written,NULL))error=GetLastError();
    else if(written!=length)error=ERROR_WRITE_FAULT;
    rec("VISIBLE_RESULT",length,error);
}
static short Samples[CHANNEL001_FRAMES*2];
static void rec(const char *tag,DWORD a,DWORD b) {
    char s[160];DWORD n,w;n=wsprintfA(s,"%s %lu %lu\r\n",tag,a,b);
    if(!WriteFile(Log,s,n,&w,NULL)||w!=n||!FlushFileBuffers(Log))ExitProcess(90);
}
static DWORD play(DWORD cycle,BOOL aborting) {
    WAVEFORMATEX f={WAVE_FORMAT_PCM,2,48000,192000,4,16,0};
    WAVEHDR h={0};HWAVEOUT wave=NULL;HANDLE event;MMRESULT r;
    MMTIME pos={0};DWORD i,start,elapsed,failed=0;BOOL prepared=FALSE,queued=FALSE;
    event=CreateEventA(NULL,FALSE,FALSE,NULL);if(!event)return 1;
    r=waveOutOpen(&wave,WAVE_MAPPER,&f,(DWORD_PTR)event,0,CALLBACK_EVENT);
    rec("OPEN",cycle,r);if(r){CloseHandle(event);return 1;}
    ResetEvent(event);
    { UINT device=0xffffffffU; DWORD volume=0xdeadbeefU;
      r=waveOutGetID(wave,&device);rec("DEVICE_ID_RESULT",cycle,r);rec("DEVICE_ID",cycle,device);
      if(r==MMSYSERR_NOERROR) {
          WAVEOUTCAPSA actual={0}; DWORD written=0; char line[128];
          r=waveOutGetDevCapsA(device,&actual,sizeof(actual));rec("DEVICE_CAPS_RESULT",cycle,r);
          if(r==MMSYSERR_NOERROR) {
              rec("DEVICE_CAPS_SUPPORT",cycle,actual.dwSupport);
              actual.szPname[sizeof(actual.szPname)-1]=0;
              wsprintfA(line,"DEVICE_NAME %lu %s\r\n",cycle,actual.szPname);
              if(!WriteFile(Log,line,lstrlenA(line),&written,NULL)||written!=(DWORD)lstrlenA(line)||!FlushFileBuffers(Log))ExitProcess(90);
          }
      }
      r=waveOutGetVolume(wave,&volume);rec("VOLUME_RESULT",cycle,r);rec("VOLUME_PACKED",cycle,volume);
      if(r==MMSYSERR_NOERROR) {rec("VOLUME_LOW16",cycle,volume&65535U);rec("VOLUME_HIGH16",cycle,volume>>16);}
    }
    unsigned mask = cycle % 3 + 1;
    rec("PHASE_MASK",cycle,mask);
    rec("PHASE_BEGIN_MS",cycle,GetTickCount());
    rec("SAMPLE_GAIN",cycle,cycle<3?1:4);
    visible(cycle<3?"Original quiet level: ":"Four-times sample level: ");
    visible(mask==1?"LEFT\r\n":mask==2?"RIGHT\r\n":"BOTH\r\n");
    for(i=0;i<CHANNEL001_FRAMES;i++) {
        Samples[2*i]=(short)(channel001_sample(i,0,mask)*(cycle<3?1:4));
        Samples[2*i+1]=(short)(channel001_sample(i,1,mask)*(cycle<3?1:4));
    }
    h.lpData=(LPSTR)Samples;h.dwBufferLength=sizeof(Samples);
    r=waveOutPrepareHeader(wave,&h,sizeof(h));rec("PREPARE",cycle,r);
    if(r){failed=1;goto cleanup;}prepared=TRUE;
    r=waveOutWrite(wave,&h,sizeof(h));rec("WRITE",cycle,r);
    if(r){failed=1;goto cleanup;}queued=TRUE;start=GetTickCount();
    if(aborting)Sleep(100);
    else {
        while(!(h.dwFlags&WHDR_DONE)&&GetTickCount()-start<10000) {
            r=WaitForSingleObject(event,100);
            if(r!=WAIT_OBJECT_0&&r!=WAIT_TIMEOUT){failed=1;break;}
        }
        elapsed=GetTickCount()-start;
        rec("DONE_BEFORE_RESET",cycle,(h.dwFlags&WHDR_DONE)!=0);
        rec("ELAPSED_MS",cycle,elapsed);
        if(!(h.dwFlags&WHDR_DONE)||elapsed<2500||elapsed>10000)failed=1;
        pos.wType=TIME_SAMPLES;r=waveOutGetPosition(wave,&pos,sizeof(pos));
        rec("POSITION_RESULT",cycle,r);rec("POSITION_TYPE",cycle,pos.wType);
        rec("POSITION_SAMPLES",cycle,pos.u.sample);
        if(r||pos.wType!=TIME_SAMPLES||pos.u.sample!=CHANNEL001_FRAMES)failed=1;
    }
cleanup:
    if(queued) {
        r=waveOutReset(wave);rec("RESET",cycle,r);if(r)failed=1;
        rec("DONE_AFTER_RESET",cycle,(h.dwFlags&WHDR_DONE)!=0);
        if(!(h.dwFlags&WHDR_DONE))failed=1;
    }
    if(prepared){r=waveOutUnprepareHeader(wave,&h,sizeof(h));rec("UNPREPARE",cycle,r);if(r)failed=1;}
    r=waveOutClose(wave);rec("CLOSE",cycle,r);
    /* On failed close, retain callback event/buffer lifetime until process exit. */
    if(r){rec("FAIL_CLOSE",cycle,r);ExitProcess(91);}
    CloseHandle(event);return failed;
}
void WINAPI mainCRTStartup(void) {
    DWORD i,failures=0;WAVEOUTCAPSA caps;MMRESULT r;
    Log=CreateFileA("audio207.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
    rec("CHANNEL001_BEGIN",1,waveOutGetNumDevs());
    if(waveOutGetNumDevs()!=1){rec("FAIL_DEVICE_COUNT",0,0);ExitProcess(1);}
    r=waveOutGetDevCapsA(WAVE_MAPPER,&caps,sizeof(caps));rec("CAPS",r,r?0:caps.wChannels);
    if(r||caps.wChannels!=2)ExitProcess(2);
    rec("CAPS_SUPPORT",0,caps.dwSupport);
    visible("Audio comparison begins in 15 seconds. Leave speaker volume unchanged.\r\nFirst quiet LEFT/RIGHT/BOTH; then moderately louder LEFT/RIGHT/BOTH.\r\n");
    Sleep(15000);
    for(i=0;i<6;i++){BOOL reset=FALSE;rec("CYCLE",i,reset);failures+=play(i,reset);Sleep(350);}
    rec("CHANNEL001_END",6,failures);CloseHandle(Log);ExitProcess(failures?1:0);
}
