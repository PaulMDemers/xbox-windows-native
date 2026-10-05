/* SPDX-License-Identifier: MIT
 * Read-only Partition6 snapshot. All output files are beside this XBE on E:.
 * No raw device write handle, repair, ATA command, or partition modification.
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
static BYTE *buf, *fatbuf;
static unsigned long long length, data_offset;
static ULONG count, requested[1024], requested_count;
static ULONG *fat;

static HANDLE records;
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
static int snapshot(void) {
 ANSI_STRING name;OBJECT_ATTRIBUTES attrs;IO_STATUS_BLOCK io={0};PARTITION_INFORMATION part={0};NTSTATUS s;DWORD n;
 RtlInitAnsiString(&name,"\\Device\\Harddisk0\\Partition6");InitializeObjectAttributes(&attrs,&name,OBJ_CASE_INSENSITIVE,NULL,NULL);
 s=NtOpenFile(&disk,GENERIC_READ|SYNCHRONIZE,&attrs,&io,FILE_SHARE_READ|FILE_SHARE_WRITE,FILE_SYNCHRONOUS_IO_NONALERT|FILE_NO_INTERMEDIATE_BUFFERING);
 if(!NT_SUCCESS(s))return 0;
 s=NtDeviceIoControlFile(disk,NULL,NULL,NULL,&io,IOCTL_DISK_GET_PARTITION_INFO,NULL,0,&part,sizeof(part));
 if(s==STATUS_PENDING){s=NtWaitForSingleObject(disk,FALSE,NULL);if(NT_SUCCESS(s))s=io.Status;}
 if(!NT_SUCCESS(s)||io.Information<sizeof(part))return 0;
 length=part.PartitionLength.QuadPart;report("PARTITION start=%llu length=%llu\r\n",(unsigned long long)part.StartingOffset.QuadPart,length);
 if(part.StartingOffset.QuadPart!=15633072ULL*512 || (length!=472764096ULL*512 && length!=129434820096ULL))return 0;
 if(!read_at(0,4096,buf))return 0;
 ULONG magic,spc,root;memcpy(&magic,buf,4);memcpy(&spc,buf+8,4);memcpy(&root,buf+12,4);
 if(magic!=0x58544146||spc!=128||root!=1)return 0;
 count=(472764096ULL*512)/65536;data_offset=4096+(((unsigned long long)count*4+4095)&~4095ULL);
 HANDLE request=CreateFileA("D:\\clusters.bin",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);
 if(request==INVALID_HANDLE_VALUE)return 0;
 DWORD bytes=GetFileSize(request,NULL);
 int valid=bytes>0 && bytes<=sizeof(requested) && !(bytes&3) && ReadFile(request,requested,bytes,&n,NULL) && n==bytes;
 CloseHandle(request);if(!valid)return 0;requested_count=bytes/4;
 for(ULONG i=0;i<requested_count;i++) {
  if(requested[i]<1 || requested[i]>=count)return 0;
  for(ULONG j=0;j<i;j++)if(requested[i]==requested[j])return 0;
 }
 HANDLE meta=CreateFileA("D:\\fat-metadata.bin",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 if(meta==INVALID_HANDLE_VALUE)return 0;
 int ok=WriteFile(meta,buf,4096,&n,NULL)&&n==4096;
 for(unsigned long long at=4096;ok && at<data_offset;at+=65536) {
  ULONG bytes=(ULONG)(data_offset-at<65536?data_offset-at:65536);
  if(!read_at(at,bytes,buf)){ok=0;break;}

  if(!WriteFile(meta,buf,bytes,&n,NULL)||n!=bytes)ok=0;
 }
 ok=flush(meta)&&ok;CloseHandle(meta);if(!ok)return 0;
 records=CreateFileA("D:\\cluster-data.bin",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 if(records==INVALID_HANDLE_VALUE)return 0;
 for(ULONG i=0;i<requested_count;i++) {
  ULONG c=requested[i];
  if(!read_at(data_offset+(unsigned long long)(c-1)*65536,65536,buf) ||
     !WriteFile(records,&c,4,&n,NULL)||n!=4 ||
     !WriteFile(records,buf,65536,&n,NULL)||n!=65536){ok=0;break;}
 }
 ok=flush(records)&&ok;CloseHandle(records);return ok&&!failed;
}
int main(void) {
 XVideoSetMode(640,480,32,REFRESH_DEFAULT);debugPrint("XWN targeted read-only recovery backup\nReading F; reports beside this app on E.\n");
 disk=INVALID_HANDLE_VALUE;logf=CreateFileA("D:\\snapshot.txt",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
 if(logf==INVALID_HANDLE_VALUE){debugPrint("Existing report or unwritable folder; stopped.\n");Sleep(3000);XReboot();return 1;}
 buf=MmAllocateContiguousMemory(65536);fatbuf=NULL;
 report("XWN-FAT-BACKUP-001\r\n");int ok=buf&&snapshot();
 report("SNAPSHOT_COMPLETE success=%d requested_clusters=%lu\r\n",ok,requested_count);flush(logf);CloseHandle(logf);
 if(disk!=INVALID_HANDLE_VALUE)NtClose(disk);if(buf)MmFreeContiguousMemory(buf);
 debugPrint("Capture %s. This does not mean the filesystem is healthy.\n",ok?"complete":"incomplete");Sleep(3000);XReboot();return 0;
}
