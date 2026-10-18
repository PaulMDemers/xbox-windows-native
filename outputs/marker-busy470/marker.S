/* SPDX-License-Identifier: MIT
 * Two bounded SMC LED transactions. Requires a valid owned stack and record.
 * Privileged I/O; no kernel calls, retry, reset, disk or EEPROM access.
 * Input: cdecl pointer to a writable 96-byte owned record.
 * Preserves every general register and EFLAGS. Result is in the record only.
 */
.intel_syntax noprefix
.code32
.text
.global marker_guarded
marker_guarded:
    pushfd
    pushad
    cld
    mov edi, [esp+40]
    call marker_body
    popad
    popfd
    ret

marker_body:
    cmp dword ptr [edi+88], 0
    jne marker_return
    mov dword ptr [edi+20], 2
    mov dword ptr [edi+88], 0
    cmp dword ptr [edi], 0x354b524d
    jne marker_done
    cmp dword ptr [edi+4], 1
    jne marker_done
    cmp dword ptr [edi+8], 96
    jne marker_done
    cmp dword ptr [edi+12], 1
    jne marker_stage2
    cmp dword ptr [edi+16], 0xff
    jne marker_done
    jmp marker_valid
marker_stage2:
    cmp dword ptr [edi+12], 2
    jne marker_done
    cmp dword ptr [edi+16], 0xa5
    jne marker_done
marker_valid:
    mov ebx, edi
    lea edi, [edi+20]
    xor eax, eax
    mov ecx, 19
    rep stosd
    mov edi, ebx
    cli
    rdtsc
    mov [edi+40], eax
    mov [edi+44], edx
    mov dword ptr [edi+84], 1
    mov ecx, 4096
    xor ebp, ebp
marker_transaction:
    mov [edi+72], ebp
marker_idle:
    call marker_clock
    jc marker_done
    test ecx, ecx
    jz marker_idle_budget
    dec ecx
    inc dword ptr [edi+36]
    mov dx, 0xc000
    in ax, dx
    movzx eax, ax
    mov [edi+32], eax
    mov [edi+56+ebp*4], eax
    test eax, 0xfffff7e7
    jnz marker_status_error
    test eax, 0x808
    jnz marker_idle
    /* Only acknowledge a completed, idle prior status. Never clear an error. */
    test eax, 0x10
    jz marker_configure
    out dx, ax
    inc dword ptr [edi+76]
    inc dword ptr [edi+80]
marker_configure:
    mov dx, 0xc004
    mov al, 0x20
    out dx, al
    mov dx, 0xc008
    mov eax, 8
    sub eax, ebp
    out dx, al
    mov dx, 0xc006
    mov eax, [edi+16]
    test ebp, ebp
    jz marker_value
    mov eax, 1
marker_value:
    out dx, ax
    mov dx, 0xc002
    mov al, 0x1a
    out dx, al
    add dword ptr [edi+76], 4
    bts dword ptr [edi+28], ebp
marker_completion:
    call marker_clock
    jc marker_done
    test ecx, ecx
    jz marker_completion_budget
    dec ecx
    inc dword ptr [edi+36]
    mov dx, 0xc000
    in ax, dx
    movzx eax, ax
    mov [edi+32], eax
    mov [edi+64+ebp*4], eax
    test eax, 0xfffff7e7
    jnz marker_status_error
    test eax, 0x808
    jnz marker_completion
    test eax, 0x10
    jz marker_completion
    inc dword ptr [edi+24]
    inc ebp
    cmp ebp, 2
    jb marker_transaction
    mov dword ptr [edi+20], 1
marker_done:
    mov dword ptr [edi+88], 1
marker_return:
    ret
marker_idle_budget:
    mov dword ptr [edi+20], 3
    jmp marker_done
marker_completion_budget:
    mov dword ptr [edi+20], 4
    jmp marker_done
marker_status_error:
    mov dword ptr [edi+20], 5
    jmp marker_done
marker_clock:
    rdtsc
    inc dword ptr [edi+84]
    mov [edi+48], eax
    mov [edi+52], edx
    sub eax, [edi+40]
    sbb edx, [edi+44]
    jc marker_clock_reverse
    test edx, edx
    jnz marker_clock_deadline
    cmp eax, 64000000
    jae marker_clock_deadline
    clc
    ret
marker_clock_reverse:
    mov dword ptr [edi+20], 7
    stc
    ret
marker_clock_deadline:
    mov dword ptr [edi+20], 6
    stc
    ret
.section .note.GNU-stack,"",@progbits
