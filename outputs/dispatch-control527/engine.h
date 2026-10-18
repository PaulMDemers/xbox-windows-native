/* SPDX-License-Identifier: MIT */
#ifndef XWN_DISPATCH527_H
#define XWN_DISPATCH527_H
#include <stdint.h>
#include <stddef.h>
struct io527 {
    void *ctx;
    int (*open)(void *, unsigned stage, int writing);
    int (*write)(void *, const unsigned char *, size_t, size_t *);
    int (*flush)(void *);
    int (*close)(void *);
    int (*read)(void *, unsigned char *, size_t, size_t *);
};
void receipt527(unsigned char out[48], unsigned stage, const uint16_t kernel[4]);
int run527(const struct io527 *io, const uint16_t kernel[4]);
#endif
