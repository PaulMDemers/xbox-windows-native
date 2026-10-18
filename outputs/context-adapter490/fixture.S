/* SPDX-License-Identifier: MIT. Diskless synthetic fixture, NOT Xbox state. */
.intel_syntax noprefix
.code32
.section .multiboot,"a"
.balign 4
.long 0x1badb002,0,-0x1badb002
.text
.global _start,test_enter,diag_reboot,fixture_success
.global witness_record,context490_packet,context490_claim,context490_first,context490_second
.global capture_begin,capture_end,fixture_gdt,context490_pre,context490_post
_start:
    cli
    cld
    lgdt [fixture_gdtr]
    ljmp 8,flat490
flat490:
    mov ax,16
    mov ds,ax
    mov es,ax
    mov ss,ax
    mov fs,ax
    mov gs,ax
    mov esp,0x180000
    lidt [fixture_idtr]
    mov al,255
    out 0x21,al
    out 0xa1,al
    mov edi,0x1000000
    mov ecx,4096
    xor eax,eax
    rep stosd
    mov dword ptr [0x1000000],0x83
    mov dword ptr [0x1002000],0x83
    mov eax,0x10
    mov cr4,eax
    mov eax,0x1000000
    mov cr3,eax
    mov eax,cr0
    or eax,0x80000000
    mov cr0,eax
    jmp paged490
paged490:
    call test_main
    mov eax,0x10
    out 0xf4,eax
    cli
1:  hlt
    jmp 1b
test_enter:
    pushfd
    pushad
    mov [fixture_saved_stack],esp
    mov eax,0x11111111
    mov ebx,0x22222222
    mov ecx,0x33333333
    mov edx,offset fixture_success
    mov esi,0x44444444
    mov edi,0x55555555
    mov ebp,0x66666666
    push dword ptr [fixture_flags]
    popfd
    pushfd
    pushad
    /* Save frame without changing its flags or contents. */
    mov esi,esp
    mov edi,offset expected_frame
    mov ecx,9
    cld
    rep movsd
    push dword ptr [esp+32]
    popfd
    jmp witness_entry
fixture_success:
    pushfd
    pushad
    cld
    mov esi,esp
    mov edi,offset actual_frame
    mov ecx,9
    rep movsd
    mov dword ptr [outcome],1
    jmp fixture_finish
diag_reboot:
    cld
    mov dword ptr [outcome],0
fixture_finish:
    mov esp,[fixture_saved_stack]
    popad
    popfd
    ret
.balign 8
fixture_gdt: .quad 0,0x00cf9a000000ffff,0x00cf92000000ffff
fixture_gdtr: .word 23
.long fixture_gdt
fixture_idtr: .word 0
.long 0
.include "witness.S"
.include "context.S"
capture_begin:
.include "capture.S"
capture_end:
.include "helpers.S"
.balign 4
.global blentry,ptr_newloc,newloc
blentry:
.incbin "loader.bin"
.set ptr_newloc,blentry+74
.set newloc,blentry+80
