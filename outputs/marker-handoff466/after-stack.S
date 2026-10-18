/* SPDX-License-Identifier: MIT
 * Detour replaces only MOV ESP at 026000f0; executes that exact operation first.
 * Located inside the existing one-MiB Cromwell destination, beyond original BSS.
 */
.intel_syntax noprefix
.code32
.text
.global after_stack_stub,after_stack_ready,after_stack_failed,after_stack_record
after_stack_stub:
    mov esp, 0x02800000
    pushfd
    pushad
    push offset after_stack_record
    call marker_guarded
    add esp, 4
    cmp dword ptr [after_stack_record+20], 1
    jne after_stack_failed
    popad
    popfd
after_stack_ready:
    jmp 0x026000f5
after_stack_failed:
    cli
    hlt
    jmp after_stack_failed
.balign 4
after_stack_record:
    .long 0x354b524d,1,96,2,0xa5
    .zero 76
