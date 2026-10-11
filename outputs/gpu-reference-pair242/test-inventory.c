/* Actual compiled242 helpers under explicit model/clock/lock adapters.
 * Real QEMU LRU/queue/atomic headers; no GL or CPU callback execution. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define qemu_build_assert(c) _Static_assert(c,"atomic width")
#include <qemu/atomic.h>
#include <qemu/lru.h>
#define QEMU_CLOCK_REALTIME 0
#define NV2A_VERTEXSHADER_ATTRIBUTES 16
#define NV2A_MAX_TEXTURES 4
#define NV_PGRAPH_CTX_USER 0
#define NV_PGRAPH_SURFACE 1
typedef struct { bool held,busy; } QemuMutex;
static int qemu_mutex_trylock(QemuMutex *m) { assert(!m->held);if(m->busy)return 1;m->held=true;return 0; }
static void qemu_mutex_unlock(QemuMutex *m) { assert(m->held);m->held=false; }
typedef struct SurfaceBinding {
 QTAILQ_ENTRY(SurfaceBinding) entry;void *access_cb;
 uint64_t vram_addr,size,pitch,width,height,dma_addr,dma_len;
 bool draw_dirty,download_pending,cpu_write_evict_pending,upload_pending,cleared,color,swizzle;
 unsigned gl_buffer;
} SurfaceBinding;
typedef struct {unsigned gl_texture,refcnt,gl_target;} TextureBinding;
typedef struct {LruNode node;struct {uint64_t texture_vram_offset,texture_length,palette_vram_offset,palette_length;}key;TextureBinding *binding;bool possibly_dirty;} TextureLruNode;
typedef struct {LruNode node;bool initialized;void *program,*save_thread;unsigned gl_program;} ShaderBinding;
typedef struct {LruNode node;unsigned gl_shader;} ShaderModuleCacheEntry;
typedef struct {LruNode node;bool initialized;unsigned gl_buffer;} VertexLruNode;
typedef struct {
 QemuMutex shader_cache_lock;QTAILQ_HEAD(,SurfaceBinding) surfaces;
 SurfaceBinding *color_binding,*zeta_binding;
 bool downloads_pending,download_dirty_surfaces_pending,shader_cache_writeback_pending;
 unsigned gl_framebuffer,gl_display_buffer,gl_display_buffer_width,gl_display_buffer_height;
 Lru texture_cache,shader_cache,shader_module_cache,element_cache;
 TextureBinding *texture_binding[4];ShaderBinding *shader_binding;
 unsigned gl_inline_array_buffer,gl_memory_buffer,gl_vertex_array,gl_inline_buffer[16];
 struct {unsigned fbo,vao,vbo,prog,pvideo_tex;}disp_rndr;
 struct {unsigned fbo,vao,vbo,prog;}s2t_rndr;
 unsigned gl_zpass_pixel_count_query_count;
} PGRAPHGLState;
typedef struct {
 PGRAPHGLState *gl_renderer_state;
 uint64_t primitive_mode,draw_arrays_length,inline_array_length,inline_elements_length,inline_buffer_length;
 bool framebuffer_in_use,flush_pending,sync_pending;
 uint64_t dma_color,dma_zeta;
 struct {uint64_t object_instance,dma_image_source,dma_image_dest;}context_surfaces_2d;
 struct {uint64_t context_surfaces;}image_blit;
 struct {unsigned type;} *renderer;
 uint32_t regs[2];
} PGRAPHState;
typedef struct {unsigned waits,pending,enabled;}NV2AWaitRow233;
#include "slot-actual.inc"
typedef struct {PGRAPHState pgraph;struct{unsigned state;int64_t deadline;}preserve227;struct{bool halt;}pfifo;struct{NV2AInventorySlot242 slots[2];}inventory242;}NV2AState;
static int64_t now,tick;
static int64_t qemu_clock_get_ns(int clock) {assert(clock==0);int64_t v=now;now+=tick;return v;}
static unsigned pgraph_reg_r(PGRAPHState *pg,unsigned reg){return pg->regs[reg];}
static void nv2a_wait233_fill(NV2AState*d,NV2AWaitRow233*row,unsigned k,unsigned v,bool f){(void)d;assert(k==9&&!v&&!f);memset(row,0,sizeof(*row));}
static void *g_nv2a_context_render=(void*)1,*g_nv2a_context_display=(void*)1;
#include "inventory-actual.inc"
static NV2AState *d;
static PGRAPHGLState *r;
static TextureLruNode *ts;
static ShaderBinding *ss;
static ShaderModuleCacheEntry *ms;
static VertexLruNode *vs;
static SurfaceBinding surfaces[129];
static struct {unsigned type;} renderer;
static unsigned checks,cases;
static void init(unsigned n,unsigned textures,unsigned shaders,unsigned modules,unsigned vertices) {
 memset(d,0,sizeof(*d));memset(r,0,sizeof(*r));
 d->preserve227.state=2;d->preserve227.deadline=1000000;d->pfifo.halt=true;
 d->pgraph.gl_renderer_state=r;d->pgraph.renderer=(void*)&renderer;renderer.type=1;
 now=99;tick=0;QTAILQ_INIT(&r->surfaces);memset(surfaces,0,sizeof(surfaces));
 for(unsigned i=0;i<n;i++){surfaces[i].vram_addr=4096*i;surfaces[i].size=4096;surfaces[i].draw_dirty=true;surfaces[i].access_cb=(void*)1;QTAILQ_INSERT_TAIL(&r->surfaces,&surfaces[i],entry);}
 lru_init(&r->texture_cache);lru_init(&r->shader_cache);lru_init(&r->shader_module_cache);lru_init(&r->element_cache);
 /* Free payloads intentionally remain poisoned. Actual helper may read only
  * node topology/in-use marker until a node is used. */
 memset(ts,0xa5,513*sizeof(*ts));memset(ss,0xa5,51201*sizeof(*ss));memset(ms,0xa5,51201*sizeof(*ms));memset(vs,0xa5,51201*sizeof(*vs));
 for(unsigned i=0;i<textures;i++)lru_add_free(&r->texture_cache,&ts[i].node);
 for(unsigned i=0;i<shaders;i++)lru_add_free(&r->shader_cache,&ss[i].node);
 for(unsigned i=0;i<modules;i++)lru_add_free(&r->shader_module_cache,&ms[i].node);
 for(unsigned i=0;i<vertices;i++)lru_add_free(&r->element_cache,&vs[i].node);
}
static void run(bool expected) {
 bool v=inventory242_copy(d,0);assert(v==expected);checks++;
 assert(d->inventory242.slots[0].valid==expected);checks++;
 assert(!r->shader_cache_lock.held);checks++;
 assert(d->pfifo.halt&&d->preserve227.state==2);checks++;
 assert(surfaces[0].draw_dirty&&surfaces[0].access_cb==(void*)1);checks++;
 cases++;
}
int main(void){
 d=calloc(1,sizeof(*d));r=calloc(1,sizeof(*r));ts=malloc(513*sizeof(*ts));ss=malloc(51201*sizeof(*ss));ms=malloc(51201*sizeof(*ms));vs=malloc(51201*sizeof(*vs));assert(d&&r&&ts&&ss&&ms&&vs);
 for(unsigned n=1;n<=129;n+=127){init(n,512,51200,51200,51200);run(n<=128);}
 init(129,512,51200,51200,51200);run(false);
 for(unsigned kind=0;kind<4;kind++){init(3,512+(kind==0),51200+(kind==1),51200+(kind==2),51200+(kind==3));run(false);}
 init(3,512,51200,51200,51200);r->shader_cache_lock.busy=true;run(false);
 init(3,512,51200,51200,51200);now=1000000;run(false);
 init(3,512,51200,51200,51200);tick=10;run(false);
 init(3,512,51200,51200,51200);r->texture_cache.num_used=1;r->texture_cache.num_free--;run(false);
 init(3,512,51200,51200,51200);r->shader_cache.num_used=1;r->shader_cache.num_free--;run(false);
 init(3,512,51200,51200,51200);r->shader_module_cache.num_used=1;r->shader_module_cache.num_free--;run(false);
 init(3,512,51200,51200,51200);r->element_cache.num_used=1;r->element_cache.num_free--;run(false);
 init(3,512,51200,51200,51200);
 TextureLruNode *t=container_of(lru_lookup(&r->texture_cache,1,NULL),TextureLruNode,node);memset(&t->key,0,sizeof(t->key));t->binding=NULL;t->possibly_dirty=true;
 ShaderBinding *s=container_of(lru_lookup(&r->shader_cache,2,NULL),ShaderBinding,node);s->initialized=true;s->program=(void*)1;s->save_thread=(void*)1;
 lru_lookup(&r->shader_module_cache,3,NULL);
 VertexLruNode *v=container_of(lru_lookup(&r->element_cache,4,NULL),VertexLruNode,node);v->initialized=true;
 run(true);assert(d->inventory242.slots[0].texture_count==1);checks++;
 assert(d->inventory242.slots[0].stats[38]==1&&d->inventory242.slots[0].stats[39]==1&&d->inventory242.slots[0].stats[40]==1&&d->inventory242.slots[0].stats[41]==1);checks++;
 assert(d->inventory242.slots[0].stats[43]==1&&d->inventory242.slots[0].stats[45]==1&&d->inventory242.slots[0].stats[46]==1);checks++;
 NV2AInventorySlot242 saved=d->inventory242.slots[0];assert(!inventory242_copy(d,0));assert(!memcmp(&saved,&d->inventory242.slots[0],sizeof(saved)));checks+=2;
 assert(!inventory242_copy(d,2));checks++;
 assert(inventory242_copy(d,1));checks++;
 for(unsigned state=0;state<8;state++){init(3,512,51200,51200,51200);d->preserve227.state=state;assert(inventory242_copy(d,0)==(state==2));assert(!r->shader_cache_lock.held);checks+=2;cases++;}
 free(vs);free(ms);free(ss);free(ts);free(r);free(d);
 printf("cases=%u checks=%u actual-helper=242\n",cases,checks);return 0;
}
