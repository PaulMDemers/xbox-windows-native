/* Owned dump-only selector for the pinned NT5 ATAPI image.
 * stdcall(adapter, SRB); tail calls preserve the original arguments.
 * Capability and command fields are those used by this image's normal path.
 * WRITE(10) is limited to 32-bit sector addresses (2 TiB at 512 bytes/sector).
 */
.intel_syntax noprefix
.section .text
.global dispatch
dispatch:
    mov edx, [esp + 8]
    cmp byte ptr [edx + 0x30], 0x2a
    jne reject
    movzx ecx, byte ptr [edx + 6]
    cmp ecx, 4
    jae reject
    mov eax, [edx + 0x10]
    test eax, eax
    jz reject
    test eax, 511
    jnz reject
    cmp eax, 131072
    ja reject
    shr eax, 9
    dec eax
    mov edx, [edx + 0x32]
    bswap edx
    add eax, edx
    jc reject
    mov edx, [esp + 4]
    test byte ptr [edx + ecx*4 + 0xb2], 0x40
    jz legacy
    imul ecx, ecx, 0x3c
    cmp byte ptr [edx + ecx + 0x910], 0x39
    jne reject
    jmp extended_dispatch
legacy:
    cmp eax, 0x0fffffff
    ja reject
    jmp legacy_dispatch
reject:
    mov eax, 6
    ret 8
