/* SPDX-License-Identifier: GPL-2.0-or-later
 * Relocatable diagnostic page. No kernel calls, encoder configuration or firmware entry. Read-only native GPU context; no mode programming.
 * Initial access uses the normal flat nxdk kernel ABI. Own tables installed
 * before paging removal. Own stack exists at the same linear address in both copies.
 */
.def @feat.00;
.scl 3;
.type 0;
.endef
.globl @feat.00
.set @feat.00,1
.text
.code32
.balign 16
.globl _stub703_probe,_stub703_render,_stub703_pci,_stub703_colors,_stub703_bar
.globl _stub703_start,_stub703_flat,_stub703_fault,_stub703_hold,_stub703_code_end,_stub703_end,_stub703_post
_stub703_start:
 call 1f
1:pop %ebp
 sub $(1b-_stub703_start),%ebp
 cmpl $0x584e0703,0x500(%ebp)
 jne _stub703_fault
 cmp %ebp,0x504(%ebp)
 jne _stub703_fault
 test $4095,%ebp
 jne _stub703_fault
 cmp $0x1000000,%ebp
 jb _stub703_fault
 cmp $0x1fff000,%ebp
 ja _stub703_fault
 cmpl $1228800,0x50c(%ebp)
 jne _stub703_fault
 mov 0x508(%ebp),%edi
 test $4095,%edi
 jne _stub703_fault
 cmp $(0x4000000-1228800),%edi
 ja _stub703_fault
 lea 4096(%ebp),%eax
 cmp %eax,%edi
 jae 2f
 lea 1228800(%edi),%eax
 cmp %eax,%ebp
 jb _stub703_fault
2:mov %cr0,%eax
 mov %eax,0x544(%ebp)
 and $0x80000001,%eax
 cmp $0x80000001,%eax
 jne _stub703_fault
 mov %cr4,%eax
 mov %eax,0x54c(%ebp)
 test $0x20,%eax
 jne _stub703_fault
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
 lgdt 0x4e0(%ebp)
 ljmp *0x4e8(%ebp)
_stub703_flat:
 mov $0x18,%ax
 mov %ax,%ds
 mov %ax,%es
 mov %ax,%ss
 lea 4096(%ebp),%esp
 xor %eax,%eax
 mov %ax,%fs
 mov %ax,%gs
 lidt 0x4f0(%ebp)
 mov %cr0,%eax
 and $0x7fffffff,%eax
 mov %eax,%cr0
_stub703_post:
 xor %eax,%eax
 mov %eax,%cr3
 lea 4096(%ebp),%eax
 cmp %eax,%esp
 jne _stub703_fault
 mov %cr0,%eax
 mov %eax,0x544(%ebp)
 and $0x80000001,%eax
 cmp $1,%eax
 jne _stub703_fault
 mov %cr3,%eax
 mov %eax,0x548(%ebp)
 mov %cr4,%eax
 mov %eax,0x54c(%ebp)
 pushfl
 pop %eax
 mov %eax,0x550(%ebp)
 test $0x200,%eax
 jne _stub703_fault
 mov %cs,%ax
 movzwl %ax,%eax
 mov %eax,0x554(%ebp)
 cmp $0x10,%eax
 jne _stub703_fault
 mov %ds,%ax
 cmp $0x18,%ax
 jne _stub703_fault
 mov %ss,%ax
 cmp $0x18,%ax
 jne _stub703_fault
 movl $2,0x540(%ebp)
 /* GREEN is written only after the post-paging checks. */
 mov 0x508(%ebp),%edi
 add $20512,%edi
 mov $72,%edx
 mov $0xff00,%eax
3:mov $624,%ecx
 rep stosl
 add $64,%edi
 dec %edx
 jnz 3b
 sfence
 wbinvd
 movl $3,0x540(%ebp)
