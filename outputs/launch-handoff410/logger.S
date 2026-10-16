// SPDX-License-Identifier: GPL-2.0-or-later
// Diagnostic only: entered after allocation observation, never boots Windows.
// Xbox kernel ABI/ordinals independently pinned from owned nxdk headers/exports.
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
    // Create ONLY a new file in the new diagnostic directory on Partition1/E.
    push 0x62                 // write-through, synchronous nonalert, non-directory
    push 2                    // FILE_CREATE: refuse an existing report
    push 0                    // no sharing
    push 0x80                 // normal attributes
    push 0                    // allocation size unspecified
    push offset diag_iosb
    push offset diag_object
    push 0x40100000           // GENERIC_WRITE | SYNCHRONIZE
    push offset diag_handle
    call dword ptr [DiagNtCreateFile]
    test eax, eax
    js diag_reboot
    mov [diag_record+60], eax
    push 0
    push 128
    push offset diag_record
    push offset diag_iosb
    push 0
    push 0
    push 0
    push dword ptr [diag_handle]
    call dword ptr [DiagNtWriteFile]
    test eax, eax
    js diag_close
    cmp dword ptr [diag_iosb+4], 128
    jne diag_close
    push offset diag_iosb
    push dword ptr [diag_handle]
    call dword ptr [DiagNtFlushBuffersFile]
    test eax, eax
    js diag_close
    // A separate trailer follows a successful full write and flush.
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
    js diag_close
    cmp dword ptr [diag_iosb+4], 16
    jne diag_close
    push offset diag_iosb
    push dword ptr [diag_handle]
    call dword ptr [DiagNtFlushBuffersFile]
diag_close:
    push dword ptr [diag_handle]
    call dword ptr [DiagNtClose]
diag_reboot:
    push 1                    // HalRebootRoutine, same as nxdk XReboot
    call dword ptr [DiagHalReturnToFirmware]
    ud2                       // reboot is noreturn; no handoff fallback

.align 4
diag_record:
    .ascii "X410"
    .long 1, 128, 0x41000101  // version, header bytes, unique attempt cookie
    .long 0, 0             // entry flags, last completed observation (1..5)
    .long 0, 0, 0, 0       // kernel VA/PA, loader VA, virtual alias in/out
    .long 0xeeeeeeee, 0     // NtAllocateVirtualMemory status, returned size
    .long 0, 0, 0, 0       // payload length, flags before copy, original loader PA, create status
    .long 1024, blentry, newloc-blentry, ptr_newloc-blentry
    .long gdt_48_base+4-blentry, 0, 0, 0
    .long 0, 0, 0, 0
    .long 0, 0, 0, 0
diag_trailer:
    .ascii "DONE"
    .long 1, 0x41000101, 128
diag_handle: .long 0
diag_iosb: .long 0, 0
diag_object: .long 0, diag_name, 0x40
diag_name:
    .word diag_path_end-diag_path, diag_path_end-diag_path+1
    .long diag_path
diag_path:
    .ascii "\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot410a\\report.bin"
diag_path_end: .byte 0
