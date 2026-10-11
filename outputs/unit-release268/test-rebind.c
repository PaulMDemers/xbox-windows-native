/* Harness models GL and register/VRAM interfaces; original bind/LRU/release code
 * is extracted byte-exact from pinned xemu. This is NOT actual GL/guest proof. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "qemu/lru.h"
#include "release-core.h"
#define NV2A_MAX_TEXTURES 4
#define GL_TEXTURE0 0x84c0u
#define GL_TEXTURE_1D 0x0de0u
#define GL_TEXTURE_2D 0x0de1u
#define GL_TEXTURE_3D 0x806fu
#define GL_TEXTURE_CUBE_MAP 0x8513u
#define GL_ACTIVE_TEXTURE 0x84e0u
#define GL_TEXTURE_BINDING_2D 0x8069u
#define GL_NO_ERROR 0
#define NV_PGRAPH_TEXFILTER0 0
#define NV_PGRAPH_TEXADDRESS0 100
#define NV_PGRAPH_BORDERCOLOR0 200
#define NV_PGRAPH_TEXCTL0_0 300
#define NV_PGRAPH_TEXCTL0_0_MAX_ANISOTROPY 1
#define NV_PGRAPH_TEXFILTER0_ASIGNED 0x8000
#define NV_PGRAPH_TEXFILTER0_RSIGNED 0x4000
#define NV_PGRAPH_TEXFILTER0_GSIGNED 0x2000
#define NV_PGRAPH_TEXFILTER0_BSIGNED 0x1000
#define NV097_SET_TEXTURE_FORMAT_COLOR_SZ_I8_A8R8G8B8 1
#define GET_MASK(v,m) ((v)&(m))
#define NV2A_UNIMPLEMENTED(x) assert(!x)
#define NV2A_GL_DGROUP_BEGIN(...) ((void)0)
#define NV2A_GL_DGROUP_END() ((void)0)
#define trace_nv2a_pgraph_surface_render_to_texture(...) ((void)0)
#define container_of(ptr,type,member) ((type*)((char*)(ptr)-offsetof(type,member)))
typedef unsigned GLuint,GLenum;
typedef int GLint;
typedef uint64_t hwaddr;
typedef void *gpointer;
typedef struct { unsigned color_format,dimensionality;bool border;unsigned width,height; } TextureShape;
typedef struct { TextureShape state;hwaddr texture_vram_offset,texture_length,palette_vram_offset,palette_length; } TextureKey;
typedef struct { unsigned refcnt;GLuint gl_texture;GLenum gl_target;int draw_time;unsigned scale;uint64_t data_hash; } TextureBinding;
typedef struct { LruNode node;TextureKey key;TextureBinding *binding;bool possibly_dirty; } TextureLruNode;
typedef struct SurfaceBinding { QTAILQ_ENTRY(SurfaceBinding) entry;hwaddr vram_addr,size;bool upload_pending;int draw_time;unsigned width,height; } SurfaceBinding;
typedef struct { Lru texture_cache;TextureLruNode nodes[16];TextureBinding *texture_binding[4];QTAILQ_HEAD(,SurfaceBinding) surfaces; } PGRAPHGLState;
typedef struct { PGRAPHGLState *gl_renderer_state;bool enabled[4],texture_dirty[4];unsigned surface_scale_factor;TextureShape shape[4];hwaddr offset[4]; } PGRAPHState;
typedef struct { PGRAPHState pgraph;void *vram;uint8_t *vram_ptr;bool dirty; } NV2AState;
typedef struct { unsigned unused; } BasicColorFormatInfo;
static const BasicColorFormatInfo kelvin_color_format_info_map[2]={{0},{0}};
static unsigned active,gl_names[4][4],next_name,deletes,frees,uploads,gl_error,binds;
static struct { bool alive;uint8_t bytes[64]; } objects[8192];
static unsigned target_index(unsigned target) {
    switch(target) {case GL_TEXTURE_1D:return 0;case GL_TEXTURE_2D:return 1;case GL_TEXTURE_3D:return 2;case GL_TEXTURE_CUBE_MAP:return 3;default:assert(false);return 0;}
}
static void glActiveTexture(unsigned name) {assert(name>=GL_TEXTURE0 && name<GL_TEXTURE0+4);active=name-GL_TEXTURE0;}
static void glBindTexture(unsigned target,unsigned name) {assert(!name || (name<8192 && objects[name].alive));gl_names[active][target_index(target)]=name;binds++;}
static void glGetIntegerv(unsigned kind,int *value) {if(kind==GL_ACTIVE_TEXTURE)*value=GL_TEXTURE0+active;else {assert(kind==GL_TEXTURE_BINDING_2D);*value=gl_names[active][1];}}
static unsigned glGetError(void) {unsigned e=gl_error;gl_error=0;return e;}
static void glDeleteTextures(int n,const unsigned *names) {assert(n==1 && objects[*names].alive);objects[*names].alive=false;deletes++;}
static void g_free(void *p) {assert(p);frees++;free(p);}
static bool pgraph_is_texture_enabled(PGRAPHState *pg,unsigned i) {return pg->enabled[i];}
static unsigned pgraph_reg_r(PGRAPHState *pg,unsigned reg) {(void)pg;(void)reg;return 0;}
static TextureShape pgraph_get_texture_shape(PGRAPHState *pg,unsigned i) {return pg->shape[i];}
static size_t pgraph_get_texture_length(PGRAPHState *pg,const TextureShape *s) {(void)pg;(void)s;return 64;}
static hwaddr pgraph_get_texture_phys_addr(PGRAPHState *pg,unsigned i) {return pg->offset[i];}
static hwaddr pgraph_get_texture_palette_phys_addr_length(PGRAPHState *pg,unsigned i,size_t *len) {*len=16;return 2048+i*32;}
static hwaddr memory_region_size(void *region) {(void)region;return 4096;}
static SurfaceBinding *pgraph_gl_surface_get(NV2AState *d,hwaddr address) {(void)d;(void)address;return NULL;}
static bool check_texture_possibly_dirty(NV2AState *d,hwaddr a,unsigned len,hwaddr pal,unsigned plen) {(void)a;(void)len;(void)pal;(void)plen;return d->dirty;}
static void apply_texture_parameters(PGRAPHGLState *r,TextureBinding *b,const BasicColorFormatInfo *f,unsigned dims,unsigned filter,unsigned address,bool bordered,uint32_t border,unsigned aniso) {(void)r;(void)b;(void)f;(void)dims;(void)filter;(void)address;(void)bordered;(void)border;(void)aniso;}
static bool pgraph_gl_check_surface_to_texture_compatibility(SurfaceBinding *b,const TextureShape *s) {(void)b;(void)s;assert(false);return false;}
static void pgraph_gl_upload_surface_data(NV2AState *d,SurfaceBinding *s,bool a) {(void)d;(void)s;(void)a;assert(false);}
static void pgraph_gl_surface_download_if_dirty(NV2AState *d,SurfaceBinding *s) {(void)d;(void)s;assert(false);}
static void pgraph_gl_render_surface_to_texture(NV2AState *d,SurfaceBinding *s,TextureBinding *b,const TextureShape *t,unsigned unit) {(void)d;(void)s;(void)b;(void)t;(void)unit;assert(false);}
static uint64_t fast_hash(const uint8_t *p,size_t n) {uint64_t h=1469598103934665603ULL;while(n--)h=(h^*p++)*1099511628211ULL;return h;}
static TextureBinding *generate_texture(TextureShape s,const uint8_t *data,const uint8_t *palette) {
    TextureBinding *b=calloc(1,sizeof(*b));assert(b);b->refcnt=1;b->gl_texture=++next_name;b->gl_target=GL_TEXTURE_2D;
    assert(next_name<8192);objects[next_name].alive=true;
    for(unsigned i=0;i<64;i++)objects[next_name].bytes[i]=data[i]^(s.color_format?palette[i%16]:0);
    glBindTexture(GL_TEXTURE_2D,next_name);uploads++;return b;
}
#include "actual-functions.h"
#include "proposed-release.c"
static X268Edge edges[4];
static X268Proof proof(NV2AState *d) {
    X268Proof p={.cpu_before_ack=true,.worker_owner=true,.render_current=true,.ui_closed=true,.contexts_matched=true,.cache_count=4,.edge_count=4,.edges=edges};
    for(unsigned i=0;i<4;i++) {
        TextureBinding *b=d->pgraph.gl_renderer_state->texture_binding[i];
        p.units[i]=(X268Unit){(uintptr_t)b,b->refcnt,1,1,d->pgraph.enabled[i],b->gl_target,b->gl_texture};
        edges[i]=(X268Edge){1,i,GL_TEXTURE_2D,gl_names[i][1]};
    }
    return p;
}
static void setup(NV2AState *d,PGRAPHGLState *r,uint8_t *memory,bool indexed) {
    memset(d,0,sizeof(*d));memset(r,0,sizeof(*r));memset(gl_names,0,sizeof(gl_names));active=0;gl_error=0;
    d->pgraph.gl_renderer_state=r;d->vram_ptr=memory;d->dirty=true;
    lru_init(&r->texture_cache);QTAILQ_INIT(&r->surfaces);
    r->texture_cache.init_node=texture_cache_entry_init;r->texture_cache.compare_nodes=texture_cache_entry_compare;r->texture_cache.post_node_evict=texture_cache_entry_post_evict;
    for(unsigned i=0;i<16;i++)lru_add_free(&r->texture_cache,&r->nodes[i].node);
    for(unsigned i=0;i<4096;i++)memory[i]=(i*17+i/23)^0xa3;
    for(unsigned i=0;i<4;i++){d->pgraph.enabled[i]=true;d->pgraph.texture_dirty[i]=true;d->pgraph.offset[i]=i*256;d->pgraph.shape[i]=(TextureShape){indexed,2,false,4,4};}
    pgraph_gl_bind_textures(d);d->dirty=false;
    for(unsigned i=0;i<4;i++)assert(r->texture_binding[i]->refcnt==2);
}
static void finish(PGRAPHGLState *r) {
    for(unsigned i=0;i<4;i++)if(r->texture_binding[i]){texture_binding_destroy(r->texture_binding[i]);r->texture_binding[i]=NULL;}
    lru_flush(&r->texture_cache);assert(r->texture_cache.num_used==0);
}
static unsigned scenarios,negative;
static void run_case(bool indexed,unsigned mutation,bool release,bool evict) {
    printf("case indexed=%u mutation=%u release=%u evict=%u\n",indexed,mutation,release,evict);fflush(stdout);
    NV2AState d;PGRAPHGLState *r=calloc(1,sizeof(*r));uint8_t memory[4096];assert(r);setup(&d,r,memory,indexed);
    TextureBinding *old[4];unsigned names[4];for(unsigned i=0;i<4;i++){old[i]=r->texture_binding[i];names[i]=old[i]->gl_texture;d.pgraph.enabled[i]=false;}
    /* Exercise original disabled branch: it unbinds but retains all four refs. */
    pgraph_gl_bind_textures(&d);
    for(unsigned i=0;i<4;i++)assert(r->texture_binding[i]==old[i] && old[i]->refcnt==2 && gl_names[i][1]==0);
    if(release) {
        /* Match267's observed state: one unit still bound; others already zero. */
        glActiveTexture(GL_TEXTURE0);glBindTexture(GL_TEXTURE_2D,names[0]);glActiveTexture(GL_TEXTURE0+2);
        X268Proof p=proof(&d);unsigned del=deletes,fr=frees,up=uploads;
        assert(x268_release(&d,&p));assert(active==2 && deletes==del && frees==fr && uploads==up);
        for(unsigned i=0;i<4;i++)assert(!r->texture_binding[i] && old[i]->refcnt==1 && objects[names[i]].alive && d.pgraph.texture_dirty[i]);
    }
    if(evict) lru_flush(&r->texture_cache); /* Ordinary cache pressure modeled separately, never inside release. */
    if(mutation){d.dirty=true;for(unsigned i=0;i<4;i++){if(mutation==2)memory[i*256+13]^=0x7d;if(mutation==3)memory[2048+i*32+7]^=0x55;}}
    unsigned up=uploads;
    for(unsigned i=0;i<4;i++)d.pgraph.enabled[i]=true;
    pgraph_gl_bind_textures(&d);
    for(unsigned i=0;i<4;i++){
        TextureBinding *b=r->texture_binding[i];assert(b && gl_names[i][1]==b->gl_texture);
        unsigned cache_edges=0;LruNode *node;
        QTAILQ_FOREACH(node,&r->texture_cache.global,next_global) {
            if(lru_is_node_in_use(&r->texture_cache,node) && container_of(node,TextureLruNode,node)->binding==b)cache_edges++;
        }
        assert(cache_edges<=1 && b->refcnt==cache_edges+1);
        if(release)assert(cache_edges==1 && b->refcnt==2);
        if(!evict && mutation<2)assert(b==old[i] && b->gl_texture==names[i]);
        for(unsigned j=0;j<64;j++){
            unsigned expected=memory[i*256+j]^(indexed?memory[2048+i*32+j%16]:0);
            assert(objects[b->gl_texture].bytes[j]==expected);
        }
    }
    if(!evict && mutation<2)assert(uploads==up);
    if((evict && (release || mutation)) || mutation==2 || (indexed && mutation==3))assert(uploads==up+4);
    if(evict && !release && !mutation)assert(uploads==up);
    finish(r);free(r);scenarios++;
}
static void refusals(void) {
    NV2AState d;PGRAPHGLState *r=calloc(1,sizeof(*r));uint8_t memory[4096];assert(r);setup(&d,r,memory,false);
    for(unsigned i=0;i<4;i++)d.pgraph.enabled[i]=false;
    X268Proof p=proof(&d);assert(x268_admit(&p)==0);
    for(unsigned test=0;test<23;test++){
        X268Proof q=p;X268Edge altered[4];memcpy(altered,edges,sizeof(altered));q.edges=altered;
        switch(test){
        case 0:q.overflow=1;break;case 1:q.unknown_owners=1;break;case 2:q.pending=1;break;
        case 3:q.actor_unknown=1;break;case 4:q.callbacks=1;break;case 5:q.cpu_before_ack=false;break;
        case 6:q.worker_owner=false;break;case 7:q.render_current=false;break;case 8:q.ui_closed=false;break;
        case 9:q.contexts_matched=false;break;case 10:q.cache_count=513;break;case 11:q.edge_count=8449;break;
        case 12:q.edges=NULL;break;case 13:q.units[0].binding=0;break;case 14:q.units[0].enabled=1;break;
        case 15:q.units[0].refs=1;break;case 16:q.units[0].cache_edges=0;break;case 17:q.units[0].unit_edges=2;break;
        case 18:q.units[0].target=GL_TEXTURE_CUBE_MAP;break;case 19:q.units[1].binding=q.units[0].binding;break;
        case 20:altered[0].role=2;break;case 21:altered[0].unit=1;break;case 22:altered[0].target=GL_TEXTURE_3D;break;
        }
        unsigned before=binds;assert(x268_admit(&q)!=0 && !x268_release(&d,&q));assert(binds==before);
        for(unsigned i=0;i<4;i++) {assert(r->texture_binding[i]->refcnt==2);}
        negative++;
    }
    /* Stale proof vs actual unit/cache/GL state must not decrement any ref. */
    d.pgraph.enabled[1]=true;assert(!x268_release(&d,&p));d.pgraph.enabled[1]=false;negative++;
    p.units[0].binding++;assert(!x268_release(&d,&p));p.units[0].binding--;negative++;
    r->texture_cache.num_used++;assert(!x268_release(&d,&p));r->texture_cache.num_used--;negative++;
    gl_names[1][1]=0;unsigned saved=active;assert(!x268_release(&d,&p));assert(active==saved);gl_names[1][1]=p.units[1].texture;negative++;
    gl_error=0x0502;assert(!x268_release(&d,&p));negative++;
    for(unsigned i=0;i<4;i++)assert(r->texture_binding[i]->refcnt==2);
    finish(r);free(r);
}
int main(void) {
    for(unsigned idx=0;idx<2;idx++)for(unsigned mutation=0;mutation<4;mutation++)for(unsigned release=0;release<2;release++)for(unsigned evict=0;evict<2;evict++)run_case(idx,mutation,release,evict);
    refusals();assert(deletes==frees && uploads==deletes);
    printf("PASS %u original-bind/rebind cases; %u refusal cases; %u model uploads/deletes; exact source/LRU, stub GL and register interfaces\n",scenarios,negative,uploads);
}
