/* SPDX-License-Identifier: MIT. Linux i386 observation fixture only. */
.intel_syntax noprefix
.code32
.text
.global invoke510, capture510_begin, capture510_end
invoke510:
    pushfd
    pushad
    mov [saved_esp], esp
    push dword ptr [seed_flags]
    popfd
    pushfd
    pop dword ptr [expected_flags]
    mov edi, [seeds]
    mov esi, [seeds+4]
    mov ebp, [seeds+8]
    mov ebx, [seeds+12]
    mov edx, [seeds+16]
    mov ecx, [seeds+20]
    mov eax, [seeds+24]
    jmp 0x11100
/* No PC-relative instruction in this copied capture block. */
capture510_begin:
    pushfd
    pushad
    cld
    mov esi, esp
    mov edi, offset observed
    mov ecx, 9
    rep movsd
    mov esp, [saved_esp]
    popad
    popfd
    ret
capture510_end:
.section .note.GNU-stack,"",@progbits
