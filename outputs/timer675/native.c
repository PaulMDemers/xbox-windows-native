/* SPDX-License-Identifier: GPL-2.0-or-later
 * HOST-ONLY terminal adapter. Not hooked to firmware or packaged as an XBE.
 */
#include "probe.h"
extern void irq_hold669(void) __attribute__((noreturn));
struct record675 Record675;
unsigned Return675;
static uint32_t flags(void *p){
 uint32_t f;(void)p;__asm__ __volatile__("pushfl; popl %0":"=r"(f)::"memory");return f;
}
static uint32_t ticks(void *p){
 uint32_t v;(void)p;__asm__ __volatile__("inl %1,%0":"=a"(v):"d"((uint16_t)0x8008));return v;
}
static unsigned input(void *p,unsigned port,unsigned width){
 (void)p;
 if(width==1){uint8_t v;__asm__ __volatile__("inb %1,%0":"=a"(v):"d"((uint16_t)port));return v;}
 else{uint16_t v;__asm__ __volatile__("inw %1,%0":"=a"(v):"d"((uint16_t)port));return v;}
}
static void output(void *p,unsigned port,unsigned width,unsigned v){
 (void)p;
 if(width==1)__asm__ __volatile__("outb %0,%1"::"a"((uint8_t)v),"d"((uint16_t)port));
 else __asm__ __volatile__("outw %0,%1"::"a"((uint16_t)v),"d"((uint16_t)port));
}
__attribute__((noreturn)) void terminal675(void){
 const struct ops675 ops={0,flags,ticks,input,output};
 Return675=probe675(&ops,&Record675,1000);
 irq_hold669();
}
typedef char record675_size[sizeof(struct record675)==404?1:-1];
