/* SPDX-License-Identifier: GPL-2.0-or-later
 * Relocatable diagnostic page. No kernel calls, encoder configuration or firmware entry. One bounded native timer observation; no SMBus access or encoder write.
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
.globl _stub699_probe,_stub699_render,_stub699_pci,_stub699_colors,_stub699_bar
.globl _stub699_start,_stub699_flat,_stub699_fault,_stub699_hold,_stub699_code_end,_stub699_end,_stub699_post
_stub699_start:
 call 1f
1:pop %ebp
 sub $(1b-_stub699_start),%ebp
 cmpl $0x584e0699,0x500(%ebp)
 jne _stub699_fault
 cmp %ebp,0x504(%ebp)
 jne _stub699_fault
 test $4095,%ebp
 jne _stub699_fault
 cmp $0x1000000,%ebp
 jb _stub699_fault
 cmp $0x1fff000,%ebp
 ja _stub699_fault
 cmpl $3686400,0x50c(%ebp)
 jne _stub699_fault
 mov 0x508(%ebp),%edi
 test $4095,%edi
 jne _stub699_fault
 cmp $(0x4000000-3686400),%edi
 ja _stub699_fault
 lea 4096(%ebp),%eax
 cmp %eax,%edi
 jae 2f
 lea 3686400(%edi),%eax
 cmp %eax,%ebp
 jb _stub699_fault
2:mov %cr0,%eax
 mov %eax,0x544(%ebp)
 and $0x80000001,%eax
 cmp $0x80000001,%eax
 jne _stub699_fault
 mov %cr4,%eax
 mov %eax,0x54c(%ebp)
 test $0x20,%eax
 jne _stub699_fault
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
_stub699_flat:
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
_stub699_post:
 xor %eax,%eax
 mov %eax,%cr3
 lea 4096(%ebp),%eax
 cmp %eax,%esp
 jne _stub699_fault
 mov %cr0,%eax
 mov %eax,0x544(%ebp)
 and $0x80000001,%eax
 cmp $1,%eax
 jne _stub699_fault
 mov %cr3,%eax
 mov %eax,0x548(%ebp)
 mov %cr4,%eax
 mov %eax,0x54c(%ebp)
 pushfl
 pop %eax
 mov %eax,0x550(%ebp)
 test $0x200,%eax
 jne _stub699_fault
 mov %cs,%ax
 movzwl %ax,%eax
 mov %eax,0x554(%ebp)
 cmp $0x10,%eax
 jne _stub699_fault
 mov %ds,%ax
 cmp $0x18,%ax
 jne _stub699_fault
 mov %ss,%ax
 cmp $0x18,%ax
 jne _stub699_fault
 movl $2,0x540(%ebp)
 /* GREEN is written only after the post-paging checks. */
 mov 0x508(%ebp),%edi
 add $40992,%edi
 mov $72,%edx
 mov $0xff00,%eax
3:mov $1264,%ecx
 rep stosl
 add $64,%edi
 dec %edx
 jnz 3b
 sfence
 wbinvd
 movl $3,0x540(%ebp)
