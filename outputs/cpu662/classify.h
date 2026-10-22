/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef CLASSIFY662_H
#define CLASSIFY662_H
#include "nic.h"
#include "admission.h"
unsigned cpu_bits662(const struct admission656 *);
unsigned cpu_stage662(const struct admission656 *);
unsigned mask662(unsigned,unsigned,unsigned,unsigned,unsigned,const struct result656 *,const struct admission656 *);
#endif
