/* SPDX-License-Identifier: GPL-2.0-or-later
 * Diagnostic only. Enter with the original pushad/pushfd frame intact.
 * The receipt proves the PRECEDING primary close, comparisons and marker.
 * Its own write/flush/close and subsequent checks/jump are NOT self-attested.
 */
.balign 4
witness_entry:
    cld
    mov eax, [diag_closed]
    mov [witness_record+16], eax
    mov eax, [diag_record+20]
    mov [witness_record+20], eax
    mov eax, [diag_record+120]
    mov [witness_record+24], eax
    mov eax, [diag_record+124]
    mov [witness_record+28], eax
    mov eax, [cromwellsize]
    mov [witness_record+32], eax
    mov eax, [kernelram]
    mov [witness_record+40], eax
    mov eax, [bootloaderram]
    mov [witness_record+44], eax
    mov eax, [phys_bootloaderram]
    mov [witness_record+48], eax
    mov eax, [phys_kernelram]
    mov [witness_record+52], eax
    mov eax, [esp+20]
    mov [witness_record+56], eax
    mov esi, offset before_marker_record
    mov edi, offset witness_record+64
    mov ecx, 24
    rep movsd
    mov esi, esp
    mov edi, offset witness_record+160
    mov ecx, 9
    rep movsd
    // Reuse the completed primary's handle/IOSB storage, not its on-disk bytes.
    // Reasons13..19 distinguish this file lifecycle in the existing refusal.
    mov dword ptr [diag_handle], 0
    mov dword ptr [diag_closed], 0
    mov dword ptr [diag_reason], 13
    call diag_reset_iosb
    push 0x62
    push 2
    push 0
    push 0x80
    push 0
    push offset diag_iosb
    push offset witness_object
    push 0x40100000
    push offset diag_handle
    call dword ptr [DiagNtCreateFile]
    test eax, eax
    jnz diag_reboot
    cmp dword ptr [diag_iosb], 0
    jne diag_reboot
    cmp dword ptr [diag_iosb+4], 2
    jne diag_reboot
    cmp dword ptr [diag_handle], 0
    je diag_reboot
    mov dword ptr [diag_reason], 14
    call diag_reset_iosb
    push 0
    push 256
    push offset witness_record
    push offset diag_iosb
    push 0
    push 0
    push 0
    push dword ptr [diag_handle]
    call dword ptr [DiagNtWriteFile]
    test eax, eax
    jnz diag_reboot
    cmp dword ptr [diag_iosb], 0
    jne diag_reboot
    cmp dword ptr [diag_iosb+4], 256
    jne diag_reboot
    mov dword ptr [diag_reason], 15
    call diag_flush
    jnz diag_reboot
    mov dword ptr [diag_reason], 16
    mov dword ptr [diag_closed], 1
    push dword ptr [diag_handle]
    call dword ptr [DiagNtClose]
    test eax, eax
    jnz diag_reboot
    mov dword ptr [diag_closed], 2
    // No kernel or SMBus calls after these final comparisons.
    mov dword ptr [diag_reason], 17
    cld
    mov esi, offset kernel
    mov edi, [kernelram]
    mov ecx, [cromwellsize]
    repe cmpsb
    jne diag_reboot
    mov dword ptr [diag_reason], 18
    mov edi, [bootloaderram]
    call diag_compare_loader
    cmp eax, 1
    jne diag_reboot
    mov dword ptr [diag_reason], 19
    mov edi, [phys_bootloaderram]
    call diag_compare_loader
    cmp eax, 1
    jne diag_reboot
witness_jump:
    popad
    popfd
    jmp edx

.balign 4
witness_record:
    .ascii "H485"
    .long 1, 256, 0x48500101
    .long 0, 0, 0, 0
    .long 0, 1024, 0, 0, 0, 0, 0, 0
    .zero 176
    .ascii "DONE"
    .long 1, 0x48500101, 256
witness_object: .long 0, witness_name, 0x40
witness_name:
    .word witness_path_end-witness_path, witness_path_end-witness_path+1
    .long witness_path
witness_path:
    .ascii "\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot485a\\handoff.bin"
witness_path_end: .byte 0
