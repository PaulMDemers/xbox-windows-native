/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef MISMATCH832_H
#define MISMATCH832_H
#include <stdint.h>
struct mismatch832 { uint32_t group,item,actual,expected; };
extern volatile struct mismatch832 Mismatch832;
#endif
