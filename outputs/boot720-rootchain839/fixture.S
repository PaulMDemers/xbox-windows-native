/* SPDX-License-Identifier: MIT. Diskless CPU fixture, no Xbox device model. */
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
 ljmp 8,fixture_flat
fixture_flat:
 mov ax,16
 mov ds,ax
 mov es,ax
 mov ss,ax
 mov fs,ax
 mov gs,ax
 mov esp,0x180000
 mov al,255
 out 0x21,al
 out 0xa1,al
 mov edi,offset idt
 mov ecx,256
 mov ebx,offset fixture_fault
1:mov eax,ebx
 and eax,0xffff
 or eax,0x80000
 stosd
 mov eax,ebx
 and eax,0xffff0000
 or eax,0x8e00
 stosd
 loop 1b
 lidt [idtr]
 mov edi,TARGET-4096
 mov ecx,12288
 mov eax,0x5a5a5a5a
 rep stosd
.if ALIAS != TARGET
 mov edi,ALIAS-4096
 mov ecx,22528
 rep stosd
.endif
 mov edi,0x3000000
 mov ecx,921600
 mov eax,0x20202020
 rep stosd
 mov esi,offset page
 mov edi,TARGET
 mov ecx,40960
 rep movsb
.if ALIAS != TARGET
 mov esi,offset page
 mov edi,ALIAS
 mov edx,10
2:mov ecx,4096
 rep movsb
 add edi,STRIDE-4096
 dec edx
 jnz 2b
.endif
 mov edi,0x3f00000
 mov ecx,2048
 xor eax,eax
 rep stosd
 mov edi,0x3f00000
 mov ecx,16
 mov eax,0x83
3:stosd
 add eax,0x400000
 loop 3b
 mov edi,0x3f01000
 mov ecx,1024
 mov eax,0x1c00003
4:stosd
 add eax,4096
 loop 4b
 mov dword ptr [0x3f00000+7*4],0x3f01003
 mov edi,0x3f01000+((TARGET-0x1c00000)/4096)*4
 mov eax,ALIAS+3
 mov ecx,10
5:stosd
 add eax,STRIDE
 loop 5b
.if CASE == 4
 mov dword ptr [TARGET+0x840],0
 mov dword ptr [ALIAS+0x840],0
.endif
.if CASE == 5
 mov dword ptr [TARGET+0x844],TARGET+4096
 mov dword ptr [ALIAS+0x844],TARGET+4096
.endif
.if CASE == 6
 mov dword ptr [TARGET+0x848],0x3fff000
 mov dword ptr [ALIAS+0x848],0x3fff000
.endif
.if CASE == 7
 mov dword ptr [0x3f01000+((TARGET-0x1c00000)/4096+3)*4],0
.endif
.if CASE == 8
 mov dword ptr [0x3f01000+((TARGET-0x1c00000)/4096+9)*4],0
.endif
.if CASE == 9
 xor dword ptr [TARGET+0x1500],1
.endif
.if CASE == 10
 xor dword ptr [ALIAS+0x1500],1
.endif
.if CASE == 11
 mov word ptr [TARGET+POST_OFFSET],0x0b0f
.endif
 mov edi,0x25ff000
 mov ecx,(0x102000/4)
 mov eax,0x55555555
 rep stosd
 mov esi,offset firmware
 mov edi,0x410000
 mov ecx,firmware_end-firmware
 rep movsb
.if CASE == 12
 xor dword ptr [0x410100],1
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
fixture_fault_loop:
 hlt
 jmp fixture_fault_loop
.balign 8
gdt:.quad 0,0xcf9a000000ffff,0xcf92000000ffff
gdtr:.word 23
.long gdt
idtr:.word 2047
.long idt
idt:.fill 2048,1,0
page:.incbin "page.bin"

firmware:.incbin "synthetic.bin"

firmware_end:
