/*
 * PROJECT: Xbox NT5 HAL experiment
 * LICENSE: GPL-2.0-or-later (see ReactOS COPYING)
 * PURPOSE: Fixed PIC interrupt translation for NT5 PnP.
 * Based on the public ReactOS translator contract (fstub/translate.c).
 * PCI routes are the firmware-programmed InterruptLine values; this does not
 * implement an ACPI/APIC router or change chipset routing registers.
 */
#include <hal.h>

C_ASSERT(sizeof(TRANSLATOR_INTERFACE) == 24);
#undef HalGetInterruptTranslator
C_ASSERT(FIELD_OFFSET(HAL_DISPATCH, HalGetInterruptTranslator) == 0x40);

/* The firmware's PIC ELCR, recorded by HalpInitializePICs. PCI's generic
 * level-sensitive descriptors are not the trigger mode of every Xbox line
 * (notably USB0 is wired to the edge-only PIC IRQ 1). Match the translated
 * contract to the actual PIC; preserve unrelated descriptor flag bits.
 */
extern LONG HalpEisaELCR;
static USHORT HalpNt5PciInterruptFlags(USHORT Flags, ULONG Line)
{
    return (Flags & ~CM_RESOURCE_INTERRUPT_LATCHED) |
           ((HalpEisaELCR & (1 << Line)) ? CM_RESOURCE_INTERRUPT_LEVEL_SENSITIVE :
                                         CM_RESOURCE_INTERRUPT_LATCHED);
}

static VOID NTAPI HalpNt5TranslatorReference(PVOID Context) { }

static NTSTATUS
HalpNt5PciLine(PDEVICE_OBJECT Pdo, PULONG Line)
{
    ULONG Bus, Address, Length;
    PCI_SLOT_NUMBER Slot;
    UCHAR Interrupt[2];
    NTSTATUS Status;
    if (!Pdo) return STATUS_INVALID_PARAMETER;
    Status = IoGetDeviceProperty(Pdo, DevicePropertyBusNumber,
                                sizeof(Bus), &Bus, &Length);
    if (!NT_SUCCESS(Status)) return Status;
    if (Length != sizeof(Bus) || Bus > 255) return STATUS_INVALID_PARAMETER;
    Status = IoGetDeviceProperty(Pdo, DevicePropertyAddress,
                                sizeof(Address), &Address, &Length);
    if (!NT_SUCCESS(Status)) return Status;
    if (Length != sizeof(Address) || (Address >> 16) > 31 ||
        (Address & 0xffff) > 7) return STATUS_INVALID_PARAMETER;
    Slot.u.AsULONG = 0;
    Slot.u.bits.DeviceNumber = Address >> 16;
    Slot.u.bits.FunctionNumber = Address & 0xffff;
    if (HalGetBusDataByOffset(PCIConfiguration, Bus, Slot.u.AsULONG,
                             Interrupt, 0x3c, sizeof(Interrupt)) != sizeof(Interrupt))
        return STATUS_UNSUCCESSFUL;
    if (!Interrupt[1] || Interrupt[1] > 4 || !Interrupt[0] || Interrupt[0] >= 16)
        return STATUS_UNSUCCESSFUL;
    *Line = Interrupt[0];
    return STATUS_SUCCESS;
}

static ULONG
HalpNt5TranslateLine(ULONG Line, PKIRQL Irql, PKAFFINITY Affinity)
{
    if (Line >= 16) return 0;
    return HalGetInterruptVector(Isa, 0, Line, Line, Irql, Affinity);
}

NTSTATUS NTAPI
HalpNt5TranslateResource(PVOID Context, PCM_PARTIAL_RESOURCE_DESCRIPTOR Source,
                        RESOURCE_TRANSLATION_DIRECTION Direction,
                        ULONG AlternativesCount, PIO_RESOURCE_DESCRIPTOR Alternatives,
                        PDEVICE_OBJECT Pdo, PCM_PARTIAL_RESOURCE_DESCRIPTOR Target)
{
    ULONG Line, Vector, i, Minimum, Maximum;
    KIRQL Irql;
    KAFFINITY Affinity;
    NTSTATUS Status;
    if (!Source || !Target || Source->Type != CmResourceTypeInterrupt)
        return STATUS_INVALID_PARAMETER;
    if (Direction == TranslateChildToParent)
    {
        Vector = HalpNt5TranslateLine(Source->u.Interrupt.Vector, &Irql, &Affinity);
        if (!Vector) return STATUS_UNSUCCESSFUL;
        *Target = *Source;
        if ((ULONG_PTR)Context == PCIBus)
            Target->Flags = HalpNt5PciInterruptFlags(Source->Flags,
                                                    Source->u.Interrupt.Vector);
        Target->u.Interrupt.Vector = Vector;
        Target->u.Interrupt.Level = Irql;
        Target->u.Interrupt.Affinity = Affinity;
        return STATUS_TRANSLATION_COMPLETE;
    }
    if (Direction != TranslateParentToChild) return STATUS_INVALID_PARAMETER;
    if ((ULONG_PTR)Context == PCIBus)
    {
        Status = HalpNt5PciLine(Pdo, &Line);
        if (!NT_SUCCESS(Status)) return Status;
        Vector = HalpNt5TranslateLine(Line, &Irql, &Affinity);
        if (!Vector || Vector != Source->u.Interrupt.Vector) return STATUS_UNSUCCESSFUL;
    }
    else
    {
        if (!Alternatives || !AlternativesCount) return STATUS_INVALID_PARAMETER;
        for (i = 0; i < AlternativesCount; ++i)
        {
            if (Alternatives[i].Type != CmResourceTypeInterrupt) continue;
            Minimum = Alternatives[i].u.Interrupt.MinimumVector;
            Maximum = min(Alternatives[i].u.Interrupt.MaximumVector, 15);
            for (Line = Minimum; Line <= Maximum; ++Line)
            {
                Vector = HalpNt5TranslateLine(Line, &Irql, &Affinity);
                if (Vector && Vector == Source->u.Interrupt.Vector) goto Found;
            }
        }
        return STATUS_UNSUCCESSFUL;
    }
Found:
    *Target = *Source;
    if ((ULONG_PTR)Context == PCIBus)
        Target->Flags = HalpNt5PciInterruptFlags(Source->Flags, Line);
    Target->u.Interrupt.Vector = Target->u.Interrupt.Level = Line;
    Target->u.Interrupt.Affinity = (KAFFINITY)-1;
    return STATUS_SUCCESS;
}

