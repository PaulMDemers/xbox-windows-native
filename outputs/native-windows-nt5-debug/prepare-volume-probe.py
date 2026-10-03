"""Generate the read-only installed-volume diagnostic from the saved fixture."""
import hashlib,json,pathlib,subprocess
out=pathlib.Path(__file__).resolve().parent
s=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos')
files=out.parent/'native-windows-nt5/installed-files'
selected=['boot.ini','WINNT/system32/ntoskrnl.exe','WINNT/system32/hal.dll','WINNT/system32/bootvid.dll','WINNT/system32/config/system','WINNT/system32/drivers/atapi.sys','WINNT/system32/drivers/disk.sys','WINNT/system32/drivers/ntfs.sys']
actual={str(p.relative_to(files)).lower():p for p in files.rglob('*') if p.is_file()}
entries=[]
for name in selected:
 data=actual[name.lower()].read_bytes();fnv=2166136261
 for b in data:fnv=((fnv^b)*16777619)&0xffffffff
 tail=2166136261
 for b in data[-7:]:tail=((tail^b)*16777619)&0xffffffff
 entries.append({'path':name,'bytes':len(data),'fnv1a32':fnv,'last7_fnv1a32':tail,'sha256':hashlib.sha256(data).hexdigest()})
(out/'volume-expected-files.json').write_text(json.dumps(entries,indent=2)+'\n')
header=r'''/* Generated task-local read-only Xbox NTFS fixture probe. GPL-2.0-or-later. */
#pragma once
typedef struct { PCSTR Path; ULONG Size; ULONG Hash; ULONG TailHash; } XWN_VOLUME_FILE;
static const XWN_VOLUME_FILE XwnVolumeFiles[] = {
'''
for e in entries:header+='    {"'+e['path'].replace('/','\\\\')+'", '+str(e['bytes'])+', '+hex(e['fnv1a32'])+', '+hex(e['last7_fnv1a32'])+'},\n'
header+=r'''};
static VOID XwnVerifyInstalledVolume(VOID)
{
    CHAR Path[MAX_PATH];
    UCHAR Buffer[4096];
    ULONG Id, Read, Index, File, Total, Hash;
    ARC_STATUS Status;
    FILEINFORMATION Info;
    LARGE_INTEGER Seek;
    printf("XWN90: Checking installed NTFS volume, partition(1)\n");
    for (File = 0; File < RTL_NUMBER_OF(XwnVolumeFiles); ++File)
    {
        const XWN_VOLUME_FILE *Expected = &XwnVolumeFiles[File];
        RtlStringCbPrintfA(Path, sizeof(Path), "multi(0)disk(0)rdisk(0)partition(1)\\%s", Expected->Path);
        Status = ArcOpen(Path, OpenReadOnly, &Id);
        if (Status != ESUCCESS)
        {
            printf("XWNVFAIL: file=%lu open=%lu\n", File, Status);
            XwnStop("XWNVFAIL: Installed file cannot be opened");
        }
        Status = ArcGetFileInformation(Id, &Info);
        if (Status != ESUCCESS || Info.EndingAddress.QuadPart != Expected->Size)
        {
            ArcClose(Id);
            printf("XWNVFAIL: file=%lu expected-size=%lu\n", File, Expected->Size);
            XwnStop("XWNVFAIL: Installed file size mismatch");
        }
        Status = ArcRead(Id, Buffer, 0, &Read);
        if (Status != ESUCCESS || Read != 0)
        {
            ArcClose(Id);
            XwnStop("XWNVFAIL: Zero-length read failed");
        }
        Total = 0; Hash = 2166136261u;
        while (Total < Expected->Size)
        {
            ULONG Wanted = min(sizeof(Buffer), Expected->Size - Total);
            Status = ArcRead(Id, Buffer, Wanted, &Read);
            if (Status != ESUCCESS || Read != Wanted)
            {
                ArcClose(Id);
                printf("XWNVFAIL: file=%lu offset=%lu read=%lu status=%lu\n", File, Total, Read, Status);
                XwnStop("XWNVFAIL: Installed file read failure");
            }
            for (Index = 0; Index < Read; ++Index) Hash = (Hash ^ Buffer[Index]) * 16777619u;
            Total += Read;
        }
        Status = ArcRead(Id, Buffer, 1, &Read);
        if (Status != ESUCCESS || Read != 0 || Hash != Expected->Hash)
        {
            ArcClose(Id);
            printf("XWNVFAIL: file=%lu hash=%08lx expected=%08lx\n", File, Hash, Expected->Hash);
            XwnStop("XWNVFAIL: Installed file content or EOF mismatch");
        }
        Seek.QuadPart = Expected->Size - 7;
        Status = ArcSeek(Id, &Seek, SeekAbsolute);
        if (Status != ESUCCESS)
        {
            ArcClose(Id);
            XwnStop("XWNVFAIL: Tail seek failed");
        }
        Status = ArcRead(Id, Buffer, 32, &Read);
        if (Status != ESUCCESS || Read != 7)
        {
            ArcClose(Id);
            XwnStop("XWNVFAIL: Read beyond logical EOF was not shortened");
        }
        Hash = 2166136261u;
        for (Index = 0; Index < 7; ++Index) Hash = (Hash ^ Buffer[Index]) * 16777619u;
        Status = ArcRead(Id, Buffer, 1, &Read);
        ArcClose(Id);
        if (Status != ESUCCESS || Read != 0 || Hash != Expected->TailHash)
            XwnStop("XWNVFAIL: Tail bytes or repeated EOF mismatch");
        printf("XWN91: file=%lu bytes=%lu content/zero/short/EOF OK\n", File, Total);
    }
    XwnStop("XWN98: Eight installed files verified. Windows NOT entered.");
}
'''
p=s/'boot/freeldr/freeldr/include/xwnvolume.h';p.write_text(header)
b=s/'boot/freeldr/freeldr/bootmgr.c';t=b.read_text()
if '#include <xwnvolume.h>' not in t:t=t.replace('#include <xwnprobe.h>','#include <xwnprobe.h>\n#ifdef XBOX_NATIVE_VOLUME_PREFLIGHT\n#include <xwnvolume.h>\n#endif')
if '    XwnVerifyInstalledVolume();' not in t:t=t.replace('    XwnStop("XWN80:', '#ifdef XBOX_NATIVE_VOLUME_PREFLIGHT\n    XwnVerifyInstalledVolume();\n#endif\n    XwnStop("XWN80:')
b.write_text(t)
p=s/'boot/freeldr/freeldr/pcat.cmake';t=p.read_text()
if 'option(XBOX_NATIVE_VOLUME_PREFLIGHT' not in t:t+='\noption(XBOX_NATIVE_VOLUME_PREFLIGHT "Read and verify the private installed Windows NTFS fixture, then halt" OFF)\nif(XBOX_NATIVE_VOLUME_PREFLIGHT AND NOT XBOX_NATIVE_IO_PREFLIGHT)\n    message(FATAL_ERROR "Volume preflight requires the IO preflight")\nendif()\n'
p.write_text(t)
p=s/'boot/freeldr/freeldr/rosload.cmake';t=p.read_text()
if 'if(XBOX_NATIVE_VOLUME_PREFLIGHT)' not in t:t+='\nif(XBOX_NATIVE_VOLUME_PREFLIGHT)\n    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_VOLUME_PREFLIGHT=1)\nendif()\n'
p.write_text(t)
subprocess.run(['git','add','-N','boot/freeldr/freeldr/include/xwnvolume.h'],cwd=s,check=True)
print('Prepared',len(entries),'read-only file expectations')
