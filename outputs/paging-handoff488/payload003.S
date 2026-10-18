/* SPDX-License-Identifier: MIT
 * Independent entry oracle. No stack use until observed ESP is verified.
 * This substitutes for Xromwell: no Windows or Xbox device code executes.
 */
.intel_syntax noprefix
.code32
.global _start
_start:
    mov al,'E'
    out 0xe9,al
    cmp esp,0xd001cd7c
    jne fail
    mov eax,cr0
    test eax,0x80000000
    jnz fail
    mov eax,cr3
    test eax,eax
    jnz fail
    mov ax,cs
    cmp ax,8
    jne fail
    mov ax,ds
    cmp ax,16
    jne fail
    mov ax,es
    cmp ax,16
    jne fail
    mov ax,ss
    cmp ax,16
    jne fail
    mov ax,fs
    cmp ax,16
    jne fail
    mov ax,gs
    cmp ax,16
    jne fail
    sgdt [0x110000]
    sidt [0x110008]
    cmp word ptr [0x110000],0x8000
    jne fail
    cmp dword ptr [0x110002],0x2000000+GDT_OFFSET
    jne fail
    cmp word ptr [0x110008],0
    jne fail
    cmp dword ptr [0x11000a],0
    jne fail
    sldt ax
    test ax,ax
    jnz fail
    mov esp,0x180000
    pushfd
    pop eax
    test eax,0x600
    jnz fail
    /* Compare the complete original1MiB source against relocated contents. */
    mov esi,0x1f00000
    mov edi,0x2600000
    mov ecx,0x100000
    repe cmpsb
    jne fail
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
1:  hlt
    jmp 1b
