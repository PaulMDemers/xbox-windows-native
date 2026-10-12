/* Scoped observation admission, not retirement or a native GPU grant. */
#ifndef XWN_BOUNDARY274_H
#define XWN_BOUNDARY274_H
#include <stdint.h>
typedef struct {
    uint64_t original_owner,actual_owner;
    uint32_t get,put,method_error,pending,primitive,draw,inline_array,inline_elements,inline_buffer,reports,queries;
    unsigned ready,cpu0_done,cpu1_done,cpu0_reason,cpu1_reason,cpu0_count,cpu1_count;
    unsigned render_fenced,display_fenced,contexts_match;
} X274Evidence;
static inline unsigned x274_admit(const X274Evidence *e,unsigned complete)
{
    if(!e->ready || !e->original_owner || e->actual_owner!=e->original_owner) return 1;
    if(e->get!=e->put || e->method_error) return 2;
    if(e->pending || e->primitive || e->draw || e->inline_array || e->inline_elements ||
       e->inline_buffer || e->reports || e->queries) return 3;
    if(complete && (!e->cpu0_done || !e->cpu1_done || e->cpu0_reason || e->cpu1_reason ||
       e->cpu0_count || e->cpu1_count)) return 4;
    if(complete && (!e->render_fenced || !e->display_fenced || !e->contexts_match)) return 5;
    return 0;
}
#endif
