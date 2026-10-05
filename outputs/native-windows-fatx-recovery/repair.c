/* SPDX-License-Identifier: MIT
 * Bounded exact-preimage directory sector repair. Reports are beside this XBE on E:.
 * No FAT-table, partition-geometry or ATA writes; only pinned plan sectors.
 */
#include <hal/debug.h>
#include <hal/video.h>
#include <hal/xbox.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <stdlib.h>

static HANDLE disk, logf;
static BYTE *buf;
static unsigned long long length, data_offset;




static int failed;

static void report(const char *fmt, ...) {
    char s[512]; DWORD n; va_list a; va_start(a,fmt);
    int len=vsnprintf(s,sizeof(s),fmt,a);va_end(a);
    if(len<0 || len>=(int)sizeof(s) || !WriteFile(logf,s,len,&n,NULL) || n!=(DWORD)len)failed=1;
}
static int flush(HANDLE h) {IO_STATUS_BLOCK io;return NT_SUCCESS(NtFlushBuffersFile(h,&io));}
static int read_at(unsigned long long offset, ULONG bytes, void *out) {
    LARGE_INTEGER at;IO_STATUS_BLOCK io={0};NTSTATUS s;
    if(offset>length || bytes>length-offset || (offset&511) || (bytes&511))return 0;
    at.QuadPart=offset;
    s=NtReadFile(disk,NULL,NULL,NULL,&io,out,bytes,&at);
    if(s==STATUS_PENDING){s=NtWaitForSingleObject(disk,FALSE,NULL);if(NT_SUCCESS(s))s=io.Status;}
    if(!NT_SUCCESS(s)||io.Information!=bytes){report("READ_FAIL offset=%llu bytes=%lu status=%08lx got=%lu\r\n",offset,bytes,(ULONG)s,io.Information);failed=1;return 0;}
    return 1;
}

