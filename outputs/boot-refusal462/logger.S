// SPDX-License-Identifier: GPL-2.0-or-later
// All file calls precede the original privileged loader instructions.
diag_finish:
    cld
    mov eax, [kernelram]
    mov [diag_record+24], eax
    mov eax, [phys_kernelram]
    mov [diag_record+28], eax
    mov eax, [bootloaderram]
    mov [diag_record+32], eax
    mov eax, [phys_bootloaderram]
    mov [diag_record+36], eax
    mov eax, [ptr_PAGE_SIZE]
    mov [diag_record+44], eax
    mov eax, [cromwellsize]
    mov [diag_record+48], eax
    mov dword ptr [diag_reason], 1
    call diag_reset_iosb
    push 0x62
    push 2
    push 0
    push 0x80
    push 0
    push offset diag_iosb
    push offset diag_object
    push 0x40100000
    push offset diag_handle
    call dword ptr [DiagNtCreateFile]
    test eax, eax
    jnz diag_close_refuse
    cmp dword ptr [diag_iosb], 0
    jne diag_close_refuse
    cmp dword ptr [diag_iosb+4], 2
    jne diag_close_refuse
    cmp dword ptr [diag_handle], 0
    je diag_reboot
    mov [diag_record+60], eax
    mov dword ptr [diag_reason], 2
    call diag_reset_iosb
    push 0
    push 160
    push offset diag_record
    push offset diag_iosb
    push 0
    push 0
    push 0
    push dword ptr [diag_handle]
    call dword ptr [DiagNtWriteFile]
    test eax, eax
    jnz diag_close_refuse
    cmp dword ptr [diag_iosb], 0
    jne diag_close_refuse
    cmp dword ptr [diag_iosb+4], 160
    jne diag_close_refuse
    mov dword ptr [diag_reason], 3
    call diag_flush
    jnz diag_close_refuse
    mov dword ptr [diag_reason], 4
    call diag_reset_iosb
    push 0
    push 16
    push offset diag_trailer
    push offset diag_iosb
    push 0
    push 0
    push 0
    push dword ptr [diag_handle]
    call dword ptr [DiagNtWriteFile]
    test eax, eax
    jnz diag_close_refuse
    cmp dword ptr [diag_iosb], 0
    jne diag_close_refuse
    cmp dword ptr [diag_iosb+4], 16
    jne diag_close_refuse
    mov dword ptr [diag_reason], 5
    call diag_flush
    jnz diag_close_refuse
    mov dword ptr [diag_reason], 6
    mov dword ptr [diag_closed], 1
    push dword ptr [diag_handle]
    call dword ptr [DiagNtClose]
    test eax, eax
    jnz diag_reboot
    mov dword ptr [diag_closed], 2
    mov dword ptr [diag_reason], 7
    cmp dword ptr [diag_record+120], 1
    jne diag_reboot
    mov dword ptr [diag_reason], 8
    cmp dword ptr [diag_record+124], 1
    jne diag_reboot
    // Logging can change memory. Recheck AFTER every file operation is finished.
    mov dword ptr [diag_reason], 9
    cld
    mov esi, offset kernel
    mov edi, [kernelram]
    mov ecx, [cromwellsize]
    repe cmpsb
    jne diag_reboot
    mov dword ptr [diag_reason], 10
    mov edi, [bootloaderram]
    call diag_compare_loader
    cmp eax, 1
    jne diag_reboot
    mov dword ptr [diag_reason], 11
    mov edi, [phys_bootloaderram]
    call diag_compare_loader
    cmp eax, 1
    jne diag_reboot
diag_handoff:
    popad
    popfd
    jmp edx

diag_reset_iosb:
    mov dword ptr [diag_iosb], 0xeeeeeeee
    mov dword ptr [diag_iosb+4], 0xeeeeeeee
    ret
diag_flush:
    call diag_reset_iosb
    push offset diag_iosb
    push dword ptr [diag_handle]
    call dword ptr [DiagNtFlushBuffersFile]
    test eax, eax
    jnz 1f
    cmp dword ptr [diag_iosb], 0
1:  ret
diag_close_refuse:
diag_reboot:
    // Snapshot FIRST refusal before cleanup or fallback I/O changes any status.
    mov [refusal_record+20], eax
    mov eax, [diag_reason]
    mov [refusal_record+16], eax
    mov eax, [diag_iosb]
    mov [refusal_record+24], eax
    mov eax, [diag_iosb+4]
    mov [refusal_record+28], eax
    mov eax, [diag_handle]
    mov [refusal_record+32], eax
    mov eax, [diag_closed]
    mov [refusal_record+36], eax
    mov eax, [diag_record+20]
    mov [refusal_record+40], eax
    mov eax, [diag_record+120]
    mov [refusal_record+44], eax
    mov eax, [diag_record+124]
    mov [refusal_record+48], eax
    mov eax, [diag_record+96]
    mov [refusal_record+52], eax
    mov eax, [diag_record+100]
    mov [refusal_record+56], eax
    mov eax, [diag_record+104]
    mov [refusal_record+60], eax
    mov eax, [diag_record+112]
    mov [refusal_record+64], eax
    mov eax, [diag_record+116]
    mov [refusal_record+68], eax
    cmp dword ptr [diag_closed], 0
    jne refusal_write
    cmp dword ptr [diag_handle], 0
    je refusal_write
    push dword ptr [diag_handle]
    call dword ptr [DiagNtClose]
    mov [refusal_record+72], eax
refusal_write:
    // One attempt in a DISTINCT exclusive file; no recursion or handoff fallback.
    cld
    mov dword ptr [refusal_iosb], 0xeeeeeeee
    mov dword ptr [refusal_iosb+4], 0xeeeeeeee
    push 0x62
    push 2
    push 0
    push 0x80
    push 0
    push offset refusal_iosb
    push offset refusal_object
    push 0x40100000
    push offset refusal_handle
    call dword ptr [DiagNtCreateFile]
    test eax, eax
    jnz refusal_close
    cmp dword ptr [refusal_iosb], 0
    jne refusal_close
    cmp dword ptr [refusal_iosb+4], 2
    jne refusal_close
    cmp dword ptr [refusal_handle], 0
    je refusal_reboot
    mov dword ptr [refusal_iosb], 0xeeeeeeee
    mov dword ptr [refusal_iosb+4], 0xeeeeeeee
    push 0
    push 96
    push offset refusal_record
    push offset refusal_iosb
    push 0
    push 0
    push 0
    push dword ptr [refusal_handle]
    call dword ptr [DiagNtWriteFile]
    test eax, eax
    jnz refusal_close
    cmp dword ptr [refusal_iosb], 0
    jne refusal_close
    cmp dword ptr [refusal_iosb+4], 96
    jne refusal_close
    mov dword ptr [refusal_iosb], 0xeeeeeeee
    mov dword ptr [refusal_iosb+4], 0xeeeeeeee
    push offset refusal_iosb
    push dword ptr [refusal_handle]
    call dword ptr [DiagNtFlushBuffersFile]
    // Regardless of fallback flush outcome, never resume or retry a refusal.
refusal_close:
    cmp dword ptr [refusal_handle], 0
    je refusal_reboot
    push dword ptr [refusal_handle]
    call dword ptr [DiagNtClose]
refusal_reboot:
    push 1
    call dword ptr [DiagHalReturnToFirmware]
    ud2

.align 4
diag_record:
    .ascii "X462"
    .long 2, 160, 0x46200101
    .long 0, 0
    .long 0, 0, 0, 0
    .long 0xeeeeeeee, 0
    .long 0, 0, 0, 0
    .long 1024, blentry, newloc-blentry, ptr_newloc-blentry
    .long gdt_48_base+4-blentry, 0, 0, 0
    .long 0, 0, 0, 0
    .long 0, 0, 0, 0
    .long 0, 0, 0, 0, 0, 0, 0, 0
diag_trailer:
    .ascii "DONE"
    .long 2, 0x46200101, 160
diag_handle: .long 0
diag_iosb: .long 0, 0
diag_object: .long 0, diag_name, 0x40
diag_name:
    .word diag_path_end-diag_path, diag_path_end-diag_path+1
    .long diag_path
diag_path:
    .ascii "\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot462a\\report.bin"
diag_path_end: .byte 0

.align 4
diag_reason: .long 0
diag_closed: .long 0
refusal_record:
    .ascii "R462"
    .long 1, 96, 0x46200101
    .long 0, 0, 0, 0, 0, 0, 0, 0
    .long 0, 0, 0, 0, 0, 0, 0xeeeeeeee, 0
    .ascii "DONE"
    .long 1, 0x46200101, 96
refusal_handle: .long 0
refusal_iosb: .long 0, 0
refusal_object: .long 0, refusal_name, 0x40
refusal_name:
    .word refusal_path_end-refusal_path, refusal_path_end-refusal_path+1
    .long refusal_path
refusal_path:
    .ascii "\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot462a\\refusal.bin"
refusal_path_end: .byte 0
