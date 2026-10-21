/* SPDX-License-Identifier: MIT
 * Read-only4034 programming facts. No video API, MMIO, SMBus, EEPROM or Windows
 * access. Header/code bytes stay in local scratch and are never logged.
 */
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdio.h>
#include "facts.h"
#include "memory.h"
typedef struct {uint32_t magic,phase,error,build,log_ok,close_ok,reads;Profile632 facts;} Record632;
volatile Record632 record632;
__attribute__((noinline)) void checkpoint632(unsigned phase,volatile Record632 *r) {
 __asm__ __volatile__("" ::: "memory");r->phase=phase;__asm__ __volatile__("" ::: "memory");
}
static int valid632(void *o,uint32_t a){(void)o;return !!MmIsAddressValid((void*)(uintptr_t)a);}
static int read632(void *o,uint32_t offset,void *out,unsigned n) {
 (void)o;if(!range632(offset,n,valid632,0))return 0;
 volatile const uint8_t *src=(volatile const uint8_t*)(uintptr_t)(0x80010000u+offset);
 for(unsigned i=0;i<n;i++)((uint8_t*)out)[i]=src[i];
 record632.reads++;return 1;
}
static int write632(HANDLE f,const char *text) {
 DWORD done=0;unsigned n=(unsigned)strlen(text);IO_STATUS_BLOCK io;
 return WriteFile(f,text,n,&done,0) && done==n && (LONG)NtFlushBuffersFile(f,&io)>=0;
}
int main(void) {
 Profile632 p={0};char line[128];record632.magic=0x632c0de;record632.build=XboxKrnlVersion.Build;
 record632.error=facts632(read632,0,XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe,(uint32_t)(uintptr_t)AvSetDisplayMode,&p);
 if(!record632.error)record632.facts=p;
 HANDLE f=CreateFileA("D:\\facts632.txt",GENERIC_WRITE,0,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);
 if(f!=INVALID_HANDLE_VALUE) {
  snprintf(line,sizeof(line),"XWN_FACTS632 version=1 kernel=%u.%u.%u.%u error=%lu reads=%lu\r\n",XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe,(unsigned long)record632.error,(unsigned long)record632.reads);
  int ok=write632(f,line);
  if(!record632.error) {
   for(unsigned i=0;i<35;i++){snprintf(line,sizeof(line),"CR index=%02x value=%02x\r\n",i==34?0x28:expected_ci[i],p.crtc[i]);ok=write632(f,line)&&ok;}
   for(unsigned i=0;i<28;i++){snprintf(line,sizeof(line),"MM offset=%08lx value=%08lx\r\n",(unsigned long)(i<26?expected_mi[i]:i==26?0x680880:0x680600),(unsigned long)p.mmio[i]);ok=write632(f,line)&&ok;}
   for(unsigned i=0;i<14;i++){snprintf(line,sizeof(line),"EN index=%02x value=%02x\r\n",i==13?0xba:expected_ei[i],p.encoder[i]);ok=write632(f,line)&&ok;}
  }
  snprintf(line,sizeof(line),"COMPLETE error=%lu log_ok=%u\r\n",(unsigned long)record632.error,ok);ok=write632(f,line)&&ok;
  record632.log_ok=ok;record632.close_ok=!!CloseHandle(f);
 }
 checkpoint632(record632.error?255:44,&record632);
 Sleep(1000);HalReturnToFirmware(HalRebootRoutine);return 0;
}
