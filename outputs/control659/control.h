/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef CONTROL659_H
#define CONTROL659_H
#include "indication.h"
#define POLLS659 100000u
struct latch659 { unsigned reads,writes,last_status,error,transactions; };
/* Finite polling only. No timer, retry, reset or NIC callback. */
unsigned latch659(const struct smc658 *,unsigned,struct latch659 *);
unsigned mask659(unsigned,unsigned,unsigned);
#endif
