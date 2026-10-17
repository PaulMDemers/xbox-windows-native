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
    call diag_flush
    jnz diag_close_refuse
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
    call diag_flush
    jnz diag_close_refuse
    push dword ptr [diag_handle]
    call dword ptr [DiagNtClose]
    test eax, eax
    jnz diag_reboot
    cmp dword ptr [diag_record+120], 1
    jne diag_reboot
    cmp dword ptr [diag_record+124], 1
    jne diag_reboot
    // Logging can change memory. Recheck AFTER every file operation is finished.
    cld
    mov esi, offset kernel
    mov edi, [kernelram]
    mov ecx, [cromwellsize]
    repe cmpsb
    jne diag_reboot
    mov edi, [bootloaderram]
    call diag_compare_loader
    cmp eax, 1
    jne diag_reboot
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
    cmp dword ptr [diag_handle], 0
    je diag_reboot
    push dword ptr [diag_handle]
    call dword ptr [DiagNtClose]
diag_reboot:
    push 1
    call dword ptr [DiagHalReturnToFirmware]
    ud2

.align 4
diag_record:
    .ascii "X460"
    .long 2, 160, 0x46000101
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
    .long 2, 0x46000101, 160
diag_handle: .long 0
diag_iosb: .long 0, 0
diag_object: .long 0, diag_name, 0x40
diag_name:
    .word diag_path_end-diag_path, diag_path_end-diag_path+1
    .long diag_path
diag_path:
    .ascii "\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot460a\\report.bin"
diag_path_end: .byte 0
