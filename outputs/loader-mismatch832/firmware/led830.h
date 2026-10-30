/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef LED830_H
#define LED830_H
#include "xcal_bus.h"
int led_write830(const struct xcal_bus *, uint8_t, uint8_t);
int led_wait830(uint32_t (*)(void *), void *, unsigned);
int led_frame832(const struct xcal_bus *, uint32_t (*)(void *), void *, unsigned, unsigned, unsigned);
#endif
