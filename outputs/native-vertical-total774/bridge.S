/* SPDX-License-Identifier: GPL-2.0-or-later
 *32KiB owned-page bridge. All writes after paging-off are to owned RAM, PCI
 * selector-restoration, or the separately checked transaction. No kernel call.
 */
.text
.code32
.balign 16
.globl bridge_start,bridge_flat,bridge_post,bridge_hold,bridge_fault,bridge_end,bridge_code_end,bridge_report
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
 cmp $0x1ff8000,%ebp
 ja bridge_fault
 cmpl $3686400,0x84c(%ebp)
 jne bridge_fault
 mov 0x848(%ebp),%edi
 test $4095,%edi
 jne bridge_fault
 cmp $0x2000000,%edi
 jb bridge_fault
 cmp $(0x4000000-3686400),%edi
 ja bridge_fault
 cmp $0x2800000,%edi
 jae 2f
 lea 3686400(%edi),%eax
 cmp $0x2600000,%eax
 ja bridge_fault
2:mov 0x850(%ebp),%eax
 sub %ebp,%eax
 sub $4096,%eax
 cmp $14080,%eax
 jae bridge_fault
 mov %cr0,%eax
 and $0x80000001,%eax
 cmp $0x80000001,%eax
 jne bridge_fault
 mov %cr4,%eax
 test $0x20,%eax
 jne bridge_fault
 call bridge_check
 cmp 0x854(%ebp),%eax
 jne bridge_fault
 /* Touch both stack pages while paging is still active. Kernel admission
  * separately byte-compares the copies and validates all page mappings. */
 mov 0x6000(%ebp),%eax
 mov 0x7ffc(%ebp),%eax
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
 lea 0x8000(%ebp),%esp
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
 movl $2,0x880(%ebp)
 mov $0x00ff00,%eax
 mov $8,%edx
 call bridge_bar
 /* Capture all three PCI functions; CF8 restored before any refusal. */
 mov $0xcf8,%dx
 inl %dx,%eax
 mov %eax,0x8a0(%ebp)
 lea pci_select-bridge_start(%ebp),%esi
 lea 0x8a4(%ebp),%edi
 mov $10,%ecx
3:lodsl
 outl %eax,%dx
 add $4,%dx
 inl %dx,%eax
 sub $4,%dx
 stosl
 loop 3b
 mov 0x8a0(%ebp),%eax
 outl %eax,%dx
 movl $1,0x8d0(%ebp)
 cmpl $0x02a010de,0x8a4(%ebp)
 jne bridge_refuse
 testl $2,0x8a8(%ebp)
 jz bridge_refuse
 mov 0x8ac(%ebp),%eax
 and $0xfffffff7,%eax
 cmp $0xfd000000,%eax
 jne bridge_refuse
 movl $2,0x8d0(%ebp)
 cmpl $0x01b410de,0x8b0(%ebp)
 jne bridge_refuse
 testl $1,0x8b4(%ebp)
 jz bridge_refuse
 cmpl $0xc001,0x8b8(%ebp)
 jne bridge_refuse
 /* LPC PM decode: retain both raw BAR0 and later-revision config84. Do not
  * change either. Require the exact distinct decode pair captured in706/707. */
 movl $3,0x8d0(%ebp)
 cmpl $0x01b210de,0x8bc(%ebp)
 jne bridge_refuse
 testl $1,0x8c0(%ebp)
 jz bridge_refuse
 cmpl $0,0x8c4(%ebp)
 jne bridge_refuse
 cmpl $0x8001,0x8c8(%ebp)
 jne bridge_refuse
4:movl $4,0x8d0(%ebp)
 /* Require the request to agree with the bridge's checked framebuffer. */
 mov 0x848(%ebp),%eax
 cmp %eax,0x5004(%ebp)
 jne bridge_refuse
 /* Recheck a bounded native PM interval at the kernel-qualified3375000Hz.
  * This proves progress, not independent frequency calibration. */
 movl $5,0x8d0(%ebp)
 mov $0x8008,%dx
 inl %dx,%eax
 mov %eax,0x8d8(%ebp)
 xor %ecx,%ecx
8:inl %dx,%eax
 inc %ecx
 mov %eax,0x8dc(%ebp)
 sub 0x8d8(%ebp),%eax
 mov %eax,0x8e0(%ebp)
 mov %ecx,0x8e4(%ebp)
 cmp $33750,%eax
 ja bridge_refuse
 cmp $1688,%eax
 jae 9f
 cmp $100000,%ecx
 jb 8b
 jmp bridge_refuse
9:mov $0x00ffff,%eax
 mov $48,%edx
 call bridge_bar
 lea 0x5100(%ebp),%eax
 push %eax
 pushl 0x848(%ebp)
 push $0xfd000000
 lea 0x5000(%ebp),%eax
 push %eax
 movl $3,0x880(%ebp)
 call *0x850(%ebp)
 add $16,%esp
 mov %eax,0x8d4(%ebp)
 lea 0x8000(%ebp),%eax
 cmp %eax,%esp
 jne bridge_fault
 cmpl $0xa5a5a5a5,0x5ffc(%ebp)
 jne bridge_fault
 movl $4,0x880(%ebp)
 /*774: call returned. Only the distinct horizontal checkpoint0x774 qualifies.
  * A GREEN second bar is checkpoint completion, not native mode success. */
 cmpl $0x774,0x8d4(%ebp)
 jne 12f
 mov $0x00ff00,%eax
 jmp 13f
12:mov $0xff8000,%eax
13:mov $48,%edx
 call bridge_bar
 call bridge_report
10:sfence
 wbinvd
bridge_hold:
 hlt
 jmp bridge_hold
bridge_refuse:
 lea status_colors-bridge_start(%ebp),%esi
 mov 0x8d0(%ebp),%ecx
 mov (%esi,%ecx,4),%eax
 mov $48,%edx
 call bridge_bar
 call bridge_report
 sfence
 wbinvd
 jmp bridge_hold
/* Only within the admitted3686400-byte1280x720 framebuffer.32 rows,1264 pixels.
 * Registers saved because later assembly and the transaction use EBP/base. */
bridge_bar:
 pushal
 imul $5120,%edx,%edi
 add 0x848(%ebp),%edi
 add $32,%edi
 mov $32,%ebx
11:mov $1264,%ecx
 rep stosl
 add $64,%edi
 dec %ebx
 jnz 11b
 popal
 ret
/*774 optical13x32-bit report. Called only from existing admitted-framebuffer
 * status paths; never from bridge_fault. No I/O or GPU register access.
 * Reads fixed owned metadata/result offsets and writes the checked framebuffer.
 * Row0 signature; later rows follow report_offsets. White1, black0, MSB left.
 */
bridge_report:
 pushal
 cld
 mov 0x848(%ebp),%edi
 add $(104*5120+112*4),%edi
 mov $536,%ebx
 mov $0xff808080,%eax
report_background:
 mov $1056,%ecx
 rep stosl
 add $896,%edi
 dec %ebx
 jnz report_background
 xor %ebx,%ebx
report_row:
 mov $0x7740000d,%eax
 test %ebx,%ebx
 jz report_value
 mov report_offsets-bridge_start(%ebp,%ebx,4),%esi
 mov (%ebp,%esi),%eax
report_value:
 mov %eax,%edx
 imul $40,%ebx,%edi
 add $120,%edi
 imul $5120,%edi,%edi
 add 0x848(%ebp),%edi
 add $512,%edi
 mov $32,%esi
report_bit:
 shl $1,%edx
 mov $0xff000000,%eax
 jnc report_color
 mov $0xffffffff,%eax
report_color:
 push %edi
 push %ebx
 mov $20,%ebx
report_square:
 mov $20,%ecx
 rep stosl
 add $5040,%edi
 dec %ebx
 jnz report_square
 pop %ebx
 pop %edi
 add $128,%edi
 dec %esi
 jnz report_bit
 inc %ebx
 cmp $13,%ebx
 jb report_row
 popal
 ret
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
 cmp $0x6000,%esi
 jb 5b
 pop %esi
 ret
.balign 4
status_colors:
 .long 0,0xff0000,0xffff00,0xff00ff,0xff8000,0xffffff,0xff8000
pci_select:
 .long 0x80010000,0x80010004,0x80010010
 .long 0x80000900,0x80000904,0x80000914
 .long 0x80000800,0x80000804,0x80000810,0x80000884
.balign 4
report_offsets:
 .long 0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x53a4,0x54b4,0x5514,0x5500,0x550c,0x5510
bridge_code_end:
.org 4096,0
bridge_end:
