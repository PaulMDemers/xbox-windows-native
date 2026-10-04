/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <asm.inc>
.code
#ifdef XBOX_NT5_SCAN_PREFLIGHT
EXTERN _HalpXwnScanCheckpoint@8:PROC
#else
EXTERN _HalpXwnMapCheckpoint@4:PROC
#endif
PUBLIC _HalpXwnMapEntry
.PROC _HalpXwnMapEntry
#ifdef XBOX_NT5_SCAN_PREFLIGHT
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
END
