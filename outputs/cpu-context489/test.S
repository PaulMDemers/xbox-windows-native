/* SPDX-License-Identifier: MIT. Synthetic CPU context, not Xbox execution. */
.intel_syntax noprefix
.code32
.section .multiboot,"a"
.balign 4
.long 0x1badb002,0,-0x1badb002
.section .text
.global _start,expected_return1,expected_return2,fixture_gdt,capture_begin,capture_end
_start:
    cli
    cld
    lgdt [fixture_gdtr]
    ljmp 8, fixture_flat
fixture_flat:
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
    mov eax,0x12345000
    mov cr2,eax
    mov eax,cr0
    or eax,0x80000000
    mov cr0,eax
    jmp paged
paged:
    mov edi,0x120000
    mov ecx,256
    xor eax,eax
    rep stosd
    mov edi,0x120000
    call seed
    mov dword ptr [edi+12],1
    mov edi,0x120100
    call seed
    mov dword ptr [edi+12],2
    /* Explicit before/after memory guards. */
    mov dword ptr [0x11fffc],0xaabbccdd
    mov dword ptr [0x1200a0],0x11223344
    mov dword ptr [0x1200fc],0x55667788
    mov dword ptr [0x1201a0],0x99aabbcc
    mov edi,0x120000
    call registers
    call capture489
expected_return1:
    pushfd
    pushad
    cld
    mov esi,esp
    mov edi,0x130000
    mov ecx,9
    rep movsd
    add esp,36
    /* Second deliberately different context; these writes are TEST ONLY. */
    mov eax,0x1002000
    mov cr3,eax
    mov eax,0x6789a000
    mov cr2,eax
    mov edi,0x120100
    call registers
    call capture489
expected_return2:
    pushfd
    pushad
    cld
    mov esi,esp
    mov edi,0x130040
    mov ecx,9
    rep movsd
    add esp,36
    /* Save both records; repeated/invalid calls must not change these bytes. */
    mov esi,0x120000
    mov edi,0x140000
    mov ecx,128
    rep movsd
    mov edi,0x120000
    mov ecx,160
    call capture489
    mov esi,0x120000
    mov edi,0x140000
    mov ecx,128
    repe cmpsd
    jne fail
    /* Bad capacity with an UNMAPPED pointer must return before dereference. */
    mov edi,0xdead0000
    xor ecx,ecx
    call capture489
    /* Fresh buffer header refusal cases; complete160B unchanged each time. */
    xor ebp,ebp
negative:
    mov edi,0x120200
    mov ecx,40
    xor eax,eax
    rep stosd
    mov edi,0x120200
    call seed
    mov dword ptr [edi+12],1
    mov ebx,[cases+ebp*8]
    mov eax,[cases+ebp*8+4]
    mov [edi+ebx],eax
    mov esi,edi
    mov edi,0x140200
    mov ecx,40
    rep movsd
    mov edi,0x120200
    mov ecx,160
    call capture489
    mov esi,0x120200
    mov edi,0x140200
    mov ecx,40
    repe cmpsd
    jne fail
    inc ebp
    cmp ebp,10
    jne negative
    cmp dword ptr [0x11fffc],0xaabbccdd
    jne fail
    cmp dword ptr [0x1200a0],0x11223344
    jne fail
    cmp dword ptr [0x1200fc],0x55667788
    jne fail
    cmp dword ptr [0x1201a0],0x99aabbcc
    jne fail
    /* Binary transport: header, two records, both post-call PUSHAD/flags frames. */
    mov eax,0x39383454
    out 0xe9,al
    shr eax,8
    out 0xe9,al
    shr eax,8
    out 0xe9,al
    shr eax,8
    out 0xe9,al
    mov esi,0x120000
    mov ecx,160
    call emit
    mov esi,0x120100
    mov ecx,160
    call emit
    mov esi,0x130000
    mov ecx,36
    call emit
    mov esi,0x130040
    mov ecx,36
    call emit
    mov al,'P'
    out 0xe9,al
    mov eax,0x10
    out 0xf4,eax
    cli
1:  hlt
    jmp 1b
fail:
    mov al,'F'
    out 0xe9,al
    mov eax,0x11
    out 0xf4,eax
    cli
2:  hlt
    jmp 2b
seed:
    mov dword ptr [edi],0x39383443
    mov dword ptr [edi+4],1
    mov dword ptr [edi+8],160
    mov dword ptr [edi+16],0x48900101
    ret
registers:
    mov eax,0x11111111
    mov ebx,0x22222222
    mov ecx,160
    mov edx,0x33333333
    mov esi,0x44444444
    mov ebp,0x55555555
    push 0x682
    popfd
    ret
emit:
    lodsb
    out 0xe9,al
    loop emit
    ret
cases:
.long 0,0,4,0,8,159,12,0,12,3,16,0,132,1,152,1,156,1,8,161
.balign 8
fixture_gdt:
.quad 0,0x00cf9a000000ffff,0x00cf92000000ffff
fixture_gdtr: .word 23
.long fixture_gdt
fixture_idtr: .word 0
.long 0
capture_begin:
.include "capture.S"
capture_end:
