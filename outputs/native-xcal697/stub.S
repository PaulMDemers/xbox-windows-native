/* SPDX-License-Identifier: GPL-2.0-or-later
 * Relocatable diagnostic page. No kernel calls, encoder configuration or firmware entry. One bounded Xcalibur register read; protocol from authored689/xcal_bus.c.
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
.globl _stub697_probe,_stub697_render,_stub697_pci,_stub697_colors,_stub697_bar
.globl _stub697_start,_stub697_flat,_stub697_fault,_stub697_hold,_stub697_code_end,_stub697_end,_stub697_post
_stub697_start:
 call 1f
1:pop %ebp
 sub $(1b-_stub697_start),%ebp
 cmpl $0x584e0697,0x500(%ebp)
 jne _stub697_fault
 cmp %ebp,0x504(%ebp)
 jne _stub697_fault
 test $4095,%ebp
 jne _stub697_fault
 cmp $0x1000000,%ebp
 jb _stub697_fault
 cmp $0x1fff000,%ebp
 ja _stub697_fault
 cmpl $3686400,0x50c(%ebp)
 jne _stub697_fault
 mov 0x508(%ebp),%edi
 test $4095,%edi
 jne _stub697_fault
 cmp $(0x4000000-3686400),%edi
 ja _stub697_fault
 lea 4096(%ebp),%eax
 cmp %eax,%edi
 jae 2f
 lea 3686400(%edi),%eax
 cmp %eax,%ebp
 jb _stub697_fault
2:mov %cr0,%eax
 mov %eax,0x544(%ebp)
 and $0x80000001,%eax
 cmp $0x80000001,%eax
 jne _stub697_fault
 mov %cr4,%eax
 mov %eax,0x54c(%ebp)
 test $0x20,%eax
 jne _stub697_fault
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
_stub697_flat:
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
_stub697_post:
 xor %eax,%eax
 mov %eax,%cr3
 lea 4096(%ebp),%eax
 cmp %eax,%esp
 jne _stub697_fault
 mov %cr0,%eax
 mov %eax,0x544(%ebp)
 and $0x80000001,%eax
 cmp $1,%eax
 jne _stub697_fault
 mov %cr3,%eax
 mov %eax,0x548(%ebp)
 mov %cr4,%eax
 mov %eax,0x54c(%ebp)
 pushfl
 pop %eax
 mov %eax,0x550(%ebp)
 test $0x200,%eax
 jne _stub697_fault
 mov %cs,%ax
 movzwl %ax,%eax
 mov %eax,0x554(%ebp)
 cmp $0x10,%eax
 jne _stub697_fault
 mov %ds,%ax
 cmp $0x18,%ax
 jne _stub697_fault
 mov %ss,%ax
 cmp $0x18,%ax
 jne _stub697_fault
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
_stub697_probe:
 /* Native controller preflight before one owned transaction.
  * CF8 selection is restored before any refusal branch. Raw status remains
  * ffffffff (unread) until PCI identity and mapping are qualified. */
 movl $0xffffffff,0x5b0(%ebp)
 movl $0xffffffff,0x5b4(%ebp)
 movl $0xffffffff,0x5b8(%ebp)
 movl $0xffffffff,0x5bc(%ebp)
 movl $0,0x5c4(%ebp)
 movl $0xffffffff,0x5c8(%ebp)
 mov $0xcf8,%dx
 inl %dx,%eax
 mov %eax,0x5a0(%ebp)
 mov $0x80000900,%eax
 call _stub697_pci
 mov %eax,0x5a4(%ebp)
 mov $0x80000904,%eax
 call _stub697_pci
 mov %eax,0x5a8(%ebp)
 mov $0x80000914,%eax
 call _stub697_pci
 mov %eax,0x5ac(%ebp)
 mov 0x5a0(%ebp),%eax
 outl %eax,%dx
 mov $2,%ebx
 cmpl $0x1b410de,0x5a4(%ebp)
 jne _stub697_render
 mov $3,%ebx
 testl $1,0x5a8(%ebp)
 jz _stub697_render
 mov $4,%ebx
 cmpl $0xc001,0x5ac(%ebp)
 jne _stub697_render
 /* Blue second bar means native probe is evaluating/issuing its one read. */
 mov $0x0000ff,%eax
 call _stub697_bar
 sfence
 wbinvd
 mov $0xc000,%dx
 xor %eax,%eax
 inw %dx,%ax
 mov %eax,0x5b0(%ebp)
 mov $5,%ebx
 test $0x800,%eax
 jnz _stub697_render
 mov $6,%ebx
 test $0x36,%eax
 jnz _stub697_render
 /* Entry clean: one block read from address70, register00; no encoder write. */
 movl $5,0x540(%ebp)
 mov $0xc004,%dx
 mov $0xe1,%al
 outb %al,%dx
 mov $0xc008,%dx
 mov $0,%al
 outb %al,%dx
 mov $0xc002,%dx
 mov $0x0d,%al
 outb %al,%dx
 mov $0xc000,%dx
 mov $100000,%ecx
9:xor %eax,%eax
 inb %dx,%al
 mov %eax,0x5b4(%ebp)
 incl 0x5c4(%ebp)
 test $0x36,%al
 jnz 10f
 loop 9b
 /* Timeout never acknowledges or retries, even if the final read sees status. */
 mov $7,%ebx
 xor %eax,%eax
 inw %dx,%ax
 mov %eax,0x5bc(%ebp)
 jmp _stub697_render
10:mov $8,%ebx
 test $0x26,%al
 jnz 11f
 mov $10,%ebx
 mov $0xc006,%dx
 xor %eax,%eax
 inw %dx,%ax
 mov %eax,0x5c8(%ebp)
 cmp $4,%eax
 jne 11f
 /* FIFO is read only for exactly4 bytes; pack wire order low byte first. */
 mov $0xc009,%dx
 xor %esi,%esi
 mov $4,%ecx
13:xor %eax,%eax
 inb %dx,%al
 ror $8,%esi
 shl $24,%eax
 or %eax,%esi
 loop 13b
 mov %esi,0x5b8(%ebp)
 mov $1,%ebx
11:mov $0xc000,%dx
 mov 0x5b4(%ebp),%eax
 and $0x36,%eax
 outw %ax,%dx
 xor %eax,%eax
 inw %dx,%ax
 mov %eax,0x5bc(%ebp)
 test $0x836,%eax
 jz 12f
 mov $9,%ebx
 jmp _stub697_render
12: /* Retain success, bus-error or length-error result; raw data is not an ID claim. */
_stub697_render:
 mov %ebx,0x5c0(%ebp)
 lea (_stub697_colors-_stub697_start)(%ebp),%eax
 mov (%eax,%ebx,4),%eax
 call _stub697_bar
 /* Ten rows, MSB left: ID, command/status, BAR, entry, last poll, data,
  * final status, result code, poll count and returned block length.
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
 jmp _stub697_hold
_stub697_bar:
 mov 0x508(%ebp),%edi
 add $491552,%edi /* y96 x8 */
 mov $64,%edx
4:mov $1264,%ecx
 rep stosl
 add $64,%edi
 dec %edx
 jnz 4b
 ret
_stub697_pci:
 outl %eax,%dx
 add $4,%dx
 inl %dx,%eax
 sub $4,%dx
 ret
.balign 4
_stub697_colors:
 .long 0,0xff00,0xff0000,0xffff,0xffff00,0xff8000,0xff00ff,0x0000ff,0xff4000,0xffffff,0x8000ff
_stub697_hold:
 hlt
 jmp _stub697_hold
_stub697_fault:
 cli
 hlt
 jmp _stub697_fault
_stub697_code_end:
.org 4096,0
_stub697_end:
