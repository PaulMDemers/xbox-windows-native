/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_INDICATION658_H
#define XWN_INDICATION658_H
#include "nic.h"
struct smc658 {
 void *p;
 unsigned (*in)(void *,unsigned,unsigned);
 void (*out)(void *,unsigned,unsigned,unsigned);
 int (*delay)(void *,unsigned); /* bounded microseconds, error propagated */
};
struct signal658 {unsigned transactions,waits,error;};
unsigned write658(const struct smc658 *,unsigned,unsigned,struct signal658 *);
unsigned show658(const struct smc658 *,unsigned,unsigned,struct signal658 *);
void classify658(unsigned,unsigned,unsigned,const struct result656 *,unsigned *);
#endif
