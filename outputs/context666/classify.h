/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef CLASSIFY666_H
#define CLASSIFY666_H
#include "nic.h"
#include "admission.h"
#include "receipt.h"
unsigned context666(const struct xwn652_data *,const struct admission656 *,unsigned);
unsigned context_mask666(unsigned);
unsigned cpu_bits666(const struct admission656 *);
unsigned cpu_stage666(const struct admission656 *);
unsigned mask666(unsigned,unsigned,unsigned,unsigned,unsigned,const struct result656 *,const struct admission656 *);
#endif
