/* MIT. Independent exact instruction ranges for original controls. */
.text
.globl _arith619
.globl _arith_end619
_arith619:
 movl 4(%esp),%eax
 movl $65536,%ecx
1: imull $1664525,%eax,%eax
 addl $1013904223,%eax
 decl %ecx
 jnz 1b
 ret
_arith_end619:
.globl _copy619
.globl _copy_end619
_copy619:
 pushl %esi
 pushl %edi
 movl 12(%esp),%edi
 movl 16(%esp),%esi
 movl 20(%esp),%ecx
 cld
 rep movsl
 popl %edi
 popl %esi
 ret
_copy_end619:
