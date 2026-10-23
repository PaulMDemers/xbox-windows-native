/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef TERMINAL669_H
#define TERMINAL669_H
#include <stdint.h>
#define BYTES669 772u
enum phase669 { EMPTY669,SEALING669,READY669,CLAIMED669,HELD669 };
enum status669 { OK669,BUSY669,ARG669,GUARD669,ADMISSION669,NO_USE669,
 SEND_FAILED669,UNSAFE669,PACKET_CHANGED669,IF_CHANGED669,INCONSISTENT669,SENT669 };
enum fault669 { F_GUARD669=1,F_PACKET669=2,F_IF669=4,F_UNSAFE669=8,F_RESULT669=16 };
/* Native adapter must copy actual NativeSend656/admission/result values.
 * A safe flag alone never proves delivery or permits ordinary continuation. */
struct outcome669 { unsigned admission,used,safe,completed,error,cleanup_error; };
struct record669 {
 volatile unsigned phase;
 unsigned status,faults,enter_called,send_called,flags_valid;
 uint32_t original_flags,transport_flags,final_flags;
 unsigned enter_error,send_error;
 struct outcome669 result;
 uint8_t original[BYTES669],transport[BYTES669];
};
struct ops669 {
 void *p;
 int (*enter)(void *,uint32_t *,uint32_t *);
 uint32_t (*flags)(void *);
 int (*send)(void *,const uint8_t *,unsigned,struct outcome669 *);
};
/* Caller owns zero-initialized storage and supplies an already validated,
 * complete post-capture encoded record. This API does not replace its codec. */
unsigned seal669(struct record669 *,const uint8_t *,unsigned,unsigned);
/* Returns for host testing/result indication ONLY. After claiming, every exit
 * is terminal HELD; native integration must enter irq_hold669, never Windows.
 * BUSY/ARG before claiming do not modify the owner or CPU state. */
unsigned run669(struct record669 *,const struct ops669 *);
int irq_enter669(void *,uint32_t *,uint32_t *);
uint32_t irq_flags669(void *);
void irq_hold669(void) __attribute__((noreturn));
#endif
