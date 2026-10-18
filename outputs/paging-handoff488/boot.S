/* SPDX-License-Identifier: MIT
 * Synthetic, diskless PC CPU fixture. NOT Xbox allocation/kernel evidence.
 * loader.bin is extracted from the pinned actual487 XBE, not rewritten here.
 */
.intel_syntax noprefix
.code32
.section .multiboot,"a"
.balign 4
.long 0x1badb002,0,-0x1badb002
.section .text
.global _start
_start:
    cli
    cld
    lgdt [fixture_gdtr]
    ljmp 8, flat
flat:
    mov ax,16
    mov ds,ax
    mov es,ax
    mov fs,ax
    mov gs,ax
    mov ss,ax
    mov esp,0x180000
    lidt [fixture_idtr]
    /* Mask external PIC interrupts; no actual Xbox interrupt timing modeled. */
    mov al,255
    out 0x21,al
    out 0xa1,al
    /* Synthetic source allocation: patterned full1MiB plus owned entry oracle. */
    mov edi,0x1f00000
    mov ecx,0x40000
    mov eax,0x93a65c17
    rep stosd
    mov esi,offset payload
    mov edi,0x1f00000
    mov ecx,payload_end-payload
    rep movsb
    /* Two physically distinct copies, identical except ordinary far patch. */
    mov esi,offset loader
    mov edi,0x2000000
    mov ecx,1024
    rep movsb
    mov esi,offset loader
    mov edi,0xc1000
    mov ecx,1024
    rep movsb
    mov dword ptr [0x2000000+FAR_OFFSET],0x2000000+NEW_OFFSET
    mov dword ptr [0xc1000+FAR_OFFSET],0x2000000+NEW_OFFSET
    /* PD at16MiB, one4KiB PT at16MiB+4KiB. Rest uses4MiB identity pages. */
    mov edi,0x1000000
    mov ecx,2048
    xor eax,eax
    rep stosd
    mov edi,0x1000000
    mov eax,0x83
    mov ecx,16
map:
    stosd
    add eax,0x400000
    loop map
    mov edi,0x1001000
    mov eax,0x2000003
    mov ecx,1024
pt:
    stosd
    add eax,4096
    loop pt
    mov dword ptr [0x1000020],0x1001003
    mov dword ptr [0x1001000],0xc1003
    mov dword ptr [0x1000820],0x2000083
    /* Fault mutations are confined to this synthetic fixture. */
.if CASE == 1
    mov dword ptr [0x1001000],0x2000003
.endif
.if CASE == 2
    mov dword ptr [0x1001000],0
.endif
.if CASE == 3
    mov word ptr [0x2000000+POST_PG_OFFSET],0x0b0f
.endif
.if CASE == 4
    mov word ptr [0xc1000],0x0b0f
.endif
.if CASE == 5
    mov dword ptr [0x2000000+FAR_OFFSET],0
    mov word ptr [0],0x0b0f
.endif
.if CASE == 6
    mov word ptr [0x1f00000],0x0b0f
.endif
.if CASE == 8
    /* Wrong initial kernel source; oracle must not report success. */
    mov word ptr [0x1e00000],0x0b0f
.endif
.if CASE == 9
    /* One byte short: reaches oracle but must fail full-copy comparison. */
    mov dword ptr [0x2000000+NEW_OFFSET+6],0xfffff
.endif
    mov eax,cr4
    or eax,0x10
    mov cr4,eax
    mov eax,0x1000000
    mov cr3,eax
    mov eax,cr0
    or eax,0x80000000
    mov cr0,eax
    jmp paged
paged:
    mov al,'B'
    out 0xe9,al
    push 0x282
    popfd
.if CASE == 7
    std
.endif
    mov esi,0x1f00000
.if CASE == 8
    mov esi,0x1e00000
.endif
    mov ecx,0x2000000-ORIGINAL_ENTRY
    mov edx,0x2000000
    /* Deliberately unmapped stack, as observed before physical entry. */
    mov esp,0xd001cd7c
    jmp edx
.balign 8
fixture_gdt:
.quad 0,0x00cf9a000000ffff,0x00cf92000000ffff
fixture_gdtr: .word 23
.long fixture_gdt
fixture_idtr: .word 0
.long 0
loader: .incbin "loader.bin"
payload: .incbin "payload.bin"
payload_end:
