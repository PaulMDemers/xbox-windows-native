/* SPDX-License-Identifier: GPL-2.0-or-later
 * Bounded parser for the Xbox LBA48 PARTINFO format. No disk I/O or writes.
 * Format reference: NKPatcher lba48.inc and xa_lba48.asm (see REFERENCES.txt).
 */
#ifndef XWN_XBOXPART_H
#define XWN_XBOXPART_H

typedef struct XWN_XBOX_PARTITION
{
    unsigned int Start;
    unsigned int Count;
} XWN_XBOX_PARTITION;

#define XWN_XBOX_MAX_PARTITIONS 14
#define XWN_XBOX_TABLE_ABSENT 0
#define XWN_XBOX_TABLE_VALID 1
#define XWN_XBOX_TABLE_INVALID (-1)

static unsigned int XwnXboxReadU32(const unsigned char *p)
{
    return (unsigned int)p[0] | ((unsigned int)p[1] << 8) |
           ((unsigned int)p[2] << 16) | ((unsigned int)p[3] << 24);
}

/* Output is usable only on TABLE_VALID. Reject unknown extensions, holes,
 * overflow, overlap and out-of-disk extents; never fall back after bad magic-
 * bearing metadata. Sector count must come from the device, not this table.
 */
static int XwnXboxParsePartitionTable(const unsigned char *sector,
    unsigned int bytes, unsigned long long diskSectors,
    XWN_XBOX_PARTITION *parts, unsigned int *partCount)
{
    static const char magic[] = "****PARTINFO****";
    unsigned int i, j, active = 0;
    int gap = 0;
    *partCount = 0;
    if (bytes < 16) return XWN_XBOX_TABLE_INVALID;
    for (i = 0; i < 16; ++i)
        if (sector[i] != (unsigned char)magic[i]) return XWN_XBOX_TABLE_ABSENT;
    if (bytes != 512 || !diskSectors) return XWN_XBOX_TABLE_INVALID;
    for (i = 16; i < 48; ++i)
        if (sector[i]) return XWN_XBOX_TABLE_INVALID;
    for (i = 496; i < 512; ++i)
        if (sector[i]) return XWN_XBOX_TABLE_INVALID;
    for (i = 0; i < XWN_XBOX_MAX_PARTITIONS; ++i)
    {
        const unsigned char *entry = sector + 48 + i * 32;
        unsigned int flags = XwnXboxReadU32(entry + 16);
        unsigned int start = XwnXboxReadU32(entry + 20);
        unsigned int count = XwnXboxReadU32(entry + 24);
        parts[i].Start = parts[i].Count = 0;
        if (XwnXboxReadU32(entry + 28) || (flags & ~0x80000000U))
            return XWN_XBOX_TABLE_INVALID;
        if (!(flags & 0x80000000U))
        {
            gap = 1;
            continue;
        }
        if (gap || start < 1024 || !count ||
            (unsigned long long)start >= diskSectors ||
            (unsigned long long)count > diskSectors - start)
            return XWN_XBOX_TABLE_INVALID;
        for (j = 0; j < i; ++j)
            if ((unsigned long long)start < (unsigned long long)parts[j].Start + parts[j].Count &&
                (unsigned long long)parts[j].Start < (unsigned long long)start + count)
                return XWN_XBOX_TABLE_INVALID;
        parts[i].Start = start;
        parts[i].Count = count;
        active = i + 1;
    }
    /* Existing Xbox volumes must remain represented; optional F/G follow. */
    if (active < 5) return XWN_XBOX_TABLE_INVALID;
    *partCount = active;
    return XWN_XBOX_TABLE_VALID;
}
#endif
