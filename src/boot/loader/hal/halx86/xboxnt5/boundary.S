/* SPDX-License-Identifier: GPL-2.0-or-later
 * Windows 2000 i386 boundary. Contracts verified against supplied 2195.7376.
 * These entry points adapt the HAL's C interfaces to the native NT5 ABI.
 */
#include <asm.inc>
.code
EXTERN __imp__Kei386EoiHelper@0:DWORD
EXTERN __imp_@KeUpdateSystemTime@12:DWORD
EXTERN __imp__KiDispatchInterrupt@0:DWORD
EXTERN _HalEndSystemInterrupt@8:PROC

PUBLIC @HalpNt5Eoi@4
.PROC @HalpNt5Eoi@4
    /* Discard every C frame. The kernel restores registers and executes IRET. */
    mov ebp, ecx
    mov esp, ecx
    jmp dword ptr [__imp__Kei386EoiHelper@0]
.ENDP

PUBLIC @HalpNt5UpdateSystemTime@12
.PROC @HalpNt5UpdateSystemTime@12
    /* ECX=trap, EDX=increment, [ESP+4]=old IRQL. Native NT expects no return
     * address: [ESP]=old IRQL, [ESP+4]=vector, [ESP+8]=trap frame. */
    movzx eax, byte ptr [esp+4]
    mov ebp, ecx
    mov esp, ecx
    push HEX(30) /* Xbox PIC primary vector + IRQ0 */
    push eax
    mov eax, edx
    jmp dword ptr [__imp_@KeUpdateSystemTime@12]
.ENDP

PUBLIC _HalpNt5EndSystemInterrupt@8
.PROC _HalpNt5EndSystemInterrupt@8
    /* Native NT passes a vector as argument 2; our PIC code needs EBP's trap.
     * Keep the internal HalEndSystemInterrupt ABI for all HAL C callers. */
    push ebp
    push dword ptr [esp+8]
    call _HalEndSystemInterrupt@8
    ret 8
.ENDP

PUBLIC _HalpNt5DispatchInterrupt@0
.PROC _HalpNt5DispatchInterrupt@0
    /* NT's assembly DPC helper clobbers EBX. Isolate the C caller from all
     * native nonvolatile-register assumptions. */
    push ebp
    push ebx
    push esi
    push edi
    call dword ptr [__imp__KiDispatchInterrupt@0]
    pop edi
    pop esi
    pop ebx
    pop ebp
    ret
.ENDP
END
