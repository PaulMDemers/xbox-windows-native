/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <asm.inc>
.code
EXTERN _HalpXwnMapCheckpoint@4:PROC
PUBLIC _HalpXwnMapEntry
.PROC _HalpXwnMapEntry
    push ebp
    call _HalpXwnMapCheckpoint@4
    cli
MapHalt:
    hlt
    jmp MapHalt
.ENDP
END
