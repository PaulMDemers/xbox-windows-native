/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef CLASSIFY665_H
#define CLASSIFY665_H
#include "nic.h"
#include "admission.h"
#include "receipt.h"
unsigned context665(const struct xwn652_data *,const struct admission656 *,unsigned);
unsigned context_mask665(unsigned);
unsigned cpu_bits665(const struct admission656 *);
unsigned cpu_stage665(const struct admission656 *);
unsigned mask665(unsigned,unsigned,unsigned,unsigned,unsigned,const struct result656 *,const struct admission656 *);
#endif
