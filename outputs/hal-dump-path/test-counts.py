"""Compile the actual proposed counter function with atomic host shims and boundary/concurrency checks."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;source=(k/'artifacts/halpnpdd.c').read_text()
start=source.index('static NTSTATUS\nHalpUpdateSpecialPathCount(');end=source.index('\n#endif',start);function=source[start:end]
harness=r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <pthread.h>
typedef int32_t LONG, NTSTATUS;
typedef LONG *PLONG;
typedef unsigned char BOOLEAN;
#define MAXLONG INT32_MAX
#define STATUS_SUCCESS 0
#define STATUS_INVALID_PARAMETER ((int32_t)0xc000000d)
#define STATUS_INTEGER_OVERFLOW ((int32_t)0xc0000095)
static LONG InterlockedCompareExchange(PLONG p,LONG next,LONG old) {
    return __sync_val_compare_and_swap(p,old,next);
}
''' + function + r'''
static LONG shared;
static void *worker(void *unused) {
    (void)unused;
    for(int i=0;i<50000;i++) {
        assert(HalpUpdateSpecialPathCount(&shared,1)==0);
        assert(HalpUpdateSpecialPathCount(&shared,0)==0);
    }
    return NULL;
}
int main(void) {
    LONG paging=0,dump=0,bad=-1,limit=MAXLONG;
    assert(HalpUpdateSpecialPathCount(&paging,0)==STATUS_INVALID_PARAMETER && paging==0);
    assert(HalpUpdateSpecialPathCount(&bad,0)==STATUS_INVALID_PARAMETER && bad==-1);
    assert(HalpUpdateSpecialPathCount(&bad,1)==STATUS_INVALID_PARAMETER && bad==-1);
    assert(HalpUpdateSpecialPathCount(&limit,1)==STATUS_INTEGER_OVERFLOW && limit==MAXLONG);
    assert(HalpUpdateSpecialPathCount(&limit,0)==0 && limit==MAXLONG-1);
    assert(HalpUpdateSpecialPathCount(&limit,1)==0 && limit==MAXLONG);
    assert(HalpUpdateSpecialPathCount(&paging,1)==0);
    assert(HalpUpdateSpecialPathCount(&dump,1)==0);
    assert(HalpUpdateSpecialPathCount(&dump,1)==0);
    assert(HalpUpdateSpecialPathCount(&paging,0)==0 && paging==0 && dump==2);
    assert(HalpUpdateSpecialPathCount(&dump,0)==0 && dump==1);
    assert(HalpUpdateSpecialPathCount(&dump,0)==0 && dump==0);
    assert(HalpUpdateSpecialPathCount(&dump,0)==STATUS_INVALID_PARAMETER && dump==0);
    pthread_t threads[8];
    for(int i=0;i<8;i++) assert(pthread_create(&threads[i],NULL,worker,NULL)==0);
    for(int i=0;i<8;i++) assert(pthread_join(threads[i],NULL)==0);
    assert(shared==0);
    puts("PASS boundary counts, independent types, 400000 concurrent add/remove pairs");
    return 0;
}
'''
out=k/'artifacts/counter-test.c';out.write_text(harness);exe=k/'artifacts/counter-test'
cmd=['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pthread',str(out),'-o',str(exe)]
subprocess.run(cmd,check=True);result=subprocess.check_output([str(exe)],text=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(scope=__doc__,source_sha256=sha(k/'artifacts/halpnpdd.c'),extracted_function_sha256=hashlib.sha256(function.encode()).hexdigest(),test_script_sha256=sha(Path(__file__)),harness_sha256=sha(out),executable_sha256=sha(exe),compiler_version=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0],command=cmd,output=result,passed=True,limits='Host counter semantics only; not a guest kernel, dispatch, power-state or dump-write qualification.')
(k/'counter-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(result)
