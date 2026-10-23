/* SPDX-License-Identifier: GPL-2.0-or-later
 * HOST-ONLY candidate. This is an explicit POST-CAPTURE transport effect.
 * No POPF/STI, control-register/PIC/APIC writes, allocator, or firmware borrow.
 * The original flag sample remains distinct from the transport sample.
 */
.text
.globl irq_enter669
.type irq_enter669,@function
irq_enter669:
 pushfl
 popl %eax
 cli
 pushfl
 popl %edx
 movl 8(%esp),%ecx
 movl %eax,(%ecx)
 movl 12(%esp),%ecx
 movl %edx,(%ecx)
 xorl %eax,%eax
 ret
.size irq_enter669,.-irq_enter669
.globl irq_flags669
.type irq_flags669,@function
irq_flags669:
 pushfl
 popl %eax
 ret
.size irq_flags669,.-irq_flags669
.globl irq_hold669
.type irq_hold669,@function
irq_hold669:
 cli
1:
 hlt
 jmp 1b
.size irq_hold669,.-irq_hold669
.section .note.GNU-stack,"",@progbits
