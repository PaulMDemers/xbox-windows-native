"""Execute exact pinned texture finalizer functions with a counted GL stub.

This is host ownership accounting, not a GL context or guest retirement test.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = Path('E:/Codex-archive/xbox-windows-native/retirement264-source001')
OUT = Path('E:/Codex-archive/xbox-windows-native/retirement264-host001')
WSL = '/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def function(text, name):
    m = re.search(r'(?m)^(?:static )?void ' + name + r'\([^)]*\)\s*\{', text)
    assert m, name
    depth, pos = 1, m.end()
    while depth:
        depth += (text[pos] == '{') - (text[pos] == '}')
        pos += 1
    return text[m.start():pos]

def main():
    assert not OUT.exists(), 'unique host attempt required'
    pins = json.loads((ROOT / 'outputs/surface-pending263/renderer-source-pins001.json').read_text())
    name = 'include/qemu/queue.h'
    queue = subprocess.check_output(['wsl', '-d', 'Ubuntu', '-u', 'root', '--', 'cat', WSL + '/' + name], timeout=30)
    assert sha(queue) == pins[name]
    texture_path = 'hw/xbox/nv2a/pgraph/gl/texture.c'
    raw = (SOURCE / texture_path).read_bytes()
    assert sha(raw) == pins[texture_path]
    text = raw.decode()
    names = ['texture_binding_destroy', 'texture_cache_entry_post_evict', 'pgraph_gl_finalize_textures']
    extracted = '\n\n'.join(function(text, n) for n in names)
    lru = (SOURCE / 'include/qemu/lru.h').read_bytes()
    assert sha(lru) == pins['include/qemu/lru.h']
    (OUT / 'qemu').mkdir(parents=True)
    (OUT / 'qemu/queue.h').write_bytes(queue)
    (OUT / 'qemu/lru.h').write_bytes(lru)
    # Preserve original license and exact extracted function bodies.
    (OUT / 'actual-functions.h').write_text(text[:text.index('#include')] + extracted + '\n', encoding='utf-8')
    harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "qemu/lru.h"
#define NV2A_MAX_TEXTURES 4
#define container_of(ptr,type,member) ((type *)((char *)(ptr)-offsetof(type,member)))
typedef void *gpointer;
typedef unsigned GLuint;
typedef struct { unsigned refcnt; GLuint gl_texture; } TextureBinding;
typedef struct { LruNode node; TextureBinding *binding; bool possibly_dirty; } TextureLruNode;
typedef struct { TextureBinding *texture_binding[4]; Lru texture_cache; TextureLruNode *texture_cache_entries; } PGRAPHGLState;
typedef struct { PGRAPHGLState *gl_renderer_state; } PGRAPHState;
static unsigned deletes, frees;
static void glDeleteTextures(int n, const GLuint *ids) { assert(n==1 && *ids); deletes++; }
static void g_free(void *p) { assert(p); frees++; free(p); }
#include "actual-functions.h"

static unsigned cases;
static void run_case(unsigned units, bool shared, bool uncached, bool release_units)
{
    PGRAPHGLState *r=calloc(1,sizeof(*r)); assert(r);
    PGRAPHState pg={r}; lru_init(&r->texture_cache);
    r->texture_cache.post_node_evict=texture_cache_entry_post_evict;
    r->texture_cache_entries=calloc(24,sizeof(TextureLruNode)); assert(r->texture_cache_entries);
    TextureBinding *objects[25]; unsigned count=24;
    for(unsigned i=0;i<24;i++) {
        objects[i]=calloc(1,sizeof(*objects[i])); assert(objects[i]);
        objects[i]->refcnt=1; objects[i]->gl_texture=i+1;
        TextureLruNode *t=&r->texture_cache_entries[i]; t->binding=objects[i];
        lru_add_free(&r->texture_cache,&t->node);
        // Populate real queue and accounting with 24 in-use cache references.
        t->node.hash=i;
        QTAILQ_INSERT_TAIL(&r->texture_cache.bins[i],&t->node,next_bin);
        r->texture_cache.num_free--; r->texture_cache.num_used++;
    }
    if(uncached) { objects[count]=calloc(1,sizeof(*objects[count])); assert(objects[count]); objects[count]->gl_texture=count+1; count++; }
    for(unsigned i=0;i<units;i++) {
        unsigned index=uncached?24:(shared?0:i);
        r->texture_binding[i]=objects[index]; objects[index]->refcnt++;
    }
    unsigned before_deletes=deletes, before_frees=frees;
    if(release_units) for(unsigned i=0;i<4;i++) if(r->texture_binding[i]) {
        texture_binding_destroy(r->texture_binding[i]); r->texture_binding[i]=NULL;
    }
    pgraph_gl_finalize_textures(&pg);
    unsigned retained=release_units?0:(uncached||shared?(units?1:0):units);
    assert(deletes-before_deletes==count-retained);
    assert(frees-before_frees==count-retained);
    assert(r->texture_cache.num_used==0 && r->texture_cache_entries==NULL);
    for(unsigned i=0;i<4;i++) assert(!r->texture_binding[i]);
    // Clean deliberate retained references AFTER measuring the exact finalizer.
    // This makes ASan a harness check; it is not a claim that the finalizer freed them.
    if(retained) {
        for(unsigned i=0;i<retained;i++) {
            unsigned index=uncached?24:i;
            unsigned refs=(uncached||shared)?units:1;
            assert(objects[index]->refcnt==refs);
            while(refs--) texture_binding_destroy(objects[index]);
        }
    }
    assert(deletes-before_deletes==count && frees-before_frees==count);
    printf("case units=%u shared=%u uncached=%u release_first=%u retained_by_original=%u\n",
           units,shared,uncached,release_units,retained);
    free(r); cases++;
}
int main(void) {
    for(unsigned units=0;units<=4;units++) for(unsigned shared=0;shared<2;shared++)
        for(unsigned fixed=0;fixed<2;fixed++) run_case(units,shared,false,fixed);
    for(unsigned units=1;units<=4;units++) for(unsigned fixed=0;fixed<2;fixed++)
        run_case(units,true,true,fixed);
    printf("PASS %u host lifetime cases; GL calls are counted stubs, no guest test\n",cases);
    return 0;
}
'''
    (OUT / 'test.c').write_text(harness, encoding='utf-8')
    base = '/mnt/e/Codex-archive/xbox-windows-native/retirement264-host001'
    command = ['wsl', '-d', 'Ubuntu', '-u', 'root', '--', 'gcc', '-std=gnu11', '-O1', '-g',
               '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-Wall', '-Wextra',
               '-Werror', '-Wno-unused-parameter', '-I' + base, base + '/test.c', '-o', base + '/test']
    result = dict(scope='host reference accounting only; stub GL; no patch applied',
                  exact_functions={n:sha(function(text,n).encode()) for n in names},
                  queue_sha256=sha(queue), texture_source_sha256=sha(raw), command=command)
    compiled = subprocess.run(command, capture_output=True, timeout=60)
    result['compile_exit'] = compiled.returncode
    result['compile_output'] = (compiled.stdout + compiled.stderr).decode(errors='replace')
    if compiled.returncode == 0:
        run = subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'], capture_output=True, timeout=60)
        result['test_exit'] = run.returncode
        result['test_output'] = (run.stdout + run.stderr).decode(errors='replace')
    result['passed'] = result.get('test_exit') == 0
    result['files'] = {str(p.relative_to(OUT)):sha(p.read_bytes()) for p in OUT.rglob('*') if p.is_file()}
    with (HERE/'texture-lifetime-test001.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2); f.write('\n')
    print(json.dumps(result,indent=2))
    assert result['passed']

if __name__ == '__main__':
    main()
