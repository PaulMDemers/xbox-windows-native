/* SPDX-License-Identifier: MIT. Diskless CPU fixture only, not Xbox devices. */
.intel_syntax noprefix
.code32
.section .multiboot,"a"
.balign 4
.long 0x1badb002,0,-0x1badb002
.section .text
.global _start,fixture_fault,fixture_fault_loop
_start:
 cli
 cld
 lgdt [gdtr]
 ljmp 8, flat
flat:
 mov ax,16
 mov ds,ax
 mov es,ax
 mov ss,ax
 mov fs,ax
 mov gs,ax
 mov esp,0x180000
 /* Fixture masks PC PIC only; diagnostic page performs no port writes. */
 mov al,255
 out 0x21,al
 out 0xa1,al
 mov edi,offset idt
 mov ecx,256
 mov ebx,offset fixture_fault
idt_loop:
 mov eax,ebx
 and eax,0xffff
 or eax,0x80000
 stosd
 mov eax,ebx
 and eax,0xffff0000
 or eax,0x8e00
 stosd
 loop idt_loop
 lidt [idtr]
 /* Neighbor-page guards around both copies. */
 mov edi,TARGET-4096
 mov ecx,3072
 mov eax,0x5a5a5a5a
 rep stosd
 mov edi,ALIAS-4096
 mov ecx,3072
 rep stosd
 mov edi,0x3000000
 mov ecx,921600
 mov eax,0x20202020
 rep stosd
 mov esi,offset page
 mov edi,TARGET
 mov ecx,4096
 rep movsb
 mov esi,offset page
 mov edi,ALIAS
 mov ecx,4096
 rep movsb
 /* 64MiB identity mappings except the one target PTE in PDE7. */
 mov edi,0x3f00000
 mov ecx,2048
 xor eax,eax
 rep stosd
 mov edi,0x3f00000
 mov ecx,16
 mov eax,0x83
pd_loop:
 stosd
 add eax,0x400000
 loop pd_loop
 mov edi,0x3f01000
 mov ecx,1024
 mov eax,0x1c00003
pt_loop:
 stosd
 add eax,4096
 loop pt_loop
 mov dword ptr [0x3f00000+7*4],0x3f01003
 mov dword ptr [0x3f01000+((TARGET-0x1c00000)/4096)*4],ALIAS+3
.if CASE == 3
 mov dword ptr [TARGET+0x500],0
 mov dword ptr [ALIAS+0x500],0
.endif
.if CASE == 4
 mov dword ptr [TARGET+0x504],TARGET+4096
 mov dword ptr [ALIAS+0x504],TARGET+4096
.endif
.if CASE == 5
 mov dword ptr [TARGET+0x508],TARGET
 mov dword ptr [ALIAS+0x508],TARGET
.endif
.if CASE == 6
 mov dword ptr [TARGET+0x508],0x3fff000
 mov dword ptr [ALIAS+0x508],0x3fff000
.endif
.if CASE == 7
 mov dword ptr [0x3f01000+((TARGET-0x1c00000)/4096)*4],0
.endif
.if CASE == 8
 mov word ptr [TARGET+POST_OFFSET],0x0b0f
.endif
.if CASE == 9
 mov dword ptr [TARGET+0x414],0
 mov dword ptr [ALIAS+0x414],0
.endif
 mov eax,cr4
 or eax,0x10
 mov cr4,eax
 mov eax,0x3f00000
 mov cr3,eax
 mov eax,cr0
 or eax,0x80000000
 mov cr0,eax
 jmp paged
paged:
 mov al,'B'
 out 0xe9,al
 jmp TARGET
fixture_fault:
 cli
 mov dword ptr [fixture_result],0xbad
fixture_fault_loop:
 hlt
 jmp fixture_fault_loop
.balign 8
gdt: .quad 0,0x00cf9a000000ffff,0x00cf92000000ffff
gdtr: .word 23
.long gdt
idtr: .word 2047
.long idt
fixture_result: .long 0
idt: .fill 2048,1,0
page: .incbin "page.bin"
