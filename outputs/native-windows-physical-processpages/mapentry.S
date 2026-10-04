/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <asm.inc>
.code
#ifdef XBOX_NT5_PT_PREFLIGHT
EXTERN _HalpXwnPtAfter@8:PROC
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
EXTERN _HalpXwnFreeAfter@8:PROC
#ifdef XBOX_NT5_SYSPTES_PREFLIGHT
EXTERN _HalpXwnTailAfter@8:PROC
#ifdef XBOX_NT5_PROCESSPAGES_PREFLIGHT
EXTERN _HalpXwnProcessAfter@8:PROC
EXTERN _XwnSysTarget:DWORD
#endif
EXTERN _XwnFreeTarget:DWORD
#endif
EXTERN _XwnCommitTarget:DWORD
#endif
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
#ifdef XBOX_NT5_PROCESSPAGES_PREFLIGHT
    call _HalpXwnProcessAfter@8
#elif defined(XBOX_NT5_SYSPTES_PREFLIGHT)
    call _HalpXwnTailAfter@8
#elif defined(XBOX_NT5_FREELIST_PREFLIGHT)
    call _HalpXwnFreeAfter@8
#else
    call _HalpXwnPtAfter@8
#endif
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
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
PUBLIC _HalpXwnCommitEntry
.PROC _HalpXwnCommitEntry
    pushfd
    pushad
    push ebx
    push ebp
    call _HalpXwnPtAfter@8
    popad
    popfd
    jmp dword ptr [_XwnCommitTarget]
.ENDP
#endif
#ifdef XBOX_NT5_SYSPTES_PREFLIGHT
PUBLIC _HalpXwnFreeEntry
.PROC _HalpXwnFreeEntry
    pushfd
    pushad
    push ebx
    push ebp
    call _HalpXwnFreeAfter@8
    popad
    popfd
    jmp dword ptr [_XwnFreeTarget]
.ENDP
#endif
#ifdef XBOX_NT5_PROCESSPAGES_PREFLIGHT
PUBLIC _HalpXwnSysEntry
.PROC _HalpXwnSysEntry
    pushfd
    pushad
    push ebx
    push ebp
    call _HalpXwnTailAfter@8
    popad
    popfd
    jmp dword ptr [_XwnSysTarget]
.ENDP
#endif
END
