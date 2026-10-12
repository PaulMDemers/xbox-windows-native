#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "edges.h"
#include "release.h"
#include "fixture.h"
#define qatomic_load_acquire(p) (*(p))
static unsigned frontend246_ready=1,frontend246_state=2,ui265_error;
static struct {uint64_t (*rows)[8];unsigned count,overflow;}ui265_rows;
#include "ui-provider.c"
#define GL_TEXTURE_2D 3553
static bool xwn_frontend246_closed(void){return frontend246_state==2;}
static uint64_t qemu_get_thread_id(void){return 91;}
typedef unsigned GloContext;static GloContext render_context=1,*g_nv2a_context_render=&render_context;
static uint64_t actual_context=65538;
static bool glo_context_observe267(GloContext *c,uintptr_t ids[4]){assert(c==g_nv2a_context_render);ids[0]=actual_context;return true;}
typedef struct{uint64_t gl_texture,gl_target,refcnt;}TextureBinding;
typedef struct{TextureBinding *texture_binding[4];struct{int num_used;}texture_cache;}PGRAPHGLState;
typedef struct{PGRAPHGLState *gl_renderer_state;unsigned enabled[4];}PGRAPHState;
typedef struct{PGRAPHState pgraph;void *vram;}NV2AState;
typedef struct{struct{unsigned state;}boundary;struct{uint64_t(*rows)[8];unsigned count,overflow;}ledger;unsigned accounting_error,shader_jobs_unknown;X277Proof proof278;}X265State;
static bool pgraph_is_texture_enabled(PGRAPHState *p,unsigned i){return p->enabled[i];}
#include "unbound.c"
static unsigned checks;
#define CHECK(x) do {assert(x);checks++;}while(0)
int main(int argc,char **argv)
{
    assert(argc==2);FILE *f=fopen(argv[1],"rb");assert(f);uint64_t header[6];assert(fread(header,sizeof(header),1,f)==1);
    unsigned counts[2]={header[0],header[1]};assert(counts[0]<180000&&counts[1]<8192);
    uint64_t (*g)[8]=calloc(counts[0]+1,64),(*u)[8]=calloc(counts[1]+1,64);assert(g&&u);
    assert(fread(g,64,counts[0],f)==counts[0]);assert(fread(u,64,counts[1],f)==counts[1]);assert(fgetc(f)==EOF);fclose(f);
    uint64_t *names=header+2;CHECK(x281_edges(g,counts[0],6,names));CHECK(x281_edges(u,counts[1],8,names));
    ui265_rows.rows=u;ui265_rows.count=counts[1];uint64_t context=0;CHECK(xwn_ui281_unbound(names,&context)&&context);
    /* Host object model pairs the actual captured context rows with current
     * live texture objects. The old captured guest is not requalified. */
    NV2AState d={0};PGRAPHGLState renderer={0};TextureBinding textures[4];X265State state={0};X279Proof result={0};
    d.pgraph.gl_renderer_state=&renderer;d.vram=&renderer;state.boundary.state=5;state.ledger.rows=g;state.ledger.count=counts[0];state.proof278=fixture;
    state.proof278.worker=91;state.proof278.device=(uintptr_t)&d;state.proof278.region=(uintptr_t)d.vram;
    for(unsigned p=0;p<2;p++)for(unsigned i=0;i<4;i++){state.proof278.cpu[p].callbacks[i].opaque=(uintptr_t)&d;state.proof278.cpu[p].callbacks[i].region=(uintptr_t)d.vram;}
    uint64_t oldids[4]={0};
    for(unsigned n=0;n<counts[0];n++)if(g[n][0]==67)oldids[g[n][1]]=g[n][2];
    for(unsigned i=0;i<4;i++){textures[i]=(TextureBinding){names[i],3553,2};renderer.texture_binding[i]=&textures[i];state.proof278.textures[i].identity=(uintptr_t)&textures[i];}
    for(unsigned n=0;n<counts[0];n++){
     if(g[n][0]==2)renderer.texture_cache.num_used++;
     unsigned col=(g[n][0]==2||g[n][0]==3||g[n][0]==67)?2:1;
     if(g[n][0]==2||g[n][0]==3||g[n][0]==4||g[n][0]==5||g[n][0]==67)
      for(unsigned i=0;i<4;i++)if(g[n][col]==oldids[i])g[n][col]=(uintptr_t)&textures[i];
    }
    CHECK(x280_unbound(&d,&state,&result));CHECK(result.complete_graph&&result.owner_current&&!result.observer_armed);
    CHECK(x279_admit(&result)==X279_REFUSED);result.observer_armed=1;CHECK(x279_admit(&result)==X279_OK);
    for(unsigned i=0;i<4;i++){
     renderer.texture_binding[i]=NULL;CHECK(!x280_unbound(&d,&state,&result));renderer.texture_binding[i]=&textures[i];
     textures[i].refcnt=1;CHECK(!x280_unbound(&d,&state,&result));textures[i].refcnt=2;
     d.pgraph.enabled[i]=1;CHECK(!x280_unbound(&d,&state,&result));d.pgraph.enabled[i]=0;
    }
    state.boundary.state=2;CHECK(!x280_unbound(&d,&state,&result));state.boundary.state=5;
    state.ledger.overflow=1;CHECK(!x280_unbound(&d,&state,&result));state.ledger.overflow=0;
    state.accounting_error=1;CHECK(!x280_unbound(&d,&state,&result));state.accounting_error=0;
    state.shader_jobs_unknown=1;CHECK(!x280_unbound(&d,&state,&result));state.shader_jobs_unknown=0;
    state.proof278.device++;CHECK(!x280_unbound(&d,&state,&result));state.proof278.device--;
    actual_context++;CHECK(!x280_unbound(&d,&state,&result));actual_context--;
    CHECK(x280_unbound(&d,&state,&result));
    for(unsigned n=0;n<counts[0];n++){
     unsigned col=(g[n][0]==2||g[n][0]==3||g[n][0]==67)?2:1;
     if(g[n][0]==2||g[n][0]==3||g[n][0]==4||g[n][0]==5||g[n][0]==67)
      for(unsigned i=0;i<4;i++)if(g[n][col]==(uintptr_t)&textures[i])g[n][col]=oldids[i];
    }
    for(unsigned group=0;group<2;group++) {
        uint64_t (*rows)[8]=group?u:g;unsigned count=counts[group],roles=group?8:6;
        for(unsigned i=0;i<count;i++) {
            uint64_t saved[8];memcpy(saved,rows[i],64);
            if(saved[0]==32 && saved[2]==0) {
                for(unsigned j=0;j<4;j++){rows[i][4]=names[j];CHECK(!x281_edges(rows,count,roles,names));}
                memcpy(rows[i],saved,64);rows[i][3]=0x1234;CHECK(!x281_edges(rows,count,roles,names));
            }
            if(saved[0]==55) {
                for(unsigned j=0;j<4;j++){rows[i][4]=0x1702;rows[i][5]=names[j];CHECK(!x281_edges(rows,count,roles,names));}
            }
            memcpy(rows[i],saved,64);
            if(saved[0]==30 || saved[0]==31 || saved[0]==32 || saved[0]==33 || saved[0]==54 || saved[0]==55 || saved[0]==56) {
                rows[i][0]=0;CHECK(!x281_edges(rows,count,roles,names));memcpy(rows[i],saved,64);
                memcpy(rows[count],saved,64);CHECK(!x281_edges(rows,count+1,roles,names));memset(rows[count],0,64);
            }
            if(group && (saved[0]==40 || saved[0]==64 || saved[0]==65)) {
                rows[i][0]=0;CHECK(!xwn_ui281_unbound(names,&context));memcpy(rows[i],saved,64);
                if(saved[0]!=65){rows[i][3]=names[0];CHECK(!xwn_ui281_unbound(names,&context));}
            }
            memcpy(rows[i],saved,64);
        }
    }
    frontend246_ready=0;CHECK(!xwn_ui281_unbound(names,&context));frontend246_ready=1;
    frontend246_state=4;CHECK(!xwn_ui281_unbound(names,&context));frontend246_state=2;
    ui265_error=1;CHECK(!xwn_ui281_unbound(names,&context));ui265_error=0;
    ui265_rows.overflow=1;CHECK(!xwn_ui281_unbound(names,&context));ui265_rows.overflow=0;
    CHECK(x281_edges(g,counts[0],6,names)&&xwn_ui281_unbound(names,&context));
    free(g);free(u);printf("PASS %u actual closed-graph/UI edge checks; actual new functions, modeled publication globals, no live GL/release\n",checks);return 0;
}
