/* Generated task-local read-only Xbox NTFS fixture probe. GPL-2.0-or-later. */
#pragma once
typedef struct { PCSTR Path; ULONG Size; ULONG Hash; ULONG TailHash; } XWN_VOLUME_FILE;
static const XWN_VOLUME_FILE XwnVolumeFiles[] = {
    {"boot.ini", 192, 0x803c3af4, 0xfe79cdc3},
    {"WINNT\\system32\\ntoskrnl.exe", 1691648, 0xc10df1a4, 0x462a7c27},
    {"WINNT\\system32\\hal.dll", 93536, 0x3c18fa59, 0x462a7c27},
    {"WINNT\\system32\\bootvid.dll", 10784, 0xda5286e6, 0x462a7c27},
    {"WINNT\\system32\\config\\system", 1810432, 0x1023cd18, 0x462a7c27},
    {"WINNT\\system32\\drivers\\atapi.sys", 88048, 0x8147907, 0x462a7c27},
    {"WINNT\\system32\\drivers\\disk.sys", 30864, 0xf9508b79, 0x462a7c27},
    {"WINNT\\system32\\drivers\\ntfs.sys", 513456, 0xfb86d4a2, 0x462a7c27},
};
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
