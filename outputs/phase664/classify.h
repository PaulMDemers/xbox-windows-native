/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef CLASSIFY664_H
#define CLASSIFY664_H
#include "nic.h"
#include "admission.h"
unsigned cpu_bits664(const struct admission656 *);
unsigned cpu_stage664(const struct admission656 *);
unsigned mask664(unsigned,unsigned,unsigned,unsigned,unsigned,const struct result656 *,const struct admission656 *);
#endif