_stub699_probe:
 /* PCI identity preflight before one native timer observation.
  * CF8 selection is restored before any refusal branch. Raw status remains
  * ffffffff (unread) until PCI identity and mapping are qualified. */
 movl $0xffffffff,0x5b0(%ebp)
 movl $0xffffffff,0x5b4(%ebp)
 movl $0xffffffff,0x5b8(%ebp)
 movl $0,0x5bc(%ebp)
 movl $0xffffffff,0x5c4(%ebp)
 movl $0xffffffff,0x5c8(%ebp)
 mov $0xcf8,%dx
 inl %dx,%eax
 mov %eax,0x5a0(%ebp)
 mov $0x80000900,%eax
 call _stub699_pci
 mov %eax,0x5a4(%ebp)
 mov $0x80000904,%eax
 call _stub699_pci
 mov %eax,0x5a8(%ebp)
 mov $0x80000914,%eax
 call _stub699_pci
 mov %eax,0x5ac(%ebp)
 mov 0x5a0(%ebp),%eax
 outl %eax,%dx
 mov $2,%ebx
 cmpl $0x1b410de,0x5a4(%ebp)
 jne _stub699_render
 mov $3,%ebx
 testl $1,0x5a8(%ebp)
 jz _stub699_render
 mov $4,%ebx
 cmpl $0xc001,0x5ac(%ebp)
 jne _stub699_render
 /* Result remains blue while measuring; this is inherited scanout. */
 mov $0x0000ff,%eax
 call _stub699_bar
 sfence
 wbinvd
 rdtsc
 mov %eax,0x5cc(%ebp)
 mov %edx,0x5d0(%ebp)
 mov $0x8008,%dx
 inl %dx,%eax
 mov %eax,0x5b0(%ebp)
 mov %eax,0x5b4(%ebp)
 movl $0,0x5b8(%ebp)
 movl $1,0x5bc(%ebp)
 mov $100000,%ecx
_timer699_poll:
 inl %dx,%eax
 mov %eax,%edi
 sub 0x5b4(%ebp),%edi
 mov %eax,0x5b4(%ebp)
 sub 0x5b0(%ebp),%eax
 mov %eax,0x5b8(%ebp)
 incl 0x5bc(%ebp)
 mov $6,%ebx
 cmp $33750,%edi
 ja _timer699_finish
 cmp $33750,%eax
 ja _timer699_finish
 cmp $1688,%eax
 jae _timer699_success
 loop _timer699_poll
 mov $5,%ebx
 jmp _timer699_finish
_timer699_success:
 mov $1,%ebx
_timer699_finish:
 rdtsc
 sub 0x5cc(%ebp),%eax
 sbb 0x5d0(%ebp),%edx
 mov %eax,0x5c4(%ebp)
 mov %edx,0x5c8(%ebp)
_stub699_render:
 mov %ebx,0x5c0(%ebp)
 lea (_stub699_colors-_stub699_start)(%ebp),%eax
 mov (%eax,%ebx,4),%eax
 call _stub699_bar
 /* Ten rows, MSB left: PCI ID, command/status, BAR, first tick, last tick,
  * elapsed ticks, read count, result, TSC delta low, TSC delta high.
  * White=1, black=0; each32-bit row has32 cells,24px wide at32px pitch.
  * Rows y200+48r, height24, x128. No writes outside these boxes. */
 xor %esi,%esi
5:mov 0x5a4(%ebp,%esi,4),%ebx
 mov %esi,%eax
 imul $48,%eax,%eax
 add $200,%eax
 imul $5120,%eax,%eax
 add $512,%eax
 add 0x508(%ebp),%eax
 mov %eax,%edi
 mov $32,%edx
6:push %edx
 push %edi
 xor %eax,%eax
 test $0x80000000,%ebx
 jz 7f
 mov $0xffffff,%eax
7:mov $24,%edx
8:mov $24,%ecx
 rep stosl
 add $5024,%edi
 dec %edx
 jnz 8b
 pop %edi
 add $128,%edi
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
 jmp _stub699_hold
_stub699_bar:
 mov 0x508(%ebp),%edi
 add $491552,%edi /* y96 x8 */
 mov $64,%edx
4:mov $1264,%ecx
 rep stosl
 add $64,%edi
 dec %edx
 jnz 4b
 ret
_stub699_pci:
 outl %eax,%dx
 add $4,%dx
 inl %dx,%eax
 sub $4,%dx
 ret
.balign 4
_stub699_colors:
 .long 0,0xff00,0xff0000,0xffff,0xffff00,0xff8000,0xff00ff,0x0000ff,0xff4000,0xffffff,0x8000ff
_stub699_hold:
 hlt
 jmp _stub699_hold
_stub699_fault:
 cli
 hlt
 jmp _stub699_fault
_stub699_code_end:
.org 4096,0
_stub699_end:
