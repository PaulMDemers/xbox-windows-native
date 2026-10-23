/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef TIMER675_H
#define TIMER675_H
#include "indication.h"
#define SAMPLES675 64u
enum phase675 { ZERO675,CLAIMED675,ENTRY675,TIMER675,FINAL675,DONE675 };
enum error675 { OK675,ARG675,BUSY675,IF675,ENTRY_SMC675,FINAL_SMC675 };
struct ops675 {
 void *p;
 uint32_t (*flags)(void *);
 uint32_t (*ticks)(void *);
 unsigned (*in)(void *,unsigned,unsigned);
 void (*out)(void *,unsigned,unsigned,unsigned);
};
struct record675 {
 volatile unsigned phase;
 unsigned error,entry_complete,timer_called,final_complete;
 uint32_t flags_before,flags_after_entry,flags_after;
 unsigned request_us,timer_error,total_samples,stored_samples;
 uint32_t samples[SAMPLES675],last_sample;
 unsigned entry_error,final_error,wait_refusals,last_wait_us,final_mask;
 struct signal658 smc;
 struct result656 timer_accounting;
};
/* HOST-ONLY prototype. Trusted zeroed owned record and immutable callbacks.
 * Caller supplies IF-clear diagnostic context and MUST terminal-hold after
 * this function returns. This API does not disable/restore IF or start a NIC.
 * One unchanged delay656 call, at most200001 timer reads. Raw first64 and last
 * sample are retained, not interpreted as calibrated hardware elapsed time.
 * Indicator never asks the timer to wait. If SMC needs a delay, fail closed;
 * neither poll without the required delay nor retry a failed transaction.
 */
unsigned probe675(const struct ops675 *,struct record675 *,unsigned);
#endif
