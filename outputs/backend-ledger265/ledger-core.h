/* SPDX-License-Identifier: GPL-2.0-or-later
 * Bounded observation storage and owner accounting; never a GPU grant.
 */
#ifndef X265_LEDGER_CORE_H
#define X265_LEDGER_CORE_H
#include <stdint.h>
#include <stddef.h>
#define X265_COLUMNS 8u
#define X265_BINDINGS 516u
#define X265_ROWS 180000u
#define X265_UI_ROWS 8192u
#define X265_PAGE 256u
typedef struct {
    uint64_t (*rows)[X265_COLUMNS];
    unsigned count, capacity, overflow;
} X265Rows;
typedef struct {
    uint64_t identity;
    unsigned refs, cache_edges, unit_edges;
} X265Binding;
static inline int x265_add(X265Rows *out, uint64_t kind, uint64_t a, uint64_t b,
                    uint64_t c, uint64_t d, uint64_t e, uint64_t f, uint64_t g)
{
    if (!out->rows || out->count >= out->capacity) {
        out->overflow = 1;
        return 0;
    }
    uint64_t values[X265_COLUMNS] = {kind,a,b,c,d,e,f,g};
    for (unsigned i=0;i<X265_COLUMNS;i++) out->rows[out->count][i]=values[i];
    out->count++;
    return 1;
}
/* Unknown owners are a failed accounting result, not an invented cache edge. */
static inline unsigned x265_account(const X265Binding *bindings, unsigned count)
{
    if (count > X265_BINDINGS || (count && !bindings)) return 1;
    for (unsigned i=0;i<count;i++) {
        const X265Binding *b=&bindings[i];
        if (!b->identity || !b->refs || b->cache_edges > 512 || b->unit_edges > 4 ||
            b->refs != b->cache_edges + b->unit_edges) return 2;
        for (unsigned j=0;j<i;j++) if (bindings[j].identity==b->identity) return 3;
    }
    return 0;
}
static inline unsigned x265_page_count(unsigned rows)
{
    return rows / X265_PAGE + !!(rows % X265_PAGE);
}
#endif
