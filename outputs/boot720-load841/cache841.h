/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Diagnostic arithmetic only. Valid mappings are forwarded without changes. */
static unsigned cache841_bad(long long offset, unsigned length, long long size)
{
    unsigned long long limit;
    if (offset < 0 || size < 0) return 1;
    limit = ((unsigned long long)size + 4095ULL) & ~4095ULL;
    return (unsigned long long)offset > limit || length > limit - (unsigned long long)offset;
}
