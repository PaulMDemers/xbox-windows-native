/* SPDX-License-Identifier: MIT

 * Kernel entry-layout827; read-only display sampling then disk report and firmware return.

 * Kernel APIs can block. No mode selection, drawing, native transition or Windows.

 */

#include <hal/debug.h>

#include <hal/video.h>

#include <windows.h>

#include <xboxkrnl/xboxkrnl.h>

#include <nxdk/mount.h>

#include <stdarg.h>

#include <stdint.h>

#include <stdio.h>

#include <string.h>

#include "layout.h"

#include "plan.h"

#include "page.h"

#include "embed.h"



static char report[32768], verify[32768];

static size_t used;

static int overflow;



/* DVD launches mount D only. Never replace an existing drive mapping: verify

 * the native target, and refuse any mapping other than standard dashboard E. */

static int prepare_e(void)

{

    const char *target = "\\Device\\Harddisk0\\Partition1";

    if (!nxIsDriveMounted('E') && !nxMountDrive('E', target)) return 0;

    ANSI_STRING name, value;

    OBJECT_ATTRIBUTES attributes;

    HANDLE handle;

    char buffer[128];

    RtlInitAnsiString(&name, "\\??\\E:");

    InitializeObjectAttributes(&attributes, &name, OBJ_CASE_INSENSITIVE, NULL, NULL);

    if (!NT_SUCCESS(NtOpenSymbolicLinkObject(&handle, &attributes))) return 0;

    value.Buffer = buffer; value.Length = 0; value.MaximumLength = sizeof(buffer);

    ULONG returned = 0;

    NTSTATUS status = NtQuerySymbolicLinkObject(handle, &value, &returned);

    NtClose(handle);

    return NT_SUCCESS(status) && value.Length == strlen(target) &&

           !memcmp(value.Buffer, target, value.Length);

}



static void append(const char *fmt, ...)

{

    if (overflow) return;

    va_list args;

    va_start(args, fmt);

    int n = vsnprintf(report + used, sizeof(report) - used, fmt, args);

    va_end(args);

    if (n < 0 || (size_t)n >= sizeof(report) - used) { overflow = 1; return; }

    used += (size_t)n;

}



static int save_report(char *path, size_t size)

{

    HANDLE file = INVALID_HANDLE_VALUE;

    for (unsigned i = 0; i < 100; ++i) {

        snprintf(path, size, "E:\\xwn-mode827-%02u.json", i);

        file = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);

        if (file != INVALID_HANDLE_VALUE) break;

        if (GetLastError() != ERROR_FILE_EXISTS && GetLastError() != ERROR_ALREADY_EXISTS) return 1;

    }

    if (file == INVALID_HANDLE_VALUE) return 2;

    DWORD written = 0;

    IO_STATUS_BLOCK io;

    int ok = WriteFile(file, report, (DWORD)used, &written, NULL) && written == used;

    if ((LONG)NtFlushBuffersFile(file, &io) < 0) ok = 0;

    if (!CloseHandle(file)) ok = 0;

    if (!ok) return 3;

    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

    if (file == INVALID_HANDLE_VALUE) return 4;

    DWORD got = 0;

    ok = ReadFile(file, verify, sizeof(verify), &got, NULL) && got == used && !memcmp(report, verify, used);

    if (!CloseHandle(file)) ok = 0;

    return ok ? 0 : 5;

}






struct sample827 {uint32_t pci[3],mm[19],cr[4],selector_before,selector_after,accepted;};
static const unsigned offsets827[]={0x600800,0x680800,0x680804,0x68080c,0x680810,0x680818,0x680820,0x680824,0x68082c,0x680830,0x680838,0x680630,0x68084c,0x680880,0x6808c4,0x600804,0x680508,0x68050c,0x100200};
void sample827(struct sample827 *s)
{
 static const unsigned regs[]={0,4,16};
 for(unsigned i=0;i<3;++i){ULONG v=0xffffffff;HalReadWritePCISpace(1,0,regs[i],&v,4,FALSE);s->pci[i]=v;}
 if(s->pci[0]!=0x02a010de || !(s->pci[1]&2) || (s->pci[2]&~8u)!=0xfd000000)return;
 for(unsigned i=0;i<19;++i)s->mm[i]=VIDEOREG(offsets827[i]);
 static const unsigned char idx[]={0x13,0x19,0x25,0x28};
 unsigned char old=VIDEOREG8(0x6013d4);s->selector_before=old;
 for(unsigned i=0;i<4;++i){VIDEOREG8(0x6013d4)=idx[i];s->cr[i]=VIDEOREG8(0x6013d5);}
 VIDEOREG8(0x6013d4)=old;s->selector_after=VIDEOREG8(0x6013d4);
 s->accepted=s->selector_before==s->selector_after;
}
int main(void)
{
 struct sample827 s={0};sample827(&s);
 if(!prepare_e()){HalReturnToFirmware(HalRebootRoutine);return 1;}
 append("{\n  \"schema\":1,\"tool\":\"xwn-entry-layout827\",\n  \"pci\":[%lu,%lu,%lu],\n",(unsigned long)s.pci[0],(unsigned long)s.pci[1],(unsigned long)s.pci[2]);
 append("  \"registers\":[");
 for(unsigned i=0;i<19;++i)append("%s[%u,%lu]",i?",":"",offsets827[i],(unsigned long)s.mm[i]);
 append("],\n  \"cr13_19_25_28\":[%lu,%lu,%lu,%lu],\n",(unsigned long)s.cr[0],(unsigned long)s.cr[1],(unsigned long)s.cr[2],(unsigned long)s.cr[3]);
 append("  \"selector_before\":%lu,\"selector_after\":%lu,\"sample_accepted\":%s,\n",(unsigned long)s.selector_before,(unsigned long)s.selector_after,s.accepted?"true":"false");
 append("  \"phase\":\"entry_sample\",\"mode_selected\":false,\"native_transition\":false,\"Windows\":false,\"complete\":true\n}\n");
 char path[64];int saved=overflow?6:save_report(path,sizeof(path));
 HalReturnToFirmware(HalRebootRoutine);return saved;
}
