/*273 Observation only; bounded270 accounting. One worker-owned generation per original unit object.
 * No release, GL object creation/deletion, guest command or guest memory write.
 * Binary observations stay in a unique private host directory. File/GL calls
 * have the outer owned-run watchdog; there is no claim of per-call cancellation.
 */
#include <glib/gstdio.h>
#define X269_LIMIT (2u*1024u*1024u)
#include "wire.h"
typedef struct {
    TextureBinding *identity;
    uint64_t generation;
    unsigned name,live,captured;
} X269Watch;
static struct {
    unsigned busy,enabled,error,core_error,transport_error,terminal;
    L270 accounting;
    uint64_t thread;
    char *dir;
    X269Watch watches[4];
} x269;
static FILE *x269_file(const char *leaf);
static bool x273_terminal(void);
unsigned pgraph_gl_reuse269_error(void) {
    return qatomic_read(&x269.error) | (qatomic_read(&x269.core_error)<<8) |
        (qatomic_read(&x269.transport_error)<<16);
}
bool pgraph_gl_reuse269_seal(void)
{
    qatomic_store_release(&x269.enabled,0);
    /* Closed and active share one atomic word: no cross-variable stale load. */
    if (qatomic_fetch_or(&x269.busy,2u)&1u) return false;
    return x273_terminal();
}

