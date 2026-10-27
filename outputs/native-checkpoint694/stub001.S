/* SPDX-License-Identifier: MIT
 * Relocatable diagnostic page. No kernel calls, ports, encoder or firmware entry.
 * Initial access uses the normal flat nxdk kernel ABI. Own tables installed
 * before paging removal. Own stack exists at the same linear address in both copies.
 */
.text
.code32
.balign 16
.globl _stub694_start,_stub694_flat,_stub694_fault,_stub694_hold,_stub694_code_end,_stub694_end,_stub694_post
_stub694_start:
 call 1f
1:pop %ebp
 sub $(1b-_stub694_start),%ebp
 cmpl $0x584e0694,0x500(%ebp)
 jne _stub694_fault
 cmp %ebp,0x504(%ebp)
 jne _stub694_fault
 test $4095,%ebp
 jne _stub694_fault
 cmp $0x1000000,%ebp
 jb _stub694_fault
 cmp $0x1fff000,%ebp
 ja _stub694_fault
 cmpl $3686400,0x50c(%ebp)
 jne _stub694_fault
 mov 0x508(%ebp),%edi
 test $4095,%edi
 jne _stub694_fault
 cmp $(0x4000000-3686400),%edi
 ja _stub694_fault
 lea 4096(%ebp),%eax
 cmp %eax,%edi
 jae 2f
 lea 3686400(%edi),%eax
 cmp %eax,%ebp
 jb _stub694_fault
2:mov %cr0,%eax
 mov %eax,0x544(%ebp)
 and $0x80000001,%eax
 cmp $0x80000001,%eax
 jne _stub694_fault
 mov %cr4,%eax
 mov %eax,0x54c(%ebp)
 test $0x20,%eax
 jne _stub694_fault
 mov %cr3,%eax
 mov %eax,0x548(%ebp)
 pushfl
 pop %eax
 mov %eax,0x550(%ebp)
 movl $1,0x540(%ebp)
 /* Irreversible diagnostic transition. No kernel service after this CLI.
  * Cache-disable, invalidate, flat descriptors and paging-off are explicit. */
 cli
 cld
 sfence
 mov %cr0,%eax
 or $0x40000000,%eax
 and $0xdfffffff,%eax
 mov %eax,%cr0
 wbinvd
 lgdt 0x420(%ebp)
 ljmp *0x428(%ebp)
_stub694_flat:
 mov $0x18,%ax
 mov %ax,%ds
 mov %ax,%es
 mov %ax,%ss
 lea 4096(%ebp),%esp
 xor %eax,%eax
 mov %ax,%fs
 mov %ax,%gs
 lidt 0x430(%ebp)
 mov %cr0,%eax
 and $0x7fffffff,%eax
 mov %eax,%cr0
_stub694_post:
 xor %eax,%eax
 mov %eax,%cr3
 lea 4096(%ebp),%eax
 cmp %eax,%esp
 jne _stub694_fault
 mov %cr0,%eax
 mov %eax,0x544(%ebp)
 and $0x80000001,%eax
 cmp $1,%eax
 jne _stub694_fault
 mov %cr3,%eax
 mov %eax,0x548(%ebp)
 mov %cr4,%eax
 mov %eax,0x54c(%ebp)
 pushfl
 pop %eax
 mov %eax,0x550(%ebp)
 test $0x200,%eax
 jne _stub694_fault
 mov %cs,%ax
 movzwl %ax,%eax
 mov %eax,0x554(%ebp)
 cmp $0x10,%eax
 jne _stub694_fault
 mov %ds,%ax
 cmp $0x18,%ax
 jne _stub694_fault
 mov %ss,%ax
 cmp $0x18,%ax
 jne _stub694_fault
 movl $2,0x540(%ebp)
 /* GREEN is written only after the post-paging checks. */
 mov 0x508(%ebp),%edi
 add $40992,%edi
 mov $72,%edx
 mov $0x00ff00,%eax
3:mov $1264,%ecx
 rep stosl
 add $64,%edi
 dec %edx
 jnz 3b
 sfence
 wbinvd
 movl $3,0x540(%ebp)
_stub694_hold:
 hlt
 jmp _stub694_hold
_stub694_fault:
 cli
 hlt
 jmp _stub694_fault
_stub694_code_end:
.org 4096,0
_stub694_end:
