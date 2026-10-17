// SPDX-License-Identifier: GPL-2.0-or-later
// Save original jump state, check copies, then log before attempting handoff.
diag_bad_size:
    mov dword ptr [diag_record+116], 1
    jmp diag_refuse
diag_bad_alias:
    mov dword ptr [diag_record+116], 2
    jmp diag_refuse
diag_bad_mirror:
    mov dword ptr [diag_record+116], 3
diag_refuse:
    mov dword ptr [diag_record+20], 7
    jmp diag_finish

diag_verify:
    pushfd
    pushad
    mov eax, [esp+32]
    mov [diag_record+112], eax
    cld
    mov esi, esp
    mov edi, offset diag_record+128
    mov ecx, 8
    rep movsd
    mov dword ptr [diag_record+120], 1
    // Original copies and both original far-jump patches have now executed.
    push dword ptr [phys_bootloaderram]
    call dword ptr [MmGetPhysicalAddress]
    mov [diag_record+84], eax
    mov esi, [phys_bootloaderram]
    mov ebx, ptr_newloc-blentry
    mov eax, [esi+ebx]
    mov [diag_record+88], eax
    mov esi, [bootloaderram]
    mov ebx, ptr_newloc-blentry
    mov eax, [esi+ebx]
    mov [diag_record+92], eax
    mov esi, offset kernel
    mov edi, [kernelram]
    mov ecx, [cromwellsize]
    repe cmpsb
    sete al
    movzx eax, al
    mov [diag_record+96], eax
    mov edi, [bootloaderram]
    call diag_compare_loader
    mov [diag_record+100], eax
    mov edi, [phys_bootloaderram]
    call diag_compare_loader
    mov [diag_record+104], eax
    mov dword ptr [diag_record+108], 1
    mov dword ptr [diag_record+20], 6
    cmp dword ptr [diag_record+96], 1
    jne diag_finish
    cmp dword ptr [diag_record+100], 1
    jne diag_finish
    cmp dword ptr [diag_record+104], 1
    jne diag_finish
    test dword ptr [diag_record+112], 0x400
    jnz diag_finish
    mov dword ptr [diag_record+124], 1
    jmp diag_finish

diag_compare_loader:
    // Compare all 1024 bytes, with the sole expected four-byte target patch.
    mov esi, offset blentry
    xor ecx, ecx
1:
    cmp ecx, ptr_newloc-blentry
    je 2f
    mov al, [esi+ecx]
    cmp al, [edi+ecx]
    jne 3f
    inc ecx
    cmp ecx, 1024
    jb 1b
    mov eax, 1
    ret
2:
    mov eax, [phys_bootloaderram]
    add eax, newloc-blentry
    cmp [edi+ecx], eax
    jne 3f
    add ecx, 4
    jmp 1b
3:
    xor eax, eax
    ret
