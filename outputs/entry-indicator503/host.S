/* SPDX-License-Identifier: MIT. Host fixture only; no Xbox API implementation. */
.intel_syntax noprefix
.code32
.text
.global host_invoke
host_invoke:
    push ebp
    push ebx
    push esi
    push edi
    lea eax, [esp-4]
    mov [expected_esp], eax
    push dword ptr [seed_flags]
    popfd
    pushfd
    pop dword ptr [expected_flags]
    mov eax, 0x11223344
    mov ecx, 0x22334455
    mov edx, 0x33445566
    mov ebx, 0x44556677
    mov ebp, 0x55667788
    mov esi, 0x66778899
    mov edi, 0x778899aa
    call entry503_gate
    pop edi
    pop esi
    pop ebx
    pop ebp
    ret
.section .note.GNU-stack,"",@progbits
