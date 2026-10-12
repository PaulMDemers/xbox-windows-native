"""Exact274 child: copied CPU detail and one read-only getter. No gate changes."""
from pathlib import Path
k=Path(__file__).resolve().parent
def one(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)
def apply(root):
    path=root/'hw/xbox/nv2a/pgraph/gl/renderer.c';s=path.read_text()
    s=one(s,'    uint64_t epoch,thread,when,rows[X260_CALLBACKS][4];','    uint64_t epoch,thread,when,rows[X260_CALLBACKS][4];\n    uint64_t detail276[X260_CALLBACKS][3]; /* CPU-owned function,region,absolute RAM address */')
    s=one(s,'        uint64_t *row=a->rows[a->count++];','        uint64_t *detail=a->detail276[a->count];\n        detail[0]=(uintptr_t)cb->func;detail[1]=(uintptr_t)cb->mr;detail[2]=cb->addr;\n        uint64_t *row=a->rows[a->count++];')
    s=one(s,'    unsigned end_page274,contexts274,seal274;','    unsigned end_page274,contexts274,seal274;\n    bool observe276; /* Never arms texture lifetime observation. */')
    s=one(s,'    if (s->accounting_error || s->shader_jobs_unknown || v->cpu[0].count) {reason=14;goto finish;}','    if (s->accounting_error || s->shader_jobs_unknown || v->cpu[0].count) {reason=14;goto finish;}\n    if (s->observe276) {reason=27;goto finish;} /* no arm even if count unexpectedly zero */')
    s=one(s,'    if (strcmp(value,"capture,1") || runstate_is_running() || !xwn_frontend246_closed() ||','    bool observe276=!strcmp(value,"observe276");\n    if ((!observe276 && strcmp(value,"capture,1")) || runstate_is_running() || !xwn_frontend246_closed() ||')
    s=one(s,'    X265State *s=g_new0(X265State,1);X260Slot *v=&s->boundary;','    X265State *s=g_new0(X265State,1);X260Slot *v=&s->boundary;\n    s->observe276=observe276;')
    s+='\n'+(k/'inventory.c').read_text();path.write_text(s)
    path=root/'hw/xbox/nv2a/nv2a_int.h';s=path.read_text();s=one(s,'char *pgraph_gl_ledger265_report(NV2AState *d);','char *pgraph_gl_ledger265_report(NV2AState *d);\nchar *pgraph_gl_callbacks276_report(NV2AState *d);');path.write_text(s)
    path=root/'hw/xbox/nv2a/nv2a.c';s=path.read_text()
    s=one(s,'static char *ledger265_report(Object *obj,Error **errp)','static char *callbacks276_report(Object *obj,Error **errp)\n{ return pgraph_gl_callbacks276_report(NV2A_DEVICE(obj)); }\nstatic char *ledger265_report(Object *obj,Error **errp)')
    s=one(s,'    object_property_add_str(OBJECT(d),"xwn-ledger265-report",ledger265_report,NULL);','    object_property_add_str(OBJECT(d),"xwn-ledger265-report",ledger265_report,NULL);\n    object_property_add_str(OBJECT(d),"xwn-callbacks276",callbacks276_report,NULL);')
    path.write_text(s)
