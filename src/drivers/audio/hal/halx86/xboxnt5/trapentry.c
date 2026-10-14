/* SPDX-License-Identifier: GPL-2.0-or-later
 * Use the NT5 PCR debug flag, not the newer KTHREAD dispatcher-header byte.
 * Offsets below are verified against the matching Windows 2000 public PDB.
 */
#include <hal.h>
// The newer shared KPCR no longer names this byte DebugActive.
#define NT5_PCR_DEBUG_ACTIVE 0x50
C_ASSERT(FIELD_OFFSET(KPRCB, ProcessorState) == 0x1c);
C_ASSERT(FIELD_OFFSET(KPRCB, ProcessorState.SpecialRegisters.KernelDr0) == 0x2f8);
C_ASSERT(FIELD_OFFSET(KPRCB, ProcessorState.SpecialRegisters.KernelDr7) == 0x30c);
C_ASSERT(FIELD_OFFSET(KTRAP_FRAME, Eip) == 0x68);
C_ASSERT(FIELD_OFFSET(KTRAP_FRAME, EFlags) == 0x70);
C_ASSERT(FIELD_OFFSET(KTRAP_FRAME, ExceptionList) == 0x4c);
C_ASSERT(PRIMARY_VECTOR_BASE + PIC_TIMER_IRQ == 0x30);

VOID FASTCALL HalpNt5EnterTrap(PKTRAP_FRAME TrapFrame)
{
    TrapFrame->Dr7 = 0;
    if ((KiUserTrap(TrapFrame) || (TrapFrame->EFlags & EFLAGS_V86_MASK)) &&
        *((volatile UCHAR *)KeGetPcr() + NT5_PCR_DEBUG_ACTIVE))
    {
        KiHandleDebugRegistersOnTrapEntry(TrapFrame);
    }
}

VOID FASTCALL HalpNt5EnterInterruptTrap(PKTRAP_FRAME TrapFrame)
{
    KeGetPcr()->NtTib.ExceptionList = EXCEPTION_CHAIN_END;
    HalpNt5EnterTrap(TrapFrame);
}
