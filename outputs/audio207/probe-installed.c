/* Audio207: ordinary NT5 waveOut lifecycle and channel-identifiable capture.
 * SPDX-License-Identifier: MIT
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <mmsystem.h>
static HANDLE Log;
static short Samples[48000*2*2];
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
    /* Different deterministic low-amplitude signals distinguish stereo channels. */
    for(i=0;i<96000;i++) {
        int l=i%120,rr=i%80;
        if(l>=60)l=119-l;if(rr>=40)rr=79-rr;
        Samples[2*i]=(short)((l-30)*64);Samples[2*i+1]=(short)((rr-20)*64);
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
        if(!(h.dwFlags&WHDR_DONE)||elapsed<1500||elapsed>10000)failed=1;
        pos.wType=TIME_SAMPLES;r=waveOutGetPosition(wave,&pos,sizeof(pos));
        rec("POSITION_RESULT",cycle,r);rec("POSITION_TYPE",cycle,pos.wType);
        rec("POSITION_SAMPLES",cycle,pos.u.sample);
        if(r||pos.wType!=TIME_SAMPLES||pos.u.sample!=96000)failed=1;
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
    rec("AUDIO207_BEGIN",1,waveOutGetNumDevs());
    if(waveOutGetNumDevs()!=1){rec("FAIL_DEVICE_COUNT",0,0);ExitProcess(1);}
    r=waveOutGetDevCapsA(WAVE_MAPPER,&caps,sizeof(caps));rec("CAPS",r,r?0:caps.wChannels);
    if(r||caps.wChannels!=2)ExitProcess(2);
    for(i=0;i<12;i++){BOOL reset=(i%3)==1;rec("CYCLE",i,reset);failures+=play(i,reset);Sleep(350);}
    rec("AUDIO207_END",12,failures);CloseHandle(Log);ExitProcess(failures?1:0);
}