static bool x269_enter(void)
{
    if (!qatomic_load_acquire(&x269.enabled)) return false;
    unsigned gate=qatomic_cmpxchg(&x269.busy,0u,1u);
    if (gate) {if (!(gate&2u)) qatomic_fetch_or(&x269.error,1u);return false;}
    if (qemu_get_thread_id()!=x269.thread) {
        qatomic_fetch_or(&x269.error,2u);qatomic_fetch_and(&x269.busy,~1u);return false;
    }
    return true;
}
static FILE *x269_file(const char *leaf)
{
    char *path=g_build_filename(x269.dir,leaf,NULL);
    int fd=g_open(path,O_WRONLY|O_CREAT|O_EXCL|O_BINARY,0600);g_free(path);
    if (fd<0) return NULL;
    FILE *f=fdopen(fd,"wb");if (!f) close(fd);return f;
}
static bool x273_terminal(void)
{
    unsigned terminal=qatomic_cmpxchg(&x269.terminal,0u,1u);
    if (terminal) return terminal==2;
    if (qatomic_load_acquire(&x269.busy)!=2 || qatomic_load_acquire(&x269.enabled)) {
        qatomic_fetch_or(&x269.error,8u);qatomic_store_release(&x269.terminal,3u);return false;
    }
    uint64_t captures=0;
    for (unsigned i=0;i<4;i++) if (x269.watches[i].captured==1) captures|=UINT64_C(1)<<i;
    X273Meta m={qatomic_read(&x269.error),qatomic_read(&x269.transport_error),x269.thread,
        qatomic_load_acquire(&x269.busy),qatomic_load_acquire(&x269.enabled),1,captures};
    uint8_t bytes[X273_CAPACITY];unsigned n=x273_encode(&x269.accounting,&m,bytes,sizeof(bytes));
    FILE *f=n?x269_file("terminal273.bin"):NULL;bool okay=f!=NULL;
    if (f) {okay=fwrite(bytes,n,1,f)==1;okay &= fclose(f)==0;}
    if (!okay) qatomic_fetch_or(&x269.transport_error,1u);
    qatomic_store_release(&x269.terminal,okay?2u:3u);
    return okay;
}
static void x273_record(unsigned slot,TextureBinding *b,unsigned kind,unsigned code)
{
    /* Called only under the single-owner gate, before any actual final free. */
    l270_observe(&x269.accounting,slot,(uint64_t)(uintptr_t)b,
        x269.watches[slot].generation,kind,code);
    qatomic_store_release(&x269.core_error,x269.accounting.error);
}
static TextureLruNode *x269_cache(PGRAPHGLState *r,TextureBinding *b)
{
    unsigned walked=0,found=0;TextureLruNode *result=NULL;LruNode *node;
    QTAILQ_FOREACH(node,&r->texture_cache.global,next_global) {
        if (++walked>512) return NULL;
        if (!lru_is_node_in_use(&r->texture_cache,node)) continue;
        TextureLruNode *t=container_of(node,TextureLruNode,node);
        if (t->binding==b) {result=t;found++;}
    }
    return found==1?result:NULL;
}
static bool x269_snapshot(NV2AState *d,unsigned index,unsigned stage)
{
    X269Watch *w=&x269.watches[index];TextureBinding *b=w->identity;
    PGRAPHGLState *r=d->pgraph.gl_renderer_state;
    TextureLruNode *t=x269_cache(r,b);uintptr_t context[4];
    if (!w->live || !t || b->gl_texture!=w->name || b->gl_target!=GL_TEXTURE_2D ||
        !glo_context_observe267(g_nv2a_context_render,context)) return false;
    uint64_t size=memory_region_size(d->vram),a=t->key.texture_vram_offset,n=t->key.texture_length;
    uint64_t pa=t->key.palette_vram_offset,pn=t->key.palette_length;
    if (!n || n>X269_LIMIT || pn>4096 || a>size || n>size-a || pa>size || pn>size-pa) return false;
    TextureKey key=t->key;
    uint8_t *source=g_memdup2(d->vram_ptr+a,n),*palette=pn?g_memdup2(d->vram_ptr+pa,pn):NULL;
    GLint active=0,bound=0,pbo=0,pack[8],width=0,height=0,format=0,type=0;
    GLenum pnames[]={GL_PACK_ALIGNMENT,GL_PACK_ROW_LENGTH,GL_PACK_IMAGE_HEIGHT,
        GL_PACK_SKIP_PIXELS,GL_PACK_SKIP_ROWS,GL_PACK_SKIP_IMAGES,GL_PACK_SWAP_BYTES,GL_PACK_LSB_FIRST};
    glGetIntegerv(GL_ACTIVE_TEXTURE,&active);glActiveTexture(GL_TEXTURE0);
    glGetIntegerv(GL_TEXTURE_BINDING_2D,&bound);glGetIntegerv(GL_PIXEL_PACK_BUFFER_BINDING,&pbo);
    for (unsigned i=0;i<8;i++) glGetIntegerv(pnames[i],&pack[i]);
    bool okay=glGetError()==GL_NO_ERROR;
    glBindTexture(GL_TEXTURE_2D,b->gl_texture);
    glGetTexLevelParameteriv(GL_TEXTURE_2D,0,GL_TEXTURE_WIDTH,&width);
    glGetTexLevelParameteriv(GL_TEXTURE_2D,0,GL_TEXTURE_HEIGHT,&height);
    glGetTexLevelParameteriv(GL_TEXTURE_2D,0,GL_TEXTURE_INTERNAL_FORMAT,&format);
    glGetTexLevelParameteriv(GL_TEXTURE_2D,0,GL_TEXTURE_RED_TYPE,&type);
    uint64_t bytes=width>0 && height>0?(uint64_t)width*height*4:0;
    okay &= width>0 && height>0 && bytes<=X269_LIMIT && bytes>0 && type==GL_UNSIGNED_NORMALIZED;
    uint8_t *pixels=okay?g_malloc(bytes):NULL;
    if (okay) {
        glBindBuffer(GL_PIXEL_PACK_BUFFER,0);
        for (unsigned i=0;i<8;i++) glPixelStorei(pnames[i],i==0?1:0);
        glGetTexImage(GL_TEXTURE_2D,0,GL_RGBA,GL_UNSIGNED_BYTE,pixels);
        okay=glGetError()==GL_NO_ERROR;
    }
    for (unsigned i=0;i<8;i++) glPixelStorei(pnames[i],pack[i]);
    glBindBuffer(GL_PIXEL_PACK_BUFFER,pbo);glBindTexture(GL_TEXTURE_2D,bound);glActiveTexture(active);
    okay &= glGetError()==GL_NO_ERROR;
    GLint verify=0;glGetIntegerv(GL_ACTIVE_TEXTURE,&verify);okay &= verify==active;
    glActiveTexture(GL_TEXTURE0);glGetIntegerv(GL_TEXTURE_BINDING_2D,&verify);okay &= verify==bound;
    glGetIntegerv(GL_PIXEL_PACK_BUFFER_BINDING,&verify);okay &= verify==pbo;
    for (unsigned i=0;i<8;i++) {glGetIntegerv(pnames[i],&verify);okay &= verify==pack[i];}
    glActiveTexture(active);okay &= glGetError()==GL_NO_ERROR;
    /* Double sampling detects observed changes, not arbitrary CPU ABA races. */
    bool stable=!memcmp(source,d->vram_ptr+a,n) && (!pn || !memcmp(palette,d->vram_ptr+pa,pn));
    if (okay) {
        uint64_t header[24]={0x3337324e5758ULL,273,stage,index,w->generation,
            (uintptr_t)b,b->gl_texture,b->refcnt,b->data_hash,(uint64_t)b->draw_time,
            a,n,pa,pn,width,height,format,bytes,sizeof(key),stable,0,
            qemu_get_thread_id(),context[0],1};
        char leaf[64];snprintf(leaf,sizeof(leaf),"unit-%u-stage-%u.bin",index,stage);
        FILE *f=x269_file(leaf);okay=f!=NULL;
        if (f) {
            okay=fwrite(header,sizeof(header),1,f)==1 && fwrite(&key,sizeof(key),1,f)==1 &&
                fwrite(source,n,1,f)==1 && (!pn || fwrite(palette,pn,1,f)==1) && fwrite(pixels,bytes,1,f)==1;
            okay &= fclose(f)==0;
        }
    }
    g_free(source);g_free(palette);g_free(pixels);
    return okay && stable;
}
bool pgraph_gl_reuse269_arm(NV2AState *d)
{
    if (qatomic_read(&x269.enabled) || qatomic_read(&x269.busy) || x269.dir || x269.accounting.armed) return false;
    const char *dir=getenv("XWN_REUSE269_DIR");if (!dir || !*dir) return false;
    x269.dir=g_strdup(dir);x269.thread=qemu_get_thread_id();
    PGRAPHGLState *r=d->pgraph.gl_renderer_state;
    for (unsigned i=0;i<4;i++) {
        TextureBinding *b=r->texture_binding[i];
        if (!b || b->refcnt!=2 || pgraph_is_texture_enabled(&d->pgraph,i) || !x269_cache(r,b)) return false;
        for (unsigned j=0;j<i;j++) if (b==x269.watches[j].identity || b->gl_texture==x269.watches[j].name) return false;
        x269.watches[i]=(X269Watch){b,i+1,b->gl_texture,1,0};
        if (!x269_snapshot(d,i,0)) return false;
    }
    uint64_t ids[4],generations[4];
    for (unsigned i=0;i<4;i++) {ids[i]=(uint64_t)(uintptr_t)x269.watches[i].identity;generations[i]=x269.watches[i].generation;}
    if (!l270_arm(&x269.accounting,ids,generations)) {
        qatomic_store_release(&x269.core_error,x269.accounting.error);return false;
    }
    qatomic_store_release(&x269.enabled,1);return true;
}
static void x269_bound(NV2AState *d,unsigned unit,TextureBinding *b,unsigned path)
{
    if (!x269_enter()) return;
    for (unsigned i=0;i<4;i++) {
        X269Watch *w=&x269.watches[i];
        if (!w->live || w->identity!=b) continue;
        x273_record(i,b,L270_BIND,(unit<<8)|path);
        if (!w->captured) {
            /* First actual normal bind only; never invoke the binder here. */
            if (x269_snapshot(d,i,1)) w->captured=1;
            else {w->captured=2;qatomic_fetch_or(&x269.transport_error,2u);}
        }
    }
    qatomic_fetch_and(&x269.busy,~1u);
}
static void x269_destroying(TextureBinding *b)
{
    if (!x269_enter()) return;
    for (unsigned i=0;i<4;i++) {
        X269Watch *w=&x269.watches[i];
        if (!w->live || w->identity!=b) continue;
        x273_record(i,b,L270_DEC,b->refcnt);
        /* Tombstone before original destruction; never inspect a dead identity. */
        if (b->refcnt==1) w->live=0;
    }
    qatomic_fetch_and(&x269.busy,~1u);
}
