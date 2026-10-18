/* SPDX-License-Identifier: MIT -- host register/flags preservation probe. */
.intel_syntax noprefix
.code32
.text
.global invoke_test
invoke_test:
    pushfd
    pushad
    push dword ptr [test_record]
    mov [expected_esp], esp
    mov eax, 0x11111111
    mov ebx, 0x22222222
    mov ecx, 0x33333333
    mov edx, 0x44444444
    mov esi, 0x55555555
    mov edi, 0x66666666
    mov ebp, 0x77777777
    push 0xed7
    popfd
    pushfd
    pop dword ptr [before_flags]
    call marker_guarded
    pushfd
    pop dword ptr [after_flags]
    pushad
    cld
    mov esi, esp
    mov edi, offset after_regs
    mov ecx, 8
    rep movsd
    popad
    add esp, 4
    popad
    popfd
    ret
.section .note.GNU-stack,"",@progbits
