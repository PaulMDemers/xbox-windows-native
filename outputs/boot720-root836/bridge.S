/* SPDX-License-Identifier: GPL-2.0-or-later
 *32KiB owned-page bridge. All writes after paging-off are to owned RAM, PCI
 * selector-restoration, or the separately checked transaction. No kernel call.
 */
.text
.code32
.balign 16
.globl bridge_start,bridge_flat,bridge_post,bridge_hold,bridge_fault,bridge_end,bridge_code_end
bridge_start:
 call 1f
1:pop %ebp
 sub $(1b-bridge_start),%ebp
 cmpl $0x584e0705,0x840(%ebp)
 jne bridge_fault
 cmp %ebp,0x844(%ebp)
 jne bridge_fault
 test $4095,%ebp
 jne bridge_fault
 cmp $0x1000000,%ebp
 jb bridge_fault
 cmp $0x1ff6000,%ebp
 ja bridge_fault
 cmpl $3686400,0x84c(%ebp)
 jne bridge_fault
 mov 0x848(%ebp),%edi
 test $4095,%edi
 jne bridge_fault
 cmp $0x2800000,%edi
 jb bridge_fault
 cmp $(0x4000000-3686400),%edi
 ja bridge_fault
 cmp $0x2800000,%edi
 jae 2f
 lea 3686400(%edi),%eax
 cmp $0x2600000,%eax
 ja bridge_fault
2: mov %cr0,%eax
 and $0x80000001,%eax
 cmp $0x80000001,%eax
 jne bridge_fault
 mov %cr4,%eax
 test $0x20,%eax
 jne bridge_fault
 call bridge_check
 cmp 0x854(%ebp),%eax
 jne bridge_fault
 /* Touch the endpoints of the 4352-byte stack above IDT while paging is still active. Kernel admission
  * separately byte-compares the copies and validates all page mappings. */
 mov 0x8f00(%ebp),%eax
 mov 0x9ffc(%ebp),%eax
 movl $1,0x880(%ebp)
 cli
 cld
 sfence
 mov %cr0,%eax
 or $0x40000000,%eax
 and $0xdfffffff,%eax
 mov %eax,%cr0
 wbinvd
 lgdt 0x820(%ebp)
 ljmp *0x828(%ebp)
bridge_flat:
 mov $0x18,%ax
 mov %ax,%ds
 mov %ax,%es
 mov %ax,%ss
 lea 0xa000(%ebp),%esp
 xor %eax,%eax
 mov %ax,%fs
 mov %ax,%gs
 lidt 0x830(%ebp)
 mov %cr0,%eax
 and $0x7fffffff,%eax
 mov %eax,%cr0
bridge_post:
 xor %eax,%eax
 mov %eax,%cr3
 call bridge_check
 cmp 0x854(%ebp),%eax
 jne bridge_fault
 mov %cr0,%eax
 mov %eax,0x884(%ebp)
 and $0xe0000001,%eax
 cmp $0x40000001,%eax
 jne bridge_fault
 mov %cr3,%eax
 mov %eax,0x888(%ebp)
 mov %cr4,%eax
 mov %eax,0x88c(%ebp)
 pushfl
 pop %eax
 mov %eax,0x890(%ebp)
 test $0x200,%eax
 jne bridge_fault
 mov %cs,%ax
 cmp $0x10,%ax
 jne bridge_fault
 mov %ds,%ax
 cmp $0x18,%ax
 jne bridge_fault
 mov %ss,%ax
 cmp $0x18,%ax
 jne bridge_fault
 /* Copy only the checked, independently allocated firmware span. */
 mov 0x858(%ebp),%esi
 test $4095,%esi
 jne bridge_fault
 cmp $0x210000,%esi
 jb bridge_fault
 mov 0x85c(%ebp),%ecx
 test $3,%ecx
 jne bridge_fault
 cmp $0x1000,%ecx
 jb bridge_fault
 cmp $0xf0000,%ecx
 ja bridge_fault
 mov %esi,%eax
 add %ecx,%eax
 jc bridge_fault
 cmp $0x2000000,%eax
 ja bridge_fault
 /* Source must not overlap the live bridge/stack. */
 lea 0xa000(%ebp),%edx
 cmp %edx,%esi
 jae copy_source_safe
 cmp %ebp,%eax
 ja bridge_fault
copy_source_safe:
 push %esi
 push %ecx
 shr $2,%ecx
 xor %eax,%eax
copy_source_sum:
 add (%esi),%eax
 add $4,%esi
 loop copy_source_sum
 pop %ecx
 pop %esi
 cmp 0x860(%ebp),%eax
 jne bridge_fault
 movl $2,0x880(%ebp)
 mov $0x02600000,%edi
 shr $2,%ecx
 rep movsl
 mov $0x02600000,%esi
 mov 0x85c(%ebp),%ecx
 shr $2,%ecx
 xor %eax,%eax
copy_target_sum:
 add (%esi),%eax
 add $4,%esi
 loop copy_target_sum
 cmp 0x860(%ebp),%eax
 jne bridge_fault
 movl $3,0x880(%ebp)
 sfence
 wbinvd
 mov $0x02600000,%eax
 jmp *%eax
bridge_hold:
 cli
 hlt
 jmp bridge_hold
bridge_fault:
 cli
 hlt
 jmp bridge_fault
bridge_check:
 push %esi
 xor %eax,%eax
 xor %esi,%esi
5:cmp $0x854,%esi
 je 6f
 cmp $0x880,%esi
 jb 7f
 cmp $0x900,%esi
 jb 6f
7:add (%ebp,%esi),%eax
6:add $4,%esi
 cmp $0x8f00,%esi
 jb 5b
 pop %esi
 ret
bridge_code_end:
.org 2304,0
bridge_end:
