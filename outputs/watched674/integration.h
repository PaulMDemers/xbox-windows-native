/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef INTEGRATION670_H
#define INTEGRATION670_H
#include "phase.h"
#include "packet.h"
struct config670 { uint8_t mac[6],ip[4]; uint16_t port; };
extern struct record669 Record670;
/* Trusted, disjoint, stable owned inputs. No live producer snapshot implied.
 * Encode failure and reentry leave the existing record untouched. */
unsigned prepare670(const struct xwn655_identity *,const struct xwn652_data *);
/* Terminal diagnostic ONLY: never returns, never restores IF, never boots.
 * Config must remain live and immutable through transport and hold. */
unsigned entry672(void);
void terminal670(const struct config670 *) __attribute__((noreturn));
#endif