static int read_file(const char *path,BYTE **data,DWORD *size,DWORD maximum) {
 HANDLE f=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);DWORD n;
 if(f==INVALID_HANDLE_VALUE)return 0;
 *size=GetFileSize(f,NULL);*data=NULL;
 if(*size==0 || *size>maximum){CloseHandle(f);return 0;}
 *data=malloc(*size);int ok=*data&&ReadFile(f,*data,*size,&n,NULL)&&n==*size;
 CloseHandle(f);return ok;
}
static int snapshot(void) {
 ANSI_STRING name;OBJECT_ATTRIBUTES attrs;IO_STATUS_BLOCK io={0};PARTITION_INFORMATION part={0};NTSTATUS s;DWORD n;
 BYTE *plan=NULL,*expected=NULL;DWORD size=0,nrecords;int ok=0;
 if(!read_file("D:\\plan.bin",&plan,&size,20+16*1032))goto done;
 if(size<20||memcmp(plan,"XWN-FIX-0001\0\0\0\0",16))goto done;
 memcpy(&nrecords,plan+16,4);if(!nrecords||nrecords>16||size!=20+nrecords*1032)goto done;
 RtlInitAnsiString(&name,"\\Device\\Harddisk0\\Partition6");InitializeObjectAttributes(&attrs,&name,OBJ_CASE_INSENSITIVE,NULL,NULL);
 s=NtOpenFile(&disk,GENERIC_READ|GENERIC_WRITE|SYNCHRONIZE,&attrs,&io,FILE_SHARE_READ|FILE_SHARE_WRITE,FILE_SYNCHRONOUS_IO_NONALERT|FILE_NO_INTERMEDIATE_BUFFERING);
 if(!NT_SUCCESS(s))goto done;
 s=NtDeviceIoControlFile(disk,NULL,NULL,NULL,&io,IOCTL_DISK_GET_PARTITION_INFO,NULL,0,&part,sizeof(part));
 if(s==STATUS_PENDING){s=NtWaitForSingleObject(disk,FALSE,NULL);if(NT_SUCCESS(s))s=io.Status;}
 if(!NT_SUCCESS(s)||io.Information<sizeof(part))goto done;
 length=part.PartitionLength.QuadPart;
 if(part.StartingOffset.QuadPart!=15633072ULL*512||(length!=472764096ULL*512&&length!=129434820096ULL))goto done;
 data_offset=14778368;
 HANDLE meta=CreateFileA("D:\\fat-before.bin",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);
 if(meta==INVALID_HANDLE_VALUE)goto done;
 expected=malloc(65536);ok=expected&&GetFileSize(meta,NULL)==data_offset;
 for(unsigned long long at=0;ok&&at<data_offset;at+=65536) {
  DWORD bytes=(DWORD)(data_offset-at<65536?data_offset-at:65536);
  ok=ReadFile(meta,expected,bytes,&n,NULL)&&n==bytes&&read_at(at,bytes,buf)&&!memcmp(buf,expected,bytes);
 }
 CloseHandle(meta);if(!ok)goto done;ok=0;
 /* Validate every target before any write, including targets from a partial run. */
 for(ULONG i=0;i<nrecords;i++) {
  BYTE *r=plan+20+i*1032;unsigned long long at;memcpy(&at,r,8);
  if(at<data_offset||at>length-512||(at&511))goto done;
  for(ULONG j=0;j<i;j++){unsigned long long other;memcpy(&other,plan+20+j*1032,8);if(at==other)goto done;}
  if(!read_at(at,512,buf)||(memcmp(buf,r+8,512)&&memcmp(buf,r+520,512)))goto done;
 }
 report("ALL_PREIMAGES_VERIFIED sectors=%lu\r\n",nrecords);
 if(!flush(logf)||failed)goto done;
 for(ULONG i=0;i<nrecords;i++) {
  BYTE *r=plan+20+i*1032;LARGE_INTEGER at;memcpy(&at.QuadPart,r,8);
  if(!read_at(at.QuadPart,512,buf))goto done;
  if(!memcmp(buf,r+520,512)){report("ALREADY_APPLIED sector=%lu\r\n",i);continue;}
  if(memcmp(buf,r+8,512))goto done;
  memcpy(buf,r+520,512);io.Status=0;io.Information=0;
  s=NtWriteFile(disk,NULL,NULL,NULL,&io,buf,512,&at);
  if(s==STATUS_PENDING){s=NtWaitForSingleObject(disk,FALSE,NULL);if(NT_SUCCESS(s))s=io.Status;}
  if(!NT_SUCCESS(s)||io.Information!=512||!flush(disk))goto done;
  if(!read_at(at.QuadPart,512,buf)||memcmp(buf,r+520,512))goto done;
  report("APPLIED sector=%lu offset=%llu\r\n",i,(unsigned long long)at.QuadPart);
  if(!flush(logf)||failed)goto done;
 }
 ok=1;
done:free(plan);free(expected);return ok&&!failed;
}
int main(void) {
 XVideoSetMode(640,480,32,REFRESH_DEFAULT);debugPrint("XWN bounded FATX directory repair\nVerifying exact plan before any write.\n");
 disk=INVALID_HANDLE_VALUE;logf=CreateFileA("D:\\repair.txt",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 if(logf==INVALID_HANDLE_VALUE){debugPrint("Existing report; stopped.\n");Sleep(3000);XReboot();return 1;}
 buf=MmAllocateContiguousMemory(65536);
 report("XWN-FAT-REPAIR-001\r\n");int ok=buf&&snapshot();
 report("REPAIR_COMPLETE success=%d\r\n",ok);flush(logf);CloseHandle(logf);
 if(disk!=INVALID_HANDLE_VALUE)NtClose(disk);if(buf)MmFreeContiguousMemory(buf);
 debugPrint("Repair %s; independent rescan required.\n",ok?"complete":"stopped");Sleep(3000);XReboot();return 0;
}
