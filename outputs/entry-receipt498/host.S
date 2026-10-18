/* SPDX-License-Identifier: MIT. Host fixture only; no Xbox API implementation. */
.intel_syntax noprefix
.code32
.text
.global host_invoke, entry498_continue
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
    call entry498_gate
    pop edi
    pop esi
    pop ebx
    pop ebp
    ret
entry498_continue:
    pushfd
    pushad
    cld
    mov esi, esp
    mov edi, offset observed
    mov ecx, 9
    rep movsd
    add dword ptr [observed+12], 4
    inc dword ptr [continued]
    add esp, 36
    ret
.section .note.GNU-stack,"",@progbits
