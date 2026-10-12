"""Exact278 child; new one-shot281 mode, unchanged legacy operations when unused."""
from pathlib import Path
k=Path(__file__).resolve().parent;worker=k.parent/'release-worker280'
def one(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b)
def apply(root):
 header=root/'hw/xbox/nv2a/pgraph/gl/renderer.h'
 shared=(worker/'admission.h').read_text()+'\n'+(worker/'release.h').read_text().replace('#include "admission.h"','').replace('static unsigned x279_admit','static inline unsigned x279_admit')
 header.write_text(header.read_text()+'\n#ifndef XWN_RELEASE281_SHARED\n#define XWN_RELEASE281_SHARED\n'+shared+'\nbool pgraph_gl_reuse280_post(NV2AState *d);\nX279Result pgraph_gl_release280(NV2AState *d,const X279Proof *proof);\n#endif\n')
 path=root/'hw/xbox/nv2a/pgraph/gl/renderer.c';s=path.read_text()
 s=one(s,'typedef struct X265State {','typedef struct X280Transaction X280Transaction;\ntypedef struct X265State {')
 s=one(s,'    X277Proof proof278;unsigned admission278;','    X277Proof proof278;unsigned admission278;\n    X280Transaction *transaction280;')
 s=one(s,'} X265State;','} X265State;\n'+(k/'transaction.h').read_text())
 code='\nbool xwn_ui281_unbound(const uint64_t names[4],uint64_t *context);\n'
 for n in ['boundary.h','link.h','resume.h']:code+=(worker/n).read_text()+'\n'
 for n in ['edges.h','unbound.c']:code+=(k/n).read_text()+'\n'
 for n in ['graph.c','validate.c','retained.c','publish.c','scalar-publish.c','capture.c','worker.c']:code+=(worker/n).read_text()+'\n'
 code+=(k/'interface.c').read_text()+'\n'
 s=one(s,'bool pgraph_gl_ledger265_worker(NV2AState *d)',code+'bool pgraph_gl_ledger265_worker(NV2AState *d)')
 s=one(s,'    if(initial->textures278)return x278_worker(d);','    if(initial->transaction280)return x280_worker(d);\n    if(initial->textures278)return x278_worker(d);')
 s=one(s,'void pgraph_gl_ledger265_request(NV2AState *d,const char *value,Error **errp)\n{','void pgraph_gl_ledger265_request(NV2AState *d,const char *value,Error **errp)\n{\n    if(x281_request(d,value,errp))return;')
 s=one(s,'void pgraph_gl_ledger265_page(NV2AState *d,const char *value,Error **errp)\n{','void pgraph_gl_ledger265_page(NV2AState *d,const char *value,Error **errp)\n{\n    if(x281_page(d,value,errp))return;')
 s=one(s,'if (!initial) return g_strdup("version=265 epoch=1 state=0");','if (!initial) return g_strdup("version=265 epoch=1 state=0");\n    if(initial->transaction280)return x281_report(initial->transaction280);')
 anchor='char *pgraph_gl_ledger265_data(NV2AState *d)\n{\n    X265State *initial=qatomic_load_acquire(&d->ledger265);'
 s=one(s,anchor,anchor+'\n    if(initial && initial->transaction280)return x281_data(initial->transaction280);');path.write_text(s)
 path=root/'hw/xbox/nv2a/pgraph/gl/texture.c';s=path.read_text()
 s+='\n'+(worker/'proposed-release.c').read_text()+'\n'+(k/'texture-wrappers.c').read_text();path.write_text(s)
 path=root/'ui/xemu.c';s=path.read_text()
 s+='\n'+(k/'edges.h').read_text()+'\nbool xwn_ui281_unbound(const uint64_t names[4],uint64_t *context);\n'+(k/'ui-provider.c').read_text();path.write_text(s)