_stub703_probe:
 /* GPU PCI admission before bounded read-only MMIO/indexed-register capture.
  * No SMBus, timer, encoder, clock, output-enable or interrupt-status writes. */
 lea 0x5a4(%ebp),%edi
 mov $10,%ecx
 mov $0xffffffff,%eax
 rep stosl
 mov $0xcf8,%dx
 inl %dx,%eax
 mov %eax,0x5a0(%ebp)
 mov $0x80010000,%eax
 call _stub703_pci
 mov %eax,0x5a4(%ebp)
 mov $0x80010004,%eax
 call _stub703_pci
 mov %eax,0x5a8(%ebp)
 mov $0x80010010,%eax
 call _stub703_pci
 mov %eax,0x5ac(%ebp)
 mov 0x5a0(%ebp),%eax
 outl %eax,%dx
 mov $2,%ebx
 cmpl $0x02a010de,0x5a4(%ebp)
 jne _stub703_render
 mov $3,%ebx
 testl $2,0x5a8(%ebp)
 jz _stub703_render
 mov $4,%ebx
 mov 0x5ac(%ebp),%eax
 and $0xfffffff7,%eax /* permit prefetchable bit only; memory32 BAR */
 cmp $0xfd000000,%eax
 jne _stub703_render
 mov 0xfd680508,%eax
 mov %eax,0x5b4(%ebp)
 mov 0xfd68050c,%eax
 mov %eax,0x5b8(%ebp)
 mov 0xfd680880,%eax
 mov %eax,0x5bc(%ebp)
 movzbl 0xfd6013d4,%ecx
 movb $0x25,0xfd6013d4
 movzbl 0xfd6013d5,%eax
 mov %eax,0x5b0(%ebp)
 movb $0x13,0xfd6013d4
 movzbl 0xfd6013d5,%eax
 movb $0x19,0xfd6013d4
 movzbl 0xfd6013d5,%edx
 shl $8,%edx
 or %edx,%eax
 movb $0x28,0xfd6013d4
 movzbl 0xfd6013d5,%edx
 shl $16,%edx
 or %edx,%eax
 movb $0x39,0xfd6013d4
 movzbl 0xfd6013d5,%edx
 shl $24,%edx
 or %edx,%eax
 mov %cl,0xfd6013d4
 mov %eax,0x5c0(%ebp)
 mov 0xfd600800,%eax
 mov %eax,0x5c4(%ebp)
 mov 0xfd100200,%eax
 mov %eax,0x5c8(%ebp)
 mov $1,%ebx
_stub703_render:
 mov %ebx,0x5cc(%ebp)
 lea (_stub703_colors-_stub703_start)(%ebp),%eax
 mov (%eax,%ebx,4),%eax
 call _stub703_bar
 /* Ten MSB-left rows: GPU PCI ID, command/status, BAR0, CRTC25,
  * VPLL, PLL selection, output control, packed CRTC13/19/28/39,
  * framebuffer start and PFB configuration. White1/black0. */
 xor %esi,%esi
5:mov 0x5a4(%ebp,%esi,4),%ebx
 mov %esi,%eax
 imul $28,%eax,%eax
 add $184,%eax
 imul $2560,%eax,%eax
 add $256,%eax
 add 0x508(%ebp),%eax
 mov %eax,%edi
 mov $32,%edx
6:push %edx
 push %edi
 xor %eax,%eax
 test $0x80000000,%ebx
 jz 7f
 mov $0xffffff,%eax
7:mov $12,%edx
8:mov $12,%ecx
 rep stosl
 add $2512,%edi
 dec %edx
 jnz 8b
 pop %edi
 add $64,%edi
 pop %edx
 shl $1,%ebx
 dec %edx
 jnz 6b
 inc %esi
 cmp $10,%esi
 jne 5b
 sfence
 wbinvd
 movl $4,0x540(%ebp)
 jmp _stub703_hold
_stub703_bar:
 mov 0x508(%ebp),%edi
 add $245792,%edi /* y96 x8 */
 mov $64,%edx
4:mov $624,%ecx
 rep stosl
 add $64,%edi
 dec %edx
 jnz 4b
 ret
_stub703_pci:
 outl %eax,%dx
 add $4,%dx
 inl %dx,%eax
 sub $4,%dx
 ret
.balign 4
_stub703_colors:
 .long 0,0xff00,0xff0000,0xffff,0xffff00,0xff8000,0xff00ff,0x0000ff,0xff4000,0xffffff,0x8000ff
_stub703_hold:
 hlt
 jmp _stub703_hold
_stub703_fault:
 cli
 hlt
 jmp _stub703_fault
_stub703_code_end:
.org 4096,0
_stub703_end:
