/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef SIGNAL672_H
#define SIGNAL672_H
#include "phase.h"
#include "indication.h"
enum kind672 { WRAPPER672,ADMISSION672,SEND672,NATIVE672,CLEANUP672,SUCCESS672,INVALID672 };
struct code672 { unsigned kind,value; };
struct emission672 {
 volatile unsigned used;
 unsigned error,steps,pauses,milliseconds,complete;
 struct signal658 smc;
};
/* Only one selected field is signaled; the complete original record remains
 * in RAM. A complete matching repeated sequence is required for interpretation.
 * Missing/partial indications never identify a failure or imply delivery. */
struct code672 classify672(const struct record669 *);
/* Trusted exclusive zeroed storage, immutable callbacks, IF already clear.
 * One-shot even after failure. Returns only for terminal caller/host tests.
 * Finite software bounds assume every callback/bus transaction returns. */
unsigned marker672(const struct smc658 *,struct emission672 *);
unsigned report672(const struct smc658 *,struct emission672 *,struct code672);
#endif
