/* Actual locked graph collector; live QEMU/GL objects modeled explicitly. */
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include "queue.h"
#include "admission.h"
#include "fixture.h"
#define container_of(p,t,m) ((t*)((char*)(p)-offsetof(t,m)))
#define GL_TEXTURE_2D 3553
typedef struct SurfaceBinding {uint64_t vram_addr,size,gl_buffer;void *access_cb;unsigned draw_dirty,download_pending,cpu_write_evict_pending,upload_pending;QTAILQ_ENTRY(SurfaceBinding)entry;} SurfaceBinding;
typedef struct TextureBinding {uint64_t gl_texture,gl_target,refcnt;} TextureBinding;
typedef struct LruNode {unsigned live;QTAILQ_ENTRY(LruNode) next_global;} LruNode;
typedef struct {QTAILQ_HEAD(,LruNode)global;} Cache;
typedef struct {LruNode node;TextureBinding *binding;struct {uint64_t texture_vram_offset,texture_length,palette_vram_offset,palette_length;}key;} TextureLruNode;
typedef struct {QTAILQ_HEAD(,SurfaceBinding)surfaces;SurfaceBinding *color_binding,*zeta_binding;Cache texture_cache;TextureBinding *texture_binding[4];} PGRAPHGLState;
typedef struct {PGRAPHGLState *gl_renderer_state;} PGRAPHState;
typedef struct {PGRAPHState pgraph;} NV2AState;
typedef struct {X277Proof proof278;uint64_t allocations278[4];} X265State;
static bool lru_is_node_in_use(Cache*c,LruNode*n){(void)c;return n->live;}
static int qemu_strtou64(const char*s,const char**end,int base,uint64_t*v){char*e;errno=0;*v=strtoull(s,&e,base);*end=e;return errno?1:0;}
/* ACTUAL_FUNCTIONS */
static NV2AState d;static PGRAPHGLState r;static X265State s;
static SurfaceBinding surface[129];static TextureBinding textures[4];static TextureLruNode cache[513];
static unsigned checks;
#define CHECK(x) do{assert(x);checks++;}while(0)
static void setup(void){
 memset(&d,0,sizeof(d));memset(&r,0,sizeof(r));memset(&s,0,sizeof(s));memset(surface,0,sizeof(surface));memset(textures,0,sizeof(textures));memset(cache,0,sizeof(cache));
 d.pgraph.gl_renderer_state=&r;QTAILQ_INIT(&r.surfaces);QTAILQ_INIT(&r.texture_cache.global);
 for(unsigned i=0;i<4;i++){
  X277Surface t=fixture.graph[0].surfaces[i];surface[i].vram_addr=t.begin;surface[i].size=t.bytes;surface[i].gl_buffer=t.name;surface[i].access_cb=(void*)(uintptr_t)t.callback;surface[i].draw_dirty=1;
  QTAILQ_INSERT_TAIL(&r.surfaces,&surface[i],entry);if(t.roles&1)r.color_binding=&surface[i];if(t.roles&2)r.zeta_binding=&surface[i];
  X277Texture a=fixture.textures[i];s.allocations278[i]=a.allocation;textures[i]=(TextureBinding){a.name,GL_TEXTURE_2D,2};r.texture_binding[i]=&textures[i];
  cache[i].node.live=1;cache[i].binding=&textures[i];cache[i].key.texture_vram_offset=a.source;cache[i].key.texture_length=a.source_bytes;
  QTAILQ_INSERT_TAIL(&r.texture_cache.global,&cache[i].node,next_global);
 }
}
int main(void){
 setup();CHECK(x278_graph(&d,&s,0));CHECK(x278_graph(&d,&s,1));CHECK(!memcmp(&s.proof278.graph[0],&s.proof278.graph[1],sizeof(X277Graph)));
 CHECK(!x278_graph(&d,&s,0));CHECK(!x278_graph(&d,&s,1));
 for(unsigned i=0;i<4;i++){
  setup();r.texture_binding[i]=NULL;CHECK(!x278_graph(&d,&s,0));
  setup();cache[i].node.live=0;CHECK(!x278_graph(&d,&s,0));
  setup();textures[i].gl_target=0;CHECK(!x278_graph(&d,&s,0));
  setup();cache[4]=cache[i];QTAILQ_INSERT_TAIL(&r.texture_cache.global,&cache[4].node,next_global);CHECK(!x278_graph(&d,&s,0));
  for(unsigned f=0;f<5;f++){
   setup();CHECK(x278_graph(&d,&s,0));
   if(f==0)textures[i].refcnt++;
   if(f==1)textures[i].gl_texture++;
   if(f==2)cache[i].key.texture_vram_offset++;
   if(f==3)cache[i].key.texture_length++;
   if(f==4)cache[i].key.palette_length++;
   CHECK(!x278_graph(&d,&s,1));
  }
 }
 setup();for(unsigned i=4;i<129;i++)QTAILQ_INSERT_TAIL(&r.surfaces,&surface[i],entry);
 CHECK(!x278_graph(&d,&s,0));CHECK(s.proof278.graph[0].count==128&&s.proof278.graph[0].error);
 setup();for(unsigned i=4;i<513;i++)QTAILQ_INSERT_TAIL(&r.texture_cache.global,&cache[i].node,next_global);
 CHECK(!x278_graph(&d,&s,0));
 uint64_t a[4];CHECK(x278_parse("textures278,0,4096,8192,12288",a));CHECK(a[0]==0&&a[3]==12288);
 const char *bad[]={"capture,1","textures278,0,4096,8192,12288x","textures278,0,4096,8192,12288,0","textures278,0,4096,8192","textures278,+0,4096,8192,12288","textures278,00,4096,8192,12288","textures278, 0,4096,8192,12288","textures278,-1,4096,8192,12288","textures278,1,4096,8192,12288","textures278,0,0,8192,12288","textures278,67108864,4096,8192,12288","textures278,18446744073709551616,4096,8192,12288"};
 for(unsigned i=0;i<sizeof(bad)/sizeof(bad[0]);i++)CHECK(!x278_parse(bad[i],a));
 printf("PASS %u actual collector/request checks; QEMU cache and GL objects modeled, no runtime graph claim\n",checks);return 0;
}
