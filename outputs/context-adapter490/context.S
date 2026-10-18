/* SPDX-License-Identifier: MIT
 * Synchronous, single-owner adapter. Two fresh slots; no reset/retry API.
 * Captures before witness IO and after successful witness close. The saved
 * packet cannot prove its OWN flush/close or the later paging transition.
 */
.balign 4
context490_pre:
    pushfd
    pushad
    mov dword ptr [diag_reason],20
    cmp dword ptr [context490_claim],0
    jne context490_bad_stack
    cmp dword ptr [context490_first+132],0
    jne context490_bad_stack
    mov dword ptr [context490_claim],1
    push dword ptr [esp+32]
    popfd
    mov edi,offset context490_first
    mov ecx,160
    call capture489
context490_pre_return:
    popad
    popfd
    cmp dword ptr [context490_first+132],1
    jne diag_reboot
    ret

context490_post:
    pushfd
    pushad
    mov dword ptr [diag_reason],21
    cmp dword ptr [context490_claim],1
    jne context490_bad_stack
    cmp dword ptr [context490_first+132],1
    jne context490_bad_stack
    cmp dword ptr [context490_second+132],0
    jne context490_bad_stack
    cmp dword ptr [diag_closed],2
    jne context490_bad_stack
    mov dword ptr [context490_claim],2
    push dword ptr [esp+32]
    popfd
    mov edi,offset context490_second
    mov ecx,160
    call capture489
context490_post_return:
    popad
    popfd
    cmp dword ptr [context490_second+132],1
    jne diag_reboot
    mov eax,[diag_closed]
    mov [context490_packet+24],eax
    lea eax,[esp+4]
    mov [context490_packet+36],eax
    mov dword ptr [diag_handle],0
    mov dword ptr [diag_closed],0
    mov dword ptr [diag_reason],22
    call diag_reset_iosb
    push 0x62
    push 2
    push 0
    push 0x80
    push 0
    push offset diag_iosb
    push offset context490_object
    push 0x40100000
    push offset diag_handle
    call dword ptr [DiagNtCreateFile]
    test eax,eax
    jnz diag_reboot
    cmp dword ptr [diag_iosb],0
    jne diag_reboot
    cmp dword ptr [diag_iosb+4],2
    jne diag_reboot
    cmp dword ptr [diag_handle],0
    je diag_reboot
    mov dword ptr [diag_reason],23
    call diag_reset_iosb
    push 0
    push 400
    push offset context490_packet
    push offset diag_iosb
    push 0
    push 0
    push 0
    push dword ptr [diag_handle]
    call dword ptr [DiagNtWriteFile]
    test eax,eax
    jnz diag_reboot
    cmp dword ptr [diag_iosb],0
    jne diag_reboot
    cmp dword ptr [diag_iosb+4],400
    jne diag_reboot
    mov dword ptr [diag_reason],24
    call diag_flush
    jnz diag_reboot
    mov dword ptr [diag_reason],25
    mov dword ptr [diag_closed],1
    push dword ptr [diag_handle]
    call dword ptr [DiagNtClose]
    test eax,eax
    jnz diag_reboot
    mov dword ptr [diag_closed],2
    ret
context490_bad_stack:
    popad
    popfd
    jmp diag_reboot

.balign 4
context490_claim: .long 0
context490_packet:
    .ascii "C490"
    .long 1,400,0x49000101,1,2,0,2,witness_record,0
    .zero 24
context490_first:
    .ascii "C489"
    .long 1,160,1,0x48900101
    .zero 140
context490_second:
    .ascii "C489"
    .long 1,160,2,0x48900101
    .zero 140
    .ascii "DONE"
    .long 1,0x49000101,400
context490_object: .long 0,context490_name,0x40
context490_name:
    .word context490_path_end-context490_path,context490_path_end-context490_path+1
    .long context490_path
context490_path:
    .ascii "\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot490a\\context.bin"
context490_path_end: .byte 0
