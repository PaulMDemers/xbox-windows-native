"""Exercise exact observer entry/seal functions with C11 atomic equivalents."""
import hashlib,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;out=Path('E:/Codex-archive/xbox-windows-native/reuse269-host002');out.mkdir(exist_ok=False)
s=(k/'watch.c').read_text()
def function(name):
    m=re.search(r'(?m)^(?:static )?bool '+name+r'\([^)]*\)\s*\{',s);assert m
    n=m.end();depth=1
    while depth:depth+=(s[n]=='{')-(s[n]=='}');n+=1
    return s[m.start():n]
functions='\n'.join(function(n) for n in ['pgraph_gl_reuse269_seal','x269_enter'])
test=r'''
#include <assert.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#define qatomic_load_acquire(p) atomic_load_explicit((p),memory_order_acquire)
#define qatomic_store_release(p,v) atomic_store_explicit((p),(v),memory_order_release)
#define qatomic_fetch_or(p,v) atomic_fetch_or_explicit((p),(v),memory_order_acq_rel)
#define qatomic_fetch_and(p,v) atomic_fetch_and_explicit((p),(v),memory_order_acq_rel)
static unsigned qatomic_cmpxchg(atomic_uint *p,unsigned expected,unsigned next) {atomic_compare_exchange_strong_explicit(p,&expected,next,memory_order_acq_rel,memory_order_acquire);return expected;}
#define qatomic_set(p,v) atomic_store_explicit((p),(v),memory_order_seq_cst)
static uint64_t qemu_get_thread_id(void) {return (uint64_t)pthread_self();}
static struct {atomic_uint enabled,busy,error;uint64_t thread;} x269;
static atomic_uint ready,start,inside,completed;
FUNCTIONS
static void *worker(void *arg) {
 (void)arg;x269.thread=qemu_get_thread_id();atomic_store(&ready,1);
 while(!atomic_load(&start))sched_yield();
 if(x269_enter()) {atomic_store(&inside,1);sched_yield();atomic_store(&inside,0);atomic_store(&completed,1);qatomic_fetch_and(&x269.busy,~1u);}
 return NULL;
}
int main(void) {
 for(unsigned i=0;i<4096;i++) {
  atomic_store(&x269.enabled,1);atomic_store(&x269.busy,0);atomic_store(&x269.error,0);
  atomic_store(&ready,0);atomic_store(&start,0);atomic_store(&inside,0);atomic_store(&completed,0);
  pthread_t t;assert(!pthread_create(&t,NULL,worker,NULL));while(!atomic_load(&ready))sched_yield();atomic_store(&start,1);
  if(i&1)sched_yield();
  while(!pgraph_gl_reuse269_seal())sched_yield();
  assert(!atomic_load(&inside));unsigned done=atomic_load(&completed);
  assert(!pthread_join(t,NULL));assert(done==atomic_load(&completed));assert(!atomic_load(&x269.error));
 }
 x269.thread=qemu_get_thread_id();atomic_store(&x269.enabled,1);atomic_store(&x269.busy,1);
 assert(!pgraph_gl_reuse269_seal());assert(!x269_enter());atomic_store(&x269.busy,0);assert(pgraph_gl_reuse269_seal());
 atomic_store(&x269.enabled,1);atomic_store(&x269.busy,0);x269.thread=0;assert(!x269_enter());assert(atomic_load(&x269.error)==2);assert(!atomic_load(&x269.busy));
 puts("PASS 4096 exact entry/seal races; busy and foreign-owner refusal");
}
'''.replace('FUNCTIONS',functions)
(out/'test.c').write_text(test);(out/'watch.c').write_bytes((k/'watch.c').read_bytes())
base='/mnt/e/Codex-archive/xbox-windows-native/reuse269-host002'
cmd=['wsl','-d','Ubuntu','-u','root','--','gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/test.c','-o',base+'/test']
c=subprocess.run(cmd,capture_output=True,timeout=60);r={'compile_exit':c.returncode,'compile_output':(c.stdout+c.stderr).decode(errors='replace'),'actual_gl':False,'functions_sha256':hashlib.sha256(functions.encode()).hexdigest(),'watch_sha256':hashlib.sha256((k/'watch.c').read_bytes()).hexdigest()}
if not c.returncode:
    t=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60);r.update(test_exit=t.returncode,test_output=(t.stdout+t.stderr).decode(errors='replace'))
r['passed']=r.get('test_exit')==0;r['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
dest=k/'seal-tests002.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(r);assert r['passed']