NTSTATUS NTAPI
HalpNt5TranslateRequirements(PVOID Context, PIO_RESOURCE_DESCRIPTOR Source,
                            PDEVICE_OBJECT Pdo, PULONG TargetCount,
                            PIO_RESOURCE_DESCRIPTOR *Target)
{
    ULONG Minimum, Maximum, Line, Vector, Count = 0, Vectors[16];
    KIRQL Irql;
    KAFFINITY Affinity;
    NTSTATUS Status;
    PIO_RESOURCE_DESCRIPTOR Result;
    if (!Target || !TargetCount) return STATUS_INVALID_PARAMETER;
    *Target = NULL;
    *TargetCount = 0;
    if (!Source || Source->Type != CmResourceTypeInterrupt)
        return STATUS_INVALID_PARAMETER;
    if ((ULONG_PTR)Context == PCIBus)
    {
        Status = HalpNt5PciLine(Pdo, &Minimum);
        if (!NT_SUCCESS(Status)) return Status;
        Maximum = Minimum;
    }
    else
    {
        Minimum = Source->u.Interrupt.MinimumVector;
        Maximum = min(Source->u.Interrupt.MaximumVector, 15);
    }
    for (Line = Minimum; Line <= Maximum; ++Line)
    {
        Vector = HalpNt5TranslateLine(Line, &Irql, &Affinity);
        if (Vector) Vectors[Count++] = Vector;
    }
    if (!Count) return STATUS_UNSUCCESSFUL;
    Result = ExAllocatePoolWithTag(PagedPool, Count * sizeof(*Result), TAG_HAL);
    if (!Result) return STATUS_INSUFFICIENT_RESOURCES;
    for (Line = 0; Line < Count; ++Line)
    {
        Result[Line] = *Source;
        if ((ULONG_PTR)Context == PCIBus)
            Result[Line].Flags = HalpNt5PciInterruptFlags(Source->Flags, Minimum);
        if (Line) Result[Line].Option |= IO_RESOURCE_ALTERNATIVE;
        Result[Line].u.Interrupt.MinimumVector = Vectors[Line];
        Result[Line].u.Interrupt.MaximumVector = Vectors[Line];
    }
    *Target = Result;
    *TargetCount = Count;
    return STATUS_TRANSLATION_COMPLETE;
}

NTSTATUS NTAPI
HalpNt5GetInterruptTranslator(INTERFACE_TYPE Parent, ULONG ParentBus,
                             INTERFACE_TYPE Bridge, USHORT Size, USHORT Version,
                             PTRANSLATOR_INTERFACE Translator, PULONG BridgeBus)
{
    if (!Translator || Size < sizeof(*Translator) || Version != 0)
        return STATUS_INVALID_PARAMETER;
    if (Bridge != PCIBus && Bridge != Isa && Bridge != Eisa &&
        Bridge != InterfaceTypeUndefined) return STATUS_NOT_IMPLEMENTED;
    if (Parent != Internal && Parent != PCIBus && Parent != Isa && Parent != Eisa)
        return STATUS_NOT_IMPLEMENTED;
    Translator->Size = sizeof(*Translator);
    Translator->Version = 0;
    Translator->Context = UlongToPtr(Bridge == PCIBus ? PCIBus : Isa);
    Translator->InterfaceReference = HalpNt5TranslatorReference;
    Translator->InterfaceDereference = HalpNt5TranslatorReference;
    Translator->TranslateResources = HalpNt5TranslateResource;
    Translator->TranslateResourceRequirements = HalpNt5TranslateRequirements;
    return STATUS_SUCCESS;
}
