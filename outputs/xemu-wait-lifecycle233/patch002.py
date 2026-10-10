"""Correct logger access mask and scope only new prototypes inside header guard."""
from patch import apply as original_apply,replace
def apply(root):
    original_apply(root)
    p=root/'hw/xbox/nv2a/pgraph/pgraph.c';s=p.read_text()
    s=replace(s,'(!qatomic_read(&pg->regs_[NV_PGRAPH_FIFO]) ? 1 : 0)',
        '(!(qatomic_read(&pg->regs_[NV_PGRAPH_FIFO]) & NV_PGRAPH_FIFO_ACCESS) ? 1 : 0)')
    p.write_text(s)
    p=root/'hw/xbox/nv2a/nv2a_int.h';s=p.read_text()
    declarations='''void nv2a_wait233_fill(NV2AState *d, NV2AWaitRow233 *row,
                       unsigned kind, uint32_t value, bool fifo_valid);
void nv2a_wait233_record(NV2AState *d, unsigned kind, uint32_t value,
                         bool fifo_valid);
'''
    s=replace(s,declarations,'');s=replace(s,'\n#endif\n\n/*228','\n'+declarations+'\n#endif\n\n/*228');p.write_text(s)
