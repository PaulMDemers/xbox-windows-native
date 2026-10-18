/* SPDX-License-Identifier: MIT
 * Read-only privileged CPU observation, not a mapping or boot fix.
 * EDI=fresh owned160-byte buffer, ECX=capacity exactly160. Caller must own and
 * validate its destination; this is not an arbitrary-pointer API. No kernel,
 * page table, descriptor contents or physical-memory dereference occurs here.
 * Invalid header/capacity or already-completed record => no writes.
 * All caller general registers/EFLAGS are restored. No CLI/STI/CLD or CR writes.
 */
.intel_syntax noprefix
.code32
.text
.global capture489
capture489:
    pushfd
    pushad
    cmp ecx,160
    jne capture_return
    cmp dword ptr [edi],0x39383443
    jne capture_return
    cmp dword ptr [edi+4],1
    jne capture_return
    cmp dword ptr [edi+8],160
    jne capture_return
    cmp dword ptr [edi+12],1
    jb capture_return
    cmp dword ptr [edi+12],2
    ja capture_return
    cmp dword ptr [edi+16],0x48900101
    jne capture_return
    cmp dword ptr [edi+132],0
    jne capture_return
    cmp dword ptr [edi+152],0
    jne capture_return
    cmp dword ptr [edi+156],0
    jne capture_return
    mov eax,[esp+32]
    mov [edi+20],eax
    rdtsc
    mov [edi+80],eax
    mov [edi+84],edx
    mov eax,cr0
    mov [edi+24],eax
    mov eax,cr2
    mov [edi+28],eax
    mov eax,cr3
    mov [edi+32],eax
    mov eax,cr4
    mov [edi+36],eax
    mov ax,cs
    mov [edi+40],ax
    mov ax,ds
    mov [edi+42],ax
    mov ax,es
    mov [edi+44],ax
    mov ax,fs
    mov [edi+46],ax
    mov ax,gs
    mov [edi+48],ax
    mov ax,ss
    mov [edi+50],ax
    sldt ax
    mov [edi+52],ax
    str ax
    mov [edi+54],ax
    sgdt [edi+56]
    sidt [edi+64]
    lea eax,[esp+36]
    mov [edi+72],eax
    mov eax,[esp+36]
    mov [edi+76],eax
    mov eax,cr0
    mov [edi+96],eax
    mov eax,cr2
    mov [edi+100],eax
    mov eax,cr3
    mov [edi+104],eax
    mov eax,cr4
    mov [edi+108],eax
    sgdt [edi+112]
    sidt [edi+120]
    rdtsc
    mov [edi+88],eax
    mov [edi+92],edx
    mov dword ptr [edi+152],0x454e4f44
    mov dword ptr [edi+156],0x48900101
    mov dword ptr [edi+132],1
capture_return:
    popad
    popfd
    ret
