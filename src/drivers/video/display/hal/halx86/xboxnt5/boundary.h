/* SPDX-License-Identifier: GPL-2.0-or-later */
#pragma once
DECLSPEC_NORETURN VOID FASTCALL HalpNt5Eoi(PKTRAP_FRAME TrapFrame);
DECLSPEC_NORETURN VOID FASTCALL HalpNt5UpdateSystemTime(PKTRAP_FRAME TrapFrame, ULONG Increment, KIRQL OldIrql);
VOID NTAPI HalpNt5DispatchInterrupt(VOID);
VOID FASTCALL HalpNt5EnterTrap(PKTRAP_FRAME TrapFrame);
VOID FASTCALL HalpNt5EnterInterruptTrap(PKTRAP_FRAME TrapFrame);
#define KiEoiHelper HalpNt5Eoi
#define KeUpdateSystemTime HalpNt5UpdateSystemTime
#define KiDispatchInterrupt HalpNt5DispatchInterrupt
#define KiEnterTrap HalpNt5EnterTrap
#define KiEnterInterruptTrap HalpNt5EnterInterruptTrap

NTSTATUS NTAPI HalpNt5GetInterruptTranslator(INTERFACE_TYPE, ULONG, INTERFACE_TYPE, USHORT, USHORT, PTRANSLATOR_INTERFACE, PULONG);

NTSTATUS NTAPI HalpNt5QueryRootResources(PCM_RESOURCE_LIST *);
NTSTATUS NTAPI HalpNt5QueryRootRequirements(PIO_RESOURCE_REQUIREMENTS_LIST *);
