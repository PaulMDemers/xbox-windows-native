/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef CLASSIFY667_H
#define CLASSIFY667_H
#include "nic.h"
#include "admission.h"
#include "receipt.h"
unsigned context667(const struct xwn652_data *,const struct admission656 *,unsigned);
unsigned context_mask667(unsigned);
unsigned cpu_bits667(const struct admission656 *);
unsigned cpu_stage667(const struct admission656 *);
unsigned mask667(unsigned,unsigned,unsigned,unsigned,unsigned,const struct result656 *,const struct admission656 *);
struct boundary667 { unsigned before,after,valid_before,valid_after; };
unsigned boundary667(const volatile struct boundary667 *,unsigned);
unsigned boundary_mask667(unsigned);
#endif
