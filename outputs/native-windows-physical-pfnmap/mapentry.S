/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <asm.inc>
.code
#ifdef XBOX_NT5_PT_PREFLIGHT
EXTERN _HalpXwnPtAfter@8:PROC
EXTERN _HalpXwnPtBefore@8:PROC
EXTERN _XwnPtBeforeTarget:DWORD
#elif defined(XBOX_NT5_SCAN_PREFLIGHT)
EXTERN _HalpXwnScanCheckpoint@8:PROC
#else
EXTERN _HalpXwnMapCheckpoint@4:PROC
#endif
PUBLIC _HalpXwnMapEntry
.PROC _HalpXwnMapEntry
#ifdef XBOX_NT5_PT_PREFLIGHT
    push ebx
    push ebp
    call _HalpXwnPtAfter@8
#elif defined(XBOX_NT5_SCAN_PREFLIGHT)
    push ebx
    push ebp
    call _HalpXwnScanCheckpoint@8
#else
    push ebp
    call _HalpXwnMapCheckpoint@4
#endif
    cli
MapHalt:
    hlt
    jmp MapHalt
.ENDP
#ifdef XBOX_NT5_PT_PREFLIGHT
PUBLIC _HalpXwnPtBeforeEntry
.PROC _HalpXwnPtBeforeEntry
    pushfd
    pushad
    push ebx
    push ebp
    call _HalpXwnPtBefore@8
    popad
    popfd
    jmp dword ptr [_XwnPtBeforeTarget]
.ENDP
#endif
END
