/* SPDX-License-Identifier: MIT; actual main and engine, all SDK services MODELED. */
#include "host-sdk.h"
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
int guest_main(void);
struct kernel528 XboxKrnlVersion={1,0,5838,1};
static uint32_t pixels[1280*720];
static unsigned mode,step,file_fail,file_calls,opened,closed,link_live,live,stage,firmware,slept,blue,green,red;
static unsigned char files[2][49];
static char transcript[8192];static size_t used;
static int file_ok(void) {return ++file_calls!=file_fail;}
BOOL XVideoSetMode(int w,int h,int b,int r) {assert(step++==0 && w==1280 && h==720 && b==32 && r==60);return mode!=1;}
VIDEO_MODE XVideoGetMode(void) {return (VIDEO_MODE){mode==2?640:1280,720,32,60};}
unsigned char *XVideoGetFB(void) {return mode==3?NULL:(unsigned char *)pixels;}
size_t MmQueryAllocationSize(void *p) {assert(p==pixels);return mode==4?4096:sizeof(pixels);}
void XVideoFlushFB(void)
{
 uint32_t c=pixels[1280*719];
 if(c==0x000060c0)++blue;else if(c==0x0000a040)++green;else if(c==0x00c02020)++red;
}
void debugClearScreen(void) {memset(pixels,0,sizeof(pixels));}
void debugPrint(const char *fmt,...)
{
 va_list args;va_start(args,fmt);int n=vsnprintf(transcript+used,sizeof(transcript)-used,fmt,args);va_end(args);
 assert(n>=0 && (size_t)n<sizeof(transcript)-used);used+=(size_t)n;
}
void Sleep(DWORD n) {assert(n==12000 || n==20000);slept+=n;}
void HalReturnToFirmware(int mode_) {assert(mode_==1 && slept==32000);++firmware;}
int nxIsDriveMounted(char d) {assert(d=='E' && slept==12000);assert(mode>=1&&mode<=4 ? !blue : blue);return mode!=5 && mode!=6;}
int nxMountDrive(char d,const char *p) {assert(d=='E' && !strcmp(p,"\\Device\\Harddisk0\\Partition1"));return mode!=6;}
DWORD GetLastError(void) {return 1234;}
void RtlInitAnsiString(ANSI_STRING *s,const char *p) {s->Buffer=(char *)p;s->Length=(uint16_t)strlen(p);s->MaximumLength=s->Length+1;}
NTSTATUS NtOpenSymbolicLinkObject(HANDLE *h,OBJECT_ATTRIBUTES *a)
{(void)a;if(mode==7)return -1;assert(!link_live);link_live=1;*h=(HANDLE)(uintptr_t)2;return 0;}
NTSTATUS NtQuerySymbolicLinkObject(HANDLE h,ANSI_STRING *v,ULONG *n)
{
 assert(h==(HANDLE)(uintptr_t)2 && link_live && v->MaximumLength==128);
 if(mode==8)return -2;
 const char *p=mode==10?"\\Device\\Harddisk0\\Partition6":"\\Device\\Harddisk0\\Partition1";
 memcpy(v->Buffer,p,strlen(p));v->Length=mode==9?129:(uint16_t)strlen(p);*n=v->Length;
 if(mode==11)v->Buffer[2]=1;
 return 0;
}
NTSTATUS NtClose(HANDLE h) {assert(h==(HANDLE)(uintptr_t)2 && link_live);link_live=0;return mode==12?-3:0;}
HANDLE CreateFileA(const char *p,DWORD access,DWORD share,void *sa,DWORD how,DWORD attr,HANDLE template_)
{
 assert(!live && !sa && !template_ && attr==128);
 assert(!strncmp(p,"E:\\Applications\\XWNDispatch528\\",31));
 assert((how==CREATE_NEW && access==GENERIC_WRITE && share==0)||(how==OPEN_EXISTING && access==GENERIC_READ && share==FILE_SHARE_READ));
 if(!file_ok())return INVALID_HANDLE_VALUE;
 stage=strstr(p,"begin.bin")?0:1;live=1;++opened;return (HANDLE)(uintptr_t)3;
}
int WriteFile(HANDLE h,const void *d,DWORD n,DWORD *count,void *over)
{assert(h==(HANDLE)(uintptr_t)3&&live&&!over&&n==48);if(!file_ok())return 0;memcpy(files[stage],d,n);*count=mode==13?47:n;return 1;}
int ReadFile(HANDLE h,void *d,DWORD n,DWORD *count,void *over)
{assert(h==(HANDLE)(uintptr_t)3&&live&&!over&&n==49);if(!file_ok())return 0;memcpy(d,files[stage],49);*count=mode==14?49:48;if(mode==15)((char *)d)[0]^=1;return 1;}
NTSTATUS NtFlushBuffersFile(HANDLE h,IO_STATUS_BLOCK *io)
{assert(h==(HANDLE)(uintptr_t)3&&live&&io);return file_ok()?0:-4;}
int CloseHandle(HANDLE h) {assert(h==(HANDLE)(uintptr_t)3&&live);live=0;++closed;return file_ok();}
static void reset(unsigned scenario,unsigned fail)
{
 mode=scenario;file_fail=fail;step=file_calls=opened=closed=link_live=live=stage=firmware=slept=blue=green=red=0;
 used=0;memset(files,0,sizeof(files));memset(pixels,0,sizeof(pixels));memset(transcript,0,sizeof(transcript));
}
int main(int argc,char **argv)
{
 assert(argc==2);FILE *log=fopen(argv[1],"wb");assert(log);unsigned cases=0;
 for(unsigned scenario=0;scenario<=15;++scenario) {
  reset(scenario,0);assert(guest_main()==0);assert(firmware==1 && !link_live && !live && opened==closed);
  int success=scenario<=5;
  if(scenario>=1&&scenario<=4)assert(!blue&&!green&&!red&&used==0);
  else {assert(blue && !!green==success && !!red==!success);assert(strstr(transcript,success?"GREEN:":"RED:"));}
  if(scenario>=6&&scenario<=12)assert(!file_calls);
  if(scenario==0)assert(file_calls==14 && strstr(transcript,"Alias target: \\Device\\Harddisk0\\Partition1"));
  if(scenario==11)assert(strstr(transcript,"Alias target: \\D?vice"));
  fprintf(log,"SCENARIO %u\n%s",scenario,transcript);++cases;
 }
 for(unsigned fail=1;fail<=14;++fail) {
  reset(0,fail);assert(guest_main()==0);assert(firmware==1 && !link_live && !live && opened==closed && blue && red && !green);
  assert(strstr(transcript,"RED:"));fprintf(log,"FILE FAILURE %u\n%s",fail,transcript);++cases;
 }
 assert(fclose(log)==0);printf("PASS %u actual main/UI scenarios with modeled SDK services\n",cases);
}
