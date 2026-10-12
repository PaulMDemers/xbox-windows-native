"""Exact276 child: separate opt-in worker; unchanged legacy worker/gates."""
from pathlib import Path
import importlib.util
k=Path(__file__).resolve().parent
def one(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)
def apply(root):
    spec=importlib.util.spec_from_file_location('clock278',k/'patch-clock.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    path=root/'system/physmem.c';s=m.apply(path.read_text())
    s=one(s,'static CPUState *x277_clock_owner;',
        'void mem_access_callback_clock277(CPUState *cpu,uint64_t *value,unsigned *error);\nstatic CPUState *x277_clock_owner;')
    path.write_text(s)
    path=root/'hw/xbox/nv2a/pgraph/gl/renderer.c';s=path.read_text()
    s=one(s,'typedef struct X260CPU {','void mem_access_callback_clock277(CPUState *cpu,uint64_t *value,unsigned *error);\ntypedef struct X260CPU {')
    s=one(s,'    unsigned done,reason,count;','    unsigned done,reason,count;\n    uint64_t clock278;unsigned clock_error278;')
    s=one(s,'done:\n    qatomic_store_release(&a->done,1);','done:\n    if(!a->reason)mem_access_callback_clock277(cpu,&a->clock278,&a->clock_error278);\n    qatomic_store_release(&a->done,1);')
    s=one(s,'typedef struct X265State {',(k/'admission.h').read_text()+'\ntypedef struct X265State {')
    s=one(s,'    bool observe276; /* Never arms texture lifetime observation. */','    bool observe276; /* Never arms texture lifetime observation. */\n    bool textures278;uint64_t allocations278[4];\n    X277Proof proof278;unsigned admission278;')
    s=one(s,'bool pgraph_gl_ledger265_worker(NV2AState *d)',(k/'adapter.c').read_text()+'\nbool pgraph_gl_ledger265_worker(NV2AState *d)')
    s=one(s,'    if (!initial) return false;\n    X265State *end=qatomic_load_acquire(&initial->end274);',
        '    if (!initial) return false;\n    if(initial->textures278)return x278_worker(d);\n    X265State *end=qatomic_load_acquire(&initial->end274);')
    s=one(s,'        X265State *end=g_new0(X265State,1);X260Slot *v=&end->boundary;',
        '        X265State *end=g_new0(X265State,1);X260Slot *v=&end->boundary;\n        end->textures278=initial->textures278;memcpy(end->allocations278,initial->allocations278,sizeof(end->allocations278));')
    s=one(s,'    bool observe276=!strcmp(value,"observe276");',
        '    uint64_t allocations278[4]={0};bool textures278=x278_parse(value,allocations278);\n    bool observe276=!strcmp(value,"observe276");')
    s=one(s,'(!observe276 && strcmp(value,"capture,1"))','(!textures278 && !observe276 && strcmp(value,"capture,1"))')
    s=one(s,'    s->observe276=observe276;',
        '    s->observe276=observe276;s->textures278=textures278;memcpy(s->allocations278,allocations278,sizeof(allocations278));')
    s=one(s,'retirement=0 reuse269_error=%u",','retirement=0 reuse269_error=%u texture278=%u admission278=%u",')
    s=one(s,'cpu1?v->cpu[1].reason:UINT_MAX,v->pending_mask,pgraph_gl_reuse269_error());',
        'cpu1?v->cpu[1].reason:UINT_MAX,v->pending_mask,pgraph_gl_reuse269_error(),s->textures278,s->admission278);')
    path.write_text(s)
