/* SPDX-License-Identifier: MIT.
 * Proposed entry-only diagnostic. Kernel SMBus/delay services, no raw I/O/CLI.
 * Integration includes exact498 entry.S with its firmware symbol aliased to
 * Entry503Return and entry498_continue bound to entry503_complete.
 * Kernel calls can block: controller watchdog is required, not a guest timeout.
 */
.intel_syntax noprefix
.code32
.text
.global entry503_gate, entry503_complete
entry503_gate:
    pushfd
    pushad
    cld
    cmp dword ptr [entry503_state], 0
    jne entry503_reentry
    mov dword ptr [entry503_state], 1
    /* Pattern first, manual mode only if the pattern call succeeds. */
    push 0xff
    push 8
    call entry503_led
    mov [entry503_status], eax
    test eax, eax
    jnz entry503_begin_file
    push 1
    push 7
    call entry503_led
    mov [entry503_status+4], eax
    test eax, eax
    jnz entry503_begin_file
    call entry503_delay
    mov [entry503_status+8], eax
entry503_begin_file:
    /* Indicator errors do not prevent the independent first-file experiment. */
    popad
    popfd
    jmp entry498_gate

entry503_complete:
    pushfd
    pushad
    cld
    /* Keep the exact post498 entry image for independent integration tests. */
    mov esi, esp
    mov edi, offset entry503_restored
    mov ecx, 9
    rep movsd
    add dword ptr [entry503_restored+12], 4
    cmp dword ptr [entry503_state], 1
    jne entry503_reentry
    cmp dword ptr [entry498_state], 7
    jne entry503_reentry
    mov dword ptr [entry503_state], 2
    /* Green only after the unchanged file gate's final flush/close succeeded. */
    push 0x0f
    push 8
    call entry503_led
    mov [entry503_status+12], eax
    test eax, eax
    jnz entry503_return
    /* If manual mode was never enabled, do not claim a visible green phase. */
    cmp dword ptr [entry503_status+4], 0
    jne entry503_return
    call entry503_delay
    mov [entry503_status+16], eax
    jmp entry503_return

entry503_failed_file:
    /* Called by exact498's abort through Entry503Return with mode1 on stack. */
    cmp dword ptr [esp+4], 1
    jne entry503_reentry
    cld
    mov dword ptr [entry503_state], 0x80000001
entry503_return:
    /* One supported automatic-mode restore; no raw controller reset. */
    cmp dword ptr [entry503_restore_attempted], 0
    jne entry503_reentry
    mov dword ptr [entry503_restore_attempted], 1
    push 0
    push 7
    call entry503_led
    mov [entry503_status+20], eax
    mov dword ptr [entry503_return_requested], 1
entry503_reentry:
    push 1
    call dword ptr [DiagHalReturnToFirmware]
    ud2

entry503_led:
    /* Internal cdecl(command,value); external Xbox stdcall(0x20,cmd,FALSE,val). */
    push dword ptr [esp+8]
    push 0
    push dword ptr [esp+12]
    push 0x20
    call dword ptr [Entry503HalWriteSMBusValue]
    ret 8

entry503_delay:
    push offset entry503_interval
    push 0
    push 0
    call dword ptr [Entry503KeDelayExecutionThread]
    ret

.data
.balign 4
.global Entry503Return, entry503_state, entry503_status
.global entry503_restore_attempted, entry503_return_requested, entry503_restored
.global entry503_interval
Entry503Return: .long entry503_failed_file
entry503_state: .long 0
entry503_status: .long 0xeeeeeeee,0xeeeeeeee,0xeeeeeeee,0xeeeeeeee,0xeeeeeeee,0xeeeeeeee
entry503_restore_attempted: .long 0
entry503_return_requested: .long 0
entry503_restored: .zero 36
entry503_interval: .quad -20000000
.section .note.GNU-stack,"",@progbits
