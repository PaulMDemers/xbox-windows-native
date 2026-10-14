/*
 * PROJECT: Xbox NT5 HAL experiment
 * LICENSE: GPL-2.0-or-later (see ReactOS COPYING)
 * PURPOSE: Root PCI apertures for Windows 2000 resource arbitration.
 * The original empty root resource list leaves every PCI address reserved.
 * Report PNPBus resources in the native NT5 format: shared, fixed windows.
 */
#include <hal.h>

#define NT5_MAX_PORT_RANGES 64
#define NT5_ROOT_DESCRIPTORS (NT5_MAX_PORT_RANGES + 3)

NTSTATUS NTAPI
HalpNt5QueryRootResources(PCM_RESOURCE_LIST *Resources)
{
    struct { ULONG Start, End; } Reserved[NT5_MAX_PORT_RANGES], Swap;
    ULONG Used = 0, i, j, Start, End, Cursor, Count = 0, Bytes;
    PADDRESS_USAGE Usage;
    PCM_RESOURCE_LIST List;
    PCM_PARTIAL_RESOURCE_DESCRIPTOR Desc;
    if (!Resources) return STATUS_INVALID_PARAMETER;
    *Resources = NULL;
    /* Complement the HAL's actual reservations instead of advertising PIC,
       timer, CMOS, DMA, debugger or PCI configuration ports to child devices. */
    for (Usage = HalpAddressUsageList; Usage; Usage = Usage->Next)
    {
        if (Usage->Type != CmResourceTypePort) continue;
        for (i = 0; Usage->Element[i].Length; ++i)
        {
            Start = Usage->Element[i].Start;
            if (Start >= 0x10000) continue;
            if (Used == NT5_MAX_PORT_RANGES) return STATUS_INSUFFICIENT_RESOURCES;
            End = Start + min(Usage->Element[i].Length, 0x10000 - Start);
            Reserved[Used].Start = Start;
            Reserved[Used++].End = End;
        }
    }
    for (i = 1; i < Used; ++i)
    {
        Swap = Reserved[i]; j = i;
        while (j && Reserved[j - 1].Start > Swap.Start)
        {
            Reserved[j] = Reserved[j - 1]; --j;
        }
        Reserved[j] = Swap;
    }
    Bytes = FIELD_OFFSET(CM_RESOURCE_LIST, List[0].PartialResourceList.PartialDescriptors) +
            NT5_ROOT_DESCRIPTORS * sizeof(*Desc);
    List = ExAllocatePoolWithTag(PagedPool, Bytes, TAG_HAL);
    if (!List) return STATUS_INSUFFICIENT_RESOURCES;
    RtlZeroMemory(List, Bytes);
    List->Count = 1;
    List->List[0].InterfaceType = PNPBus;
    List->List[0].BusNumber = (ULONG)-1;
    List->List[0].PartialResourceList.Version = 1;
    List->List[0].PartialResourceList.Revision = 1;
    Desc = List->List[0].PartialResourceList.PartialDescriptors;
    Desc[Count].Type = CmResourceTypeBusNumber;
    Desc[Count].ShareDisposition = CmResourceShareShared;
    Desc[Count++].u.BusNumber.Length = 256;
    Cursor = 0;
    for (i = 0; i <= Used; ++i)
    {
        Start = (i == Used) ? 0x10000 : Reserved[i].Start;
        if (Start > Cursor)
        {
            Desc[Count].Type = CmResourceTypePort;
            Desc[Count].ShareDisposition = CmResourceShareShared;
            Desc[Count].Flags = CM_RESOURCE_PORT_IO;
            Desc[Count].u.Port.Start.QuadPart = Cursor;
            Desc[Count++].u.Port.Length = Start - Cursor;
        }
        if (i != Used) Cursor = max(Cursor, Reserved[i].End);
    }
    /* Xbox PCI device/bridge apertures observed in firmware configuration:
       NV2A framebuffer at F0000000, GPU at FD000000, MCP devices at FE8xxxxx
       through FEFxxxxx. Exclude RAM and the FFxxxxxx flash/firmware window. */
    Desc[Count].Type = CmResourceTypeMemory;
    Desc[Count].ShareDisposition = CmResourceShareShared;
    Desc[Count].u.Memory.Start.QuadPart = 0xf0000000ULL;
    Desc[Count++].u.Memory.Length = 0x0f000000;
    ASSERT(Count <= NT5_ROOT_DESCRIPTORS);
    List->List[0].PartialResourceList.Count = Count;
    *Resources = List;
    return STATUS_SUCCESS;
}

NTSTATUS NTAPI
HalpNt5QueryRootRequirements(PIO_RESOURCE_REQUIREMENTS_LIST *Requirements)
{
    PCM_RESOURCE_LIST Resources;
    PCM_PARTIAL_RESOURCE_DESCRIPTOR Source;
    PIO_RESOURCE_REQUIREMENTS_LIST Result;
    PIO_RESOURCE_DESCRIPTOR Target;
    ULONG Count, Bytes, i;
    NTSTATUS Status;
    if (!Requirements) return STATUS_INVALID_PARAMETER;
    *Requirements = NULL;
    Status = HalpNt5QueryRootResources(&Resources);
    if (!NT_SUCCESS(Status)) return Status;
    Count = Resources->List[0].PartialResourceList.Count;
    Bytes = FIELD_OFFSET(IO_RESOURCE_REQUIREMENTS_LIST, List[0].Descriptors) +
            (Count + 1) * sizeof(*Target);
    Result = ExAllocatePoolWithTag(PagedPool, Bytes, TAG_HAL);
    if (!Result)
    {
        ExFreePool(Resources);
        return STATUS_INSUFFICIENT_RESOURCES;
    }
    RtlZeroMemory(Result, Bytes);
    Result->ListSize = Bytes;
    Result->InterfaceType = PNPBus;
    Result->BusNumber = (ULONG)-1;
    Result->AlternativeLists = 1;
    Result->List[0].Version = Result->List[0].Revision = 1;
    Result->List[0].Count = Count + 1;
    Target = Result->List[0].Descriptors;
    Target->Type = CmResourceTypeConfigData;
    Target->ShareDisposition = CmResourceShareShared;
    Target->Option = IO_RESOURCE_PREFERRED;
    Target->u.ConfigData.Priority = 1;
    ++Target;
    Source = Resources->List[0].PartialResourceList.PartialDescriptors;
    for (i = 0; i < Count; ++i, ++Target, ++Source)
    {
        Target->Option = IO_RESOURCE_PREFERRED;
        Target->Type = Source->Type;
        Target->ShareDisposition = Source->ShareDisposition;
        Target->Flags = Source->Flags;
        if (Source->Type == CmResourceTypeBusNumber)
        {
            Target->u.BusNumber.Length = 256;
            Target->u.BusNumber.MinBusNumber = 0;
            Target->u.BusNumber.MaxBusNumber = 255;
        }
        else
        {
            /* Port and Memory union layouts share the same fields. */
            Target->u.Memory.Length = Source->u.Memory.Length;
            Target->u.Memory.Alignment = 1;
            Target->u.Memory.MinimumAddress = Source->u.Memory.Start;
            Target->u.Memory.MaximumAddress.QuadPart = Source->u.Memory.Start.QuadPart +
                                                     Source->u.Memory.Length - 1;
        }
    }
    ExFreePool(Resources);
    *Requirements = Result;
    return STATUS_SUCCESS;
}
