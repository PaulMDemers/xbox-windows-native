"""Freeze inputs and test new accounting plus exact existing one-word gate."""
import hashlib,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
out=Path('E:/Codex-archive/xbox-windows-native/lifetime270-host001')
assert not out.exists(); out.mkdir(parents=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
prior=json.loads((k.parent/'unit-reuse269/final-review.json').read_text())
capture=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/reuse269/watch-emu001')
events=[]; pins={}
for i in range(129):
    name=f'event-{i:03}.txt'; data=(capture/name).read_bytes()
    assert sha(data)==prior['private_capture'][name]['sha256']
    pins[name]=sha(data)
    e=dict((key,int(val)) for key,val in re.findall(r'(\w+)=(\d+)',data.decode()))
    assert e['seq']==i
    events.append(e)
assert events[0]['kind']==1 and events[-1]['kind']==9
assert all(e['kind'] in (2,3) for e in events[1:-1])
actual='#define ACTUAL_COUNT 127u\nstatic const unsigned actual[127][3]={\n'
actual+=''.join('{%d,%d,%d},\n'%(e['kind'],e['unit'],e['code']) for e in events[1:-1])+'};\n'
(out/'actual-prefix.h').write_text(actual)
for name in ['lifetime.h','test.c','test-host.py']:(out/name).write_bytes((k/name).read_bytes())
s=(k.parent/'unit-reuse269/watch.c').read_text()
def function(name):
    m=re.search(r'(?m)^(?:static )?bool '+name+r'\([^)]*\)\s*\{',s);assert m
    n=m.end();depth=1
    while depth:depth+=(s[n]=='{')-(s[n]=='}');n+=1
    return s[m.start():n]
gate='\n'.join(function(n) for n in ['pgraph_gl_reuse269_seal','x269_enter'])
race=r'''
#include "lifetime.h"
#include <assert.h>
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
static atomic_uint ready,start;
static L270 state;
FUNCTIONS
static void *worker(void *arg) {
 (void)arg;x269.thread=qemu_get_thread_id();atomic_store(&ready,1);
 while(!atomic_load(&start))sched_yield();
 if(x269_enter()) {
  for(unsigned i=0;i<64;i++) assert(l270_observe(&state,0,101,11,L270_DEC,2));
  assert(l270_observe(&state,0,101,11,L270_BIND,1));
  assert(l270_observe(&state,0,101,11,L270_DEC,1));
  qatomic_fetch_and(&x269.busy,~1u);
 }
 return NULL;
}
int main(void) {
 for(unsigned i=0;i<4096;i++) {
  memset(&state,0,sizeof(state));uint64_t id[]={101,102,103,104},gen[]={11,12,13,14};assert(l270_arm(&state,id,gen));
  atomic_store(&x269.enabled,1);atomic_store(&x269.busy,0);atomic_store(&x269.error,0);
  atomic_store(&ready,0);atomic_store(&start,0);
  pthread_t t;assert(!pthread_create(&t,NULL,worker,NULL));while(!atomic_load(&ready))sched_yield();atomic_store(&start,1);
  if(i&1)sched_yield();
  while(!pgraph_gl_reuse269_seal())sched_yield();
  L270 sealed=state;assert(state.sequence==0 || state.sequence==66);
  assert(!pthread_join(t,NULL));assert(!memcmp(&sealed,&state,sizeof(state)));assert(!atomic_load(&x269.error));
  assert(l270_complete(&state));assert(!x269_enter());
 }
 x269.thread=qemu_get_thread_id();atomic_store(&x269.enabled,1);atomic_store(&x269.busy,1);atomic_store(&x269.error,0);
 assert(!x269_enter());assert(atomic_load(&x269.error)==1);assert(!pgraph_gl_reuse269_seal());
 qatomic_fetch_and(&x269.busy,~1u);assert(pgraph_gl_reuse269_seal());assert(!x269_enter());
 atomic_store(&x269.enabled,1);atomic_store(&x269.busy,0);atomic_store(&x269.error,0);x269.thread=0;
 assert(!x269_enter());assert(atomic_load(&x269.error)==2);assert(!atomic_load(&x269.busy));
 puts("PASS 4096 exact gate/accounting publication races; busy/foreign-owner/closed refusals");
}
'''.replace('FUNCTIONS',gate)
(out/'gate-test.c').write_text(race)
base='/mnt/e/Codex-archive/xbox-windows-native/lifetime270-host001'
result=dict(scope='Host accounting and C11 equivalents of exact269 gate; no renderer or guest integration',
            prior_run_remains_failed=True,actual_prefix_events=127,prior_event_pins=pins,
            exact_gate_sha256=sha(gate.encode()),guest_executed=False,renderer_modified=False,physical_access=False,tests=[])
for source in ['test.c','gate-test.c']:
    command=['wsl','-d','Ubuntu','-u','root','--','gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/'+source,'-o',base+'/'+source+'.exe']
    c=subprocess.run(command,capture_output=True,timeout=60)
    t=dict(source=source,command=command,compile_exit=c.returncode,compile_output=(c.stdout+c.stderr).decode(errors='replace'))
    if not c.returncode:
        r=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/'+source+'.exe'],capture_output=True,timeout=60)
        t.update(test_exit=r.returncode,test_output=(r.stdout+r.stderr).decode(errors='replace'))
    result['tests'].append(t)
result['passed']=all(t.get('test_exit')==0 for t in result['tests'])
result['files']={p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file()}
dest=k/'host-tests001.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({key:val for key,val in result.items() if key not in ['prior_event_pins','files']},indent=2))
assert result['passed']
