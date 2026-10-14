/* Task-local Xbox CD/second-stage diagnostic. GPL-2.0-or-later. */
#pragma once

static VOID XwnStop(PCSTR Message)
{
    printf("%s\n", Message);
    _disable();
    for (;;) __halt();
}

static BOOLEAN XwnVerifyFile(VOID)
{
    CHAR Path[MAX_PATH];
    UCHAR Buffer[1024];
    ULONG FileId, Read, Offset = 0, Index, Wanted;
    FILEINFORMATION Info;
    LARGE_INTEGER Seek;
    ARC_STATUS Status;
    BOOLEAN Good = FALSE;
    RtlStringCbPrintfA(Path, sizeof(Path), "%s\\probe.bin", FrLdrGetBootPath());
    Status = ArcOpen(Path, OpenReadOnly, &FileId);
    if (Status != ESUCCESS)
    {
        printf("XWNFAIL: probe open status=%lu\n", Status);
        return FALSE;
    }
    Status = ArcGetFileInformation(FileId, &Info);
    if (Status != ESUCCESS || Info.EndingAddress.QuadPart != 131075)
        goto Done;
    while (Offset < 131075)
    {
        Wanted = min(sizeof(Buffer), 131075 - Offset);
        Status = ArcRead(FileId, Buffer, Wanted, &Read);
        if (Status != ESUCCESS || Read != Wanted) goto Done;
        for (Index = 0; Index < Read; ++Index)
            if (Buffer[Index] != (UCHAR)((Offset + Index) * 37 + ((Offset + Index) >> 8) + 0x5a))
                goto Done;
        Offset += Read;
    }
    Status = ArcRead(FileId, Buffer, 1, &Read);
    if (Status != ESUCCESS || Read != 0) goto Done;
    Seek.QuadPart = 2041;
    Status = ArcSeek(FileId, &Seek, SeekAbsolute);
    if (Status != ESUCCESS) goto Done;
    Status = ArcRead(FileId, Buffer, 31, &Read);
    if (Status != ESUCCESS || Read != 31) goto Done;
    for (Index = 0; Index < Read; ++Index)
        if (Buffer[Index] != (UCHAR)((2041 + Index) * 37 + ((2041 + Index) >> 8) + 0x5a))
            goto Done;
    Good = TRUE;
Done:
    ArcClose(FileId);
    if (!Good) printf("XWNFAIL: file data/size/seek/EOF offset=%lu status=%lu\n", Offset, Status);
    return Good;
}
