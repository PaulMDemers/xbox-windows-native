from pathlib import Path
p=Path('/home/paul/xbox-windows-native/sources/reactos-extended/hal/halx86/xbox/part_xbox.c')
s=p.read_text();assert 'XwnExtendedPartitionTrace' not in s
key='/* Require an exact device length'
s=s.replace(key,'''/* Read-only debugger telemetry: magic, calls, stage, status, table status,
 * count, device length low/high, returned bytes, sector size, BRFR status. */
volatile ULONG XwnExtendedPartitionTrace[16] = {0x58575054};

'''+key,1)
s=s.replace('    *TableStatus = XWN_XBOX_TABLE_INVALID;','    XwnExtendedPartitionTrace[2] = 30;\n    *TableStatus = XWN_XBOX_TABLE_INVALID;',1)
s=s.replace('    if (!NT_SUCCESS(Status)) goto Done;\n    /* The first parse', '    XwnExtendedPartitionTrace[3] = Status;\n    if (!NT_SUCCESS(Status)) goto Done;\n    XwnExtendedPartitionTrace[2] = 35;\n    /* The first parse',1)
s=s.replace('    if (*TableStatus == XWN_XBOX_TABLE_ABSENT) goto Done;', '    XwnExtendedPartitionTrace[4] = *TableStatus;\n    if (*TableStatus == XWN_XBOX_TABLE_ABSENT) goto Done;',1)
s=s.replace('    if (!NT_SUCCESS(Status)) goto Done;\n    if (Io.Information', '''    XwnExtendedPartitionTrace[2] = 40;
    XwnExtendedPartitionTrace[3] = Status;
    XwnExtendedPartitionTrace[6] = Length.Length.LowPart;
    XwnExtendedPartitionTrace[7] = Length.Length.HighPart;
    XwnExtendedPartitionTrace[8] = Io.Information;
    if (!NT_SUCCESS(Status)) goto Done;
    if (Io.Information''',1)
s=s.replace('Done:\n    ExFreePoolWithTag(Buffer, TAG_HAL_XBOX);','''Done:
    XwnExtendedPartitionTrace[3] = Status;
    XwnExtendedPartitionTrace[4] = *TableStatus;
    XwnExtendedPartitionTrace[5] = *Count;
    ExFreePoolWithTag(Buffer, TAG_HAL_XBOX);''',1)
needle='    Status = HalpXboxDeviceHasXboxPartitioning(DeviceObject, SectorSize, &HasXboxPartitioning);'
# Instrument only partition-table routine, not the earlier examine-MBR routine.
start=s.index('HalpXboxIoReadPartitionTable(IN')
a=s[:start];b=s[start:];assert needle in b
b=b.replace(needle,'''    XwnExtendedPartitionTrace[1]++;
    XwnExtendedPartitionTrace[2] = 10;
    XwnExtendedPartitionTrace[9] = SectorSize;
'''+needle+'''
    XwnExtendedPartitionTrace[3] = Status;
    XwnExtendedPartitionTrace[10] = NT_SUCCESS(Status) ? HasXboxPartitioning : 0;''',1)
b=b.replace('    (*PartitionBuffer)->PartitionCount = PartCount;', '    XwnExtendedPartitionTrace[2] = 90;\n    (*PartitionBuffer)->PartitionCount = PartCount;',1)
p.write_text(a+b)
