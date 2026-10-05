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

static HANDLE disk, logf;
static BYTE *buf, *fatbuf;
static unsigned long long length, data_offset;
static ULONG count, saved[512], saved_count;
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
static int save_cluster(ULONG c) {
    DWORD wrote;char name[80];HANDLE out;
    if(c<1 || c>=count || data_offset+(unsigned long long)c*65536>length)return 0;
    if(!read_at(data_offset+(unsigned long long)(c-1)*65536,65536,buf))return 0;
    for(ULONG i=0;i<saved_count;i++)if(saved[i]==c)return 1;
    if(saved_count>=512)return 0;
    snprintf(name,sizeof(name),"D:\\cluster-%08lx.bin",c);
    out=CreateFileA(name,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(out==INVALID_HANDLE_VALUE)return 0;
    int ok=WriteFile(out,buf,65536,&wrote,NULL)&&wrote==65536&&flush(out);CloseHandle(out);
    if(ok)saved[saved_count++]=c;return ok;
}
static int next_cluster(ULONG c, ULONG *next) {
    unsigned long long at=4096+(unsigned long long)c*4;
    if(c>=count || !read_at(at&~511ULL,512,fatbuf))return 0;
    memcpy(next,fatbuf+(at&511),4);return 1;
}
static int equal_name(const BYTE *e,const char *name) {
    unsigned n=strlen(name);if(e[0]!=n || n>42)return 0;
    for(unsigned i=0;i<n;i++){unsigned a=e[2+i],b=(unsigned char)name[i];if(a>='A'&&a<='Z')a+=32;if(b>='A'&&b<='Z')b+=32;if(a!=b)return 0;}
    return 1;
}
static int lookup(ULONG dir,const char *name,ULONG *first,ULONG *size) {
    ULONG c=dir,seen[64],n=0,next;
    while(c>=1 && c<count && n<64) {
        for(ULONG i=0;i<n;i++)if(seen[i]==c)return 0;seen[n++]=c;
        if(!save_cluster(c))return 0;
        for(unsigned off=0;off<65536;off+=64) {
            BYTE *e=buf+off;
            if(e[0]==0 || e[0]==255)return 0;
            if(e[0]<=42 && equal_name(e,name)) {
                memcpy(first,e+44,4);memcpy(size,e+48,4);
                report("ENTRY parent=%lu cluster=%lu offset=%u name=%s first=%lu size=%lu attributes=%02x\r\n",dir,c,off,name,*first,*size,e[1]);
                return 1;
            }
        }
        if(!next_cluster(c,&next))return 0;c=next;
    }
    return 0;
}
static void chain(ULONG first,ULONG size,const char *name) {
    ULONG c=first,seen[64],n=0,next;
    report("CHAIN name=%s first=%lu expected_bytes=%lu\r\n",name,first,size);
    while(c>=1 && c<count && n<64) {
        for(ULONG i=0;i<n;i++)if(seen[i]==c){report("CHAIN_LOOP %lu\r\n",c);return;}seen[n++]=c;
        if(!next_cluster(c,&next)||!save_cluster(c)){failed=1;return;}
        report("LINK cluster=%lu next=%08lx\r\n",c,next);c=next;
    }
    report("CHAIN_END clusters=%lu marker=%08lx bytes_capacity=%llu\r\n",n,c,(unsigned long long)n*65536);
}
static int snapshot(void) {
    ANSI_STRING name;OBJECT_ATTRIBUTES attrs;IO_STATUS_BLOCK io={0};PARTITION_INFORMATION part={0};NTSTATUS s;DWORD wrote;
    RtlInitAnsiString(&name,"\\Device\\Harddisk0\\Partition6");
    InitializeObjectAttributes(&attrs,&name,OBJ_CASE_INSENSITIVE,NULL,NULL);
    s=NtOpenFile(&disk,GENERIC_READ|SYNCHRONIZE,&attrs,&io,FILE_SHARE_READ|FILE_SHARE_WRITE,FILE_SYNCHRONOUS_IO_NONALERT|FILE_NO_INTERMEDIATE_BUFFERING);
    if(!NT_SUCCESS(s)){report("OPEN_FAIL %08lx\r\n",(ULONG)s);return 0;}
    s=NtDeviceIoControlFile(disk,NULL,NULL,NULL,&io,IOCTL_DISK_GET_PARTITION_INFO,NULL,0,&part,sizeof(part));
    if(s==STATUS_PENDING){s=NtWaitForSingleObject(disk,FALSE,NULL);if(NT_SUCCESS(s))s=io.Status;}
    if(!NT_SUCCESS(s)||io.Information<sizeof(part))return 0;
    length=part.PartitionLength.QuadPart;
    report("PARTITION start=%llu length=%llu\r\n",(unsigned long long)part.StartingOffset.QuadPart,length);
    /* The owned emulator's Xbox BIOS exposes only the LBA28 prefix of the
     * same 250-GB FATX fixture. Permit that exact prefix for validation,
     * while read_at still enforces the actual handle's reported bound.
     * FAT geometry comes from the pinned full-volume layout in both cases. */
    if(part.StartingOffset.QuadPart!=15633072ULL*512 ||
       (length!=472764096ULL*512 && length!=129434820096ULL))return 0;
    if(!read_at(0,4096,buf))return 0;
    ULONG magic,spc,root;memcpy(&magic,buf,4);memcpy(&spc,buf+8,4);memcpy(&root,buf+12,4);
    if(magic!=0x58544146 || spc!=128 || root!=1)return 0;
    count=(472764096ULL*512)/65536;data_offset=4096+(((unsigned long long)count*4+4095)&~4095ULL);
    report("FATX clusters=%lu fat_bytes=%llu data_offset=%llu\r\n",count,data_offset-4096,data_offset);
    HANDLE meta=CreateFileA("D:\\fat-metadata.bin",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(meta==INVALID_HANDLE_VALUE)return 0;
    int ok=1;
    for(unsigned long long at=0;at<data_offset;at+=65536) {
        ULONG bytes=(ULONG)(data_offset-at<65536?data_offset-at:65536);
        if(!read_at(at,bytes,buf)||!WriteFile(meta,buf,bytes,&wrote,NULL)||wrote!=bytes){ok=0;break;}
    }
    ok=flush(meta)&&ok;CloseHandle(meta);if(!ok)return 0;
    ULONG winnt,system,drivers,wbem,repo,c,size;
    if(!lookup(1,"winnt",&winnt,&size)||!lookup(winnt,"system32",&system,&size))return 0;
    if(!lookup(system,"drivers",&drivers,&size)||!lookup(drivers,"xwnfatx.sys",&c,&size))return 0;
    chain(c,size,"xwnfatx.sys");
    if(!lookup(system,"wbem",&wbem,&size)||!lookup(wbem,"repository",&repo,&size)||!lookup(repo,"cim.rep",&c,&size))return 0;
    chain(c,size,"CIM.REP");
    return !failed;
}
int main(void) {
    XVideoSetMode(640,480,32,REFRESH_DEFAULT);debugPrint("XWN FATX read-only snapshot\nReport files go beside this app.\n");
    disk=INVALID_HANDLE_VALUE;logf=CreateFileA("D:\\snapshot.txt",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(logf==INVALID_HANDLE_VALUE){debugPrint("Existing report or unwritable app folder; stopped.\n");Sleep(3000);XReboot();return 1;}
    buf=MmAllocateContiguousMemory(65536);fatbuf=MmAllocateContiguousMemory(4096);
    report("XWN-FAT-READONLY-013\r\n");int ok=buf&&fatbuf&&snapshot();
    report("SNAPSHOT_COMPLETE success=%d files=%lu\r\n",ok,saved_count);flush(logf);CloseHandle(logf);
    if(disk!=INVALID_HANDLE_VALUE)NtClose(disk);if(buf)MmFreeContiguousMemory(buf);if(fatbuf)MmFreeContiguousMemory(fatbuf);
    debugPrint("Snapshot %s. Returning to dashboard.\n",ok?"complete":"incomplete");Sleep(3000);XReboot();return 0;
}
