/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef CLASSIFY663_H
#define CLASSIFY663_H
#include "nic.h"
#include "admission.h"
unsigned cpu_bits663(const struct admission656 *);
unsigned cpu_stage663(const struct admission656 *);
unsigned mask663(unsigned,unsigned,unsigned,unsigned,unsigned,const struct result656 *,const struct admission656 *);
#endif
