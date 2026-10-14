/*
 * PROJECT:         ReactOS HAL
 * LICENSE:         GPL - See COPYING in the top level directory
 * FILE:            hal/halx86/generic/halinit.c
 * PURPOSE:         HAL Entrypoint and Initialization
 * PROGRAMMERS:     Alex Ionescu (alex.ionescu@reactos.org)
 */

/* INCLUDES ******************************************************************/

#include <hal.h>
#define NDEBUG
#include <debug.h>

#ifdef XBOX_NT5_PHASE0_PREFLIGHT
VOID HalpXwnProcessorBoundary(BOOLEAN, ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#ifdef XBOX_NT5_HALBASE_PREFLIGHT
VOID HalpXwnPhase0(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#ifdef XBOX_NT5_TIMER_PREFLIGHT
VOID HalpXwnBaseReady(ULONG, PLOADER_PARAMETER_BLOCK, PVOID, NTSTATUS);
#ifdef XBOX_NT5_CLOCK_PREFLIGHT
VOID HalpXwnTimerReady(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#ifdef XBOX_NT5_HOOKS_PREFLIGHT
VOID HalpXwnClockReady(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#ifdef XBOX_NT5_BIOS_PREFLIGHT
VOID HalpXwnHooksReady(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#ifndef XBOX_NT5_MM_PREFLIGHT
DECLSPEC_NORETURN
#endif
VOID HalpXwnBiosReady(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#else
DECLSPEC_NORETURN VOID HalpXwnHooksReady(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#endif
#else
DECLSPEC_NORETURN VOID HalpXwnClockReady(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#endif
#else
DECLSPEC_NORETURN VOID HalpXwnTimerReady(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#endif
#else
DECLSPEC_NORETURN VOID HalpXwnBaseReady(ULONG, PLOADER_PARAMETER_BLOCK, PVOID, NTSTATUS);
#endif
#else
DECLSPEC_NORETURN VOID HalpXwnPhase0(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#endif
#endif
#ifdef XBOX_NT5_ENTRY_PREFLIGHT
DECLSPEC_NORETURN VOID HalpXwnFirstProcessor(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#endif

/* GLOBALS *******************************************************************/

//#ifdef CONFIG_SMP // FIXME: Reenable conditional once HAL is consistently compiled for SMP mode
BOOLEAN HalpOnlyBootProcessor;
//#endif
BOOLEAN HalpPciLockSettings;
BOOLEAN HalBootViaEfi;

/* PRIVATE FUNCTIONS *********************************************************/

static
CODE_SEG("INIT")
VOID
HalpGetParameters(
    _In_ PLOADER_PARAMETER_BLOCK LoaderBlock)
{
    /* Make sure we have a loader block and command line */
    if (LoaderBlock && LoaderBlock->LoadOptions)
    {
        /* Read the command line */
        PCSTR CommandLine = LoaderBlock->LoadOptions;

//#ifdef CONFIG_SMP // FIXME: Reenable conditional once HAL is consistently compiled for SMP mode
        /* Check whether we should only start one CPU */
        if (strstr(CommandLine, "ONECPU"))
            HalpOnlyBootProcessor = TRUE;
//#endif

        /* Check if PCI is locked */
        if (strstr(CommandLine, "PCILOCK"))
            HalpPciLockSettings = TRUE;

        /* Check for initial breakpoint */
        if (strstr(CommandLine, "BREAK"))
            DbgBreakPoint();
    }
}

/* FUNCTIONS *****************************************************************/

VOID
NTAPI
HalInitializeProcessor(
    IN ULONG ProcessorNumber,
    IN PLOADER_PARAMETER_BLOCK LoaderBlock)
{
#if defined(XBOX_NT5_PHASE0_PREFLIGHT)
    HalpXwnProcessorBoundary(FALSE, ProcessorNumber, LoaderBlock, _ReturnAddress());
#elif defined(XBOX_NT5_ENTRY_PREFLIGHT)
    HalpXwnFirstProcessor(ProcessorNumber, LoaderBlock, _ReturnAddress());
#endif
#if !defined(XBOX_NT5_ENTRY_PREFLIGHT) || defined(XBOX_NT5_PHASE0_PREFLIGHT)
    /* Hal specific initialization for this cpu */
    HalpInitProcessor(ProcessorNumber, LoaderBlock);

    /* Set default stall count */
    KeGetPcr()->StallScaleFactor = INITIAL_STALL_COUNT;

    /* Update the interrupt affinity and processor mask */
    InterlockedBitTestAndSetAffinity(&HalpActiveProcessors, ProcessorNumber);
    InterlockedBitTestAndSetAffinity(&HalpDefaultInterruptAffinity, ProcessorNumber);

    if (ProcessorNumber == 0)
    {
        /* Register routines for KDCOM */
        HalpRegisterKdSupportFunctions();
    }
#ifdef XBOX_NT5_PHASE0_PREFLIGHT
    HalpXwnProcessorBoundary(TRUE, ProcessorNumber, LoaderBlock, _ReturnAddress());
#endif
#endif
}

/*
 * @implemented
 */
CODE_SEG("INIT")
BOOLEAN
NTAPI
HalInitSystem(
    _In_ ULONG BootPhase,
    _In_ PLOADER_PARAMETER_BLOCK LoaderBlock)
{
#if defined(XBOX_NT5_PHASE0_PREFLIGHT)
    HalpXwnPhase0(BootPhase, LoaderBlock, _ReturnAddress());
#elif defined(XBOX_NT5_ENTRY_PREFLIGHT)
    /* Defense in depth: this build cannot continue into HAL system init. */
    _disable(); for (;;) __halt();
#endif
    PKPRCB Prcb = KeGetCurrentPrcb();
    NTSTATUS Status;

    /* Check the boot phase */
    if (BootPhase == 0)
    {
        /* Save bus type */
        HalpBusType = LoaderBlock->u.I386.MachineType & 0xFF;

        /* Get command-line parameters */
        HalpGetParameters(LoaderBlock);

#if (NTDDI_VERSION >= NTDDI_LONGHORN)
        HalBootViaEfi = LoaderBlock->FirmwareInformation.FirmwareTypeEfi;
#else
        HalBootViaEfi = FALSE;
#if defined(__REACTOS__) && !defined(XBOX_NT5_HAL)
        ASSERT(LoaderBlock->Extension != NULL);
        if (LoaderBlock->Extension->Size >= FIELD_OFFSET(LOADER_PARAMETER_EXTENSION, LoaderPerformanceData))
            HalBootViaEfi = LoaderBlock->Extension->BootViaEFI;
#endif
#endif

        /* Check for PRCB version mismatch */
        if (Prcb->MajorVersion != PRCB_MAJOR_VERSION)
        {
            /* No match, bugcheck */
            KeBugCheckEx(MISMATCHED_HAL, 1, Prcb->MajorVersion, PRCB_MAJOR_VERSION, 0);
        }

        /* Checked/free HAL requires checked/free kernel */
        if (Prcb->BuildType != HalpBuildType)
        {
            /* No match, bugcheck */
            KeBugCheckEx(MISMATCHED_HAL, 2, Prcb->BuildType, HalpBuildType, 0);
        }

        /* Initialize ACPI */
        Status = HalpSetupAcpiPhase0(LoaderBlock);
        if (!NT_SUCCESS(Status))
        {
            KeBugCheckEx(ACPI_BIOS_ERROR, Status, 0, 0, 0);
        }

        /* Initialize the PICs */
        HalpInitializePICs(TRUE);

        /* Initialize CMOS lock */
        KeInitializeSpinLock(&HalpSystemHardwareLock);

        /* Initialize CMOS */
        HalpInitializeCmos();

        /* Fill out the dispatch tables */
        HalQuerySystemInformation = HaliQuerySystemInformation;
        HalSetSystemInformation = HaliSetSystemInformation;
        HalInitPnpDriver = HaliInitPnpDriver;
        HalGetDmaAdapter = HalpGetDmaAdapter;

#ifdef XBOX_NT5_HAL
        HalGetInterruptTranslator = HalpNt5GetInterruptTranslator;
#else
        HalGetInterruptTranslator = NULL;  // FIXME: TODO
#endif
        HalResetDisplay = HalpBiosDisplayReset;
        HalHaltSystem = HaliHaltSystem;

        /* Setup I/O space */
        HalpDefaultIoSpace.Next = HalpAddressUsageList;
        HalpAddressUsageList = &HalpDefaultIoSpace;

#ifdef XBOX_NT5_HALBASE_PREFLIGHT
        HalpXwnBaseReady(BootPhase, LoaderBlock, _ReturnAddress(), Status);
#endif
        /* Setup busy waiting */
        HalpCalibrateStallExecution();
#ifdef XBOX_NT5_TIMER_PREFLIGHT
        HalpXwnTimerReady(BootPhase, LoaderBlock, _ReturnAddress());
#endif

        /* Initialize the clock */
        HalpInitializeClock();

        /*
         * We could be rebooting with a pending profile interrupt,
         * so clear it here before interrupts are enabled
         */
        HalStopProfileInterrupt(ProfileTime);
#ifdef XBOX_NT5_CLOCK_PREFLIGHT
        HalpXwnClockReady(BootPhase, LoaderBlock, _ReturnAddress());
#endif

        /* Do some HAL-specific initialization */
        HalpInitPhase0(LoaderBlock);
#ifdef XBOX_NT5_HOOKS_PREFLIGHT
        HalpXwnHooksReady(BootPhase, LoaderBlock, _ReturnAddress());
#endif

        /* Initialize Phase 0 of the x86 emulator */
        HalInitializeBios(0, LoaderBlock);
#ifdef XBOX_NT5_BIOS_PREFLIGHT
        HalpXwnBiosReady(BootPhase, LoaderBlock, _ReturnAddress());
#endif
    }
    else if (BootPhase == 1)
    {
        /* Initialize bus handlers */
        HalpInitBusHandlers();

        /* Do some HAL-specific initialization */
        HalpInitPhase1();

        /* Initialize Phase 1 of the x86 emulator */
        HalInitializeBios(1, LoaderBlock);
    }

    /* All done, return */
    return TRUE;
}
