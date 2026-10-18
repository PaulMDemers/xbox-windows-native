/* SPDX-License-Identifier: MIT
 * Proposed earliest entry gate. Host-tested separately; NOT installed in an XBE.
 * Integration must JMP here, then define entry498_continue as the old _start.
 * Uses existing Xbox stdcall thunks; no allocation or privileged-state writes.
 */
.intel_syntax noprefix
.code32
.text
.global entry498_gate
entry498_gate:
    pushfd
    pushad
    cld
    cmp dword ptr [entry498_state], 0
    jne entry498_abort
    mov dword ptr [entry498_state], 1
    /* PUSHAD image: EDI,ESI,EBP,ESP-after-PUSHFD,EBX,EDX,ECX,EAX. */
    mov eax, [esp+32]
    mov [entry498_record+16], eax
    mov esi, esp
    mov edi, offset entry498_record+20
    mov ecx, 8
    rep movsd
    add dword ptr [entry498_record+32], 4
    xor eax, eax
    mov ax, cs
    mov [entry498_record+52], eax
    mov ax, ds
    mov [entry498_record+56], eax
    mov ax, es
    mov [entry498_record+60], eax
    mov ax, ss
    mov [entry498_record+64], eax
    mov ax, fs
    mov [entry498_record+68], eax
    mov ax, gs
    mov [entry498_record+72], eax
    /* FNV-1a detects accidental transport corruption, not authenticity. */
    mov eax, 2166136261
    mov esi, offset entry498_record
    mov ecx, 96
1:  movzx edx, byte ptr [esi]
    xor eax, edx
    imul eax, eax, 16777619
    inc esi
    loop 1b
    mov [entry498_trailer+4], eax
    call entry498_io
    cmp dword ptr [entry498_state], 7
    jne entry498_abort
    popad
    popfd
    jmp entry498_continue
entry498_abort:
    /* Metadata/static buffers stay alive; no retry, rearm or original boot. */
    push 1
    call dword ptr [DiagHalReturnToFirmware]
    ud2

entry498_reset_iosb:
    mov dword ptr [entry498_iosb], 0xeeeeeeee
    mov dword ptr [entry498_iosb+4], 0xeeeeeeee
    ret
entry498_io:
    call entry498_reset_iosb
    push 0x62
    push 2
    push 0
    push 0x80
    push 0
    push offset entry498_iosb
    push offset entry498_object
    push 0x40100000
    push offset entry498_handle
    call dword ptr [DiagNtCreateFile]
    test eax, eax
    jnz entry498_fail
    cmp dword ptr [entry498_handle], 0
    je entry498_fail
    mov dword ptr [entry498_owned], 1
    cmp dword ptr [entry498_iosb], 0
    jne entry498_fail
    cmp dword ptr [entry498_iosb+4], 2
    jne entry498_fail
    mov dword ptr [entry498_state], 2
    call entry498_reset_iosb
    push 0
    push 96
    push offset entry498_record
    call entry498_write
    test eax, eax
    jnz entry498_fail
    cmp dword ptr [entry498_iosb], 0
    jne entry498_fail
    cmp dword ptr [entry498_iosb+4], 96
    jne entry498_fail
    mov dword ptr [entry498_state], 3
    call entry498_flush
    test eax, eax
    jnz entry498_fail
    cmp dword ptr [entry498_iosb], 0
    jne entry498_fail
    mov dword ptr [entry498_state], 4
    call entry498_reset_iosb
    push 0
    push 16
    push offset entry498_trailer
    call entry498_write
    test eax, eax
    jnz entry498_fail
    cmp dword ptr [entry498_iosb], 0
    jne entry498_fail
    cmp dword ptr [entry498_iosb+4], 16
    jne entry498_fail
    mov dword ptr [entry498_state], 5
    call entry498_flush
    test eax, eax
    jnz entry498_fail
    cmp dword ptr [entry498_iosb], 0
    jne entry498_fail
    mov dword ptr [entry498_state], 6
    call entry498_close
    test eax, eax
    jnz entry498_fail
    mov dword ptr [entry498_state], 7
    ret

entry498_write:
    /* Caller supplies offset/length/buffer; move return address below args. */
    pop edx
    push offset entry498_iosb
    push 0
    push 0
    push 0
    push dword ptr [entry498_handle]
    push edx
    jmp dword ptr [DiagNtWriteFile]
entry498_flush:
    call entry498_reset_iosb
    push offset entry498_iosb
    push dword ptr [entry498_handle]
    call dword ptr [DiagNtFlushBuffersFile]
    ret
entry498_close:
    /* Set before call: even failure never causes a second close. */
    mov dword ptr [entry498_close_attempted], 1
    push dword ptr [entry498_handle]
    call dword ptr [DiagNtClose]
    mov [entry498_close_status], eax
    ret
entry498_fail:
    mov [entry498_status], eax
    mov eax, [entry498_iosb]
    mov [entry498_failure_iosb], eax
    mov eax, [entry498_iosb+4]
    mov [entry498_failure_info], eax
    or dword ptr [entry498_state], 0x80000000
    cmp dword ptr [entry498_owned], 1
    jne 1f
    cmp dword ptr [entry498_close_attempted], 0
    jne 1f
    call entry498_close
1:  ret

.data
.balign 4
.global entry498_record, entry498_trailer, entry498_state, entry498_owned
.global entry498_handle, entry498_iosb, entry498_object
.global entry498_status, entry498_failure_iosb, entry498_failure_info
.global entry498_close_attempted, entry498_close_status
entry498_record:
    .ascii "E498"
    .long 1, 96, 0x49800101
    .zero 80
entry498_trailer:
    .ascii "DONE"
    .long 0, 0x49800101, 96
entry498_state: .long 0
entry498_owned: .long 0
entry498_handle: .long 0
entry498_iosb: .long 0, 0
entry498_status: .long 0xeeeeeeee
entry498_failure_iosb: .long 0xeeeeeeee
entry498_failure_info: .long 0xeeeeeeee
entry498_close_attempted: .long 0
entry498_close_status: .long 0xeeeeeeee
entry498_object: .long 0, entry498_name, 0x40
entry498_name:
    .word entry498_path_end-entry498_path, entry498_path_end-entry498_path+1
    .long entry498_path
entry498_path:
    .ascii "\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot498a\\entry.bin"
entry498_path_end: .byte 0
.section .note.GNU-stack,"",@progbits
