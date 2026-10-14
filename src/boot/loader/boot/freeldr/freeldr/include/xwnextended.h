/* SPDX-License-Identifier: GPL-2.0-or-later */
#pragma once
/* Opt-in owned-emulator fixture test. No writes and no kernel entry. */
static BOOLEAN XwnVerifyExtendedFile(VOID)
{
    CHAR Path[MAX_PATH];
    UCHAR Buffer[1024];
    ULONG FileId, Read, Offset = 0, Index, Wanted;
    FILEINFORMATION Info;
    LARGE_INTEGER Seek;
    ARC_STATUS Status;
    BOOLEAN Good = FALSE;
    RtlStringCbCopyA(Path, sizeof(Path), "multi(0)disk(0)rdisk(0)partition(6)\\xwn-high.bin");
    Status = ArcOpen(Path, OpenReadOnly, &FileId);
    if (Status != ESUCCESS)
    {
        printf("XWNFAIL: probe open status=%lu\n", Status);
        return FALSE;
    }
    Status = ArcGetFileInformation(FileId, &Info);
    if (Status != ESUCCESS || Info.EndingAddress.QuadPart != 4097)
        goto Done;
    while (Offset < 4097)
    {
        Wanted = min(sizeof(Buffer), 4097 - Offset);
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

static VOID XwnExtendedReadPreflight(VOID)
{
    if (!XwnVerifyExtendedFile()) XwnStop("XWNFAIL: high-LBA F file");
    XwnStop("XWNF90: F high-LBA file/size/seek/EOF verified. Windows NOT entered.");
}
