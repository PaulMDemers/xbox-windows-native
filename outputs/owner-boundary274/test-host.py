"""Freeze and test actual admission/context functions; no live GL/CPU jobs."""
import hashlib,importlib.util,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
out=Path('E:/Codex-archive/xbox-windows-native/boundary274-host001');out.mkdir(exist_ok=False)
dest=k/'host-tests001.json';assert not dest.exists()
parent=Path('E:/Codex-archive/xbox-windows-native/lifetime273-build001/source')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((k.parent/'owned-lifetime273/renderer-source-pins001.json').read_text())
for name in ['hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pgraph/gl/texture.c']:
    p=parent/name;assert sha(p)==pins[name]
    q=out/'source'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
for name in ['patch-renderer.py','boundary.h','test-host.py']:(out/name).write_bytes((k/name).read_bytes())
spec=importlib.util.spec_from_file_location('patch274',k/'patch-renderer.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
result=dict(passed=False,guest_executed=False,gl_executed=False,scope='Actual admission and native-context matching functions; simulated field values, no CPU queue or GL fences executed')
try:
    mod.apply(out/'source')
    def extract(source,name):
        m=re.search(r'(?m)^(?:static )?(?:bool|void|unsigned) '+name+r'\([^)]*\)\s*\{',source);assert m,name
        n=m.end();depth=1
        while depth:depth+=(source[n]=='{')-(source[n]=='}');n+=1
        return source[m.start():n]
    renderer=(out/'source/hw/xbox/nv2a/pgraph/gl/renderer.c').read_text()
    texture=(out/'source/hw/xbox/nv2a/pgraph/gl/texture.c').read_text()
    functions='\n'.join([extract(renderer,'x274_context_match'),extract(texture,'pgraph_gl_reuse269_error'),extract(texture,'pgraph_gl_reuse274_ready')])
    source='''#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "boundary.h"
typedef struct {uint64_t (*rows)[8];unsigned count;} Rows;
typedef struct {Rows ledger;} X265State;
static struct {unsigned enabled,busy,terminal,error,core_error,transport_error;uint64_t thread;} x269;
#define qatomic_read(p) (*(p))
#define qatomic_load_acquire(p) (*(p))
'''+functions+'''
int main(void) {
    unsigned checks=0;
    X274Evidence good={.original_owner=91,.actual_owner=91,.get=128,.put=128,.ready=1,
        .cpu0_done=1,.cpu1_done=1,.render_fenced=1,.display_fenced=1,.contexts_match=1};
    assert(!x274_admit(&good,0)&&!x274_admit(&good,1));checks+=2;
    for(unsigned mask=0;mask<(1u<<18);mask++) {
        X274Evidence e=good;
        if(mask&1)e.actual_owner++;
        if(mask&2)e.get++;
        if(mask&4)e.method_error=1;
        if(mask&8)e.pending=1;
        if(mask&16)e.primitive=1;
        if(mask&32)e.draw=1;
        if(mask&64)e.inline_array=1;
        if(mask&128)e.inline_elements=1;
        if(mask&256)e.inline_buffer=1;
        if(mask&512)e.reports=1;
        if(mask&1024)e.queries=1;
        if(mask&2048)e.ready=0;
        if(mask&4096)e.cpu0_done=0;
        if(mask&8192)e.cpu1_done=0;
        if(mask&16384)e.cpu0_count=1;
        if(mask&32768)e.cpu1_reason=1;
        if(mask&65536)e.render_fenced=0;
        if(mask&131072)e.contexts_match=0;
        assert((x274_admit(&e,1)==0)==(mask==0));checks++;
    }
    X274Evidence e=good;e.display_fenced=0;assert(x274_admit(&e,1));checks++;
    e=good;e.cpu0_reason=1;assert(x274_admit(&e,1));checks++;
    e=good;e.cpu1_count=1;assert(x274_admit(&e,1));checks++;
    e=good;e.original_owner=0;e.actual_owner=0;assert(x274_admit(&e,1));checks++;
    for(unsigned enabled=0;enabled<2;enabled++)for(unsigned busy=0;busy<4;busy++)
    for(unsigned terminal=0;terminal<4;terminal++)for(unsigned error=0;error<8;error++)
    for(unsigned owner=0;owner<3;owner++) {
        x269.enabled=enabled;x269.busy=busy;x269.terminal=terminal;x269.thread=91;
        x269.error=error&1;x269.core_error=(error>>1)&1;x269.transport_error=(error>>2)&1;
        uint64_t id=owner==0?0:owner==1?91:92;
        assert(pgraph_gl_reuse274_ready(id)==(enabled==1 && busy==0 && terminal==0 && error==0 && owner==1));checks++;
    }
    uint64_t rows[2][8]={{51,1,100,65538,65538,200,200,1},{51,2,101,65539,65539,201,201,1}};
    uint64_t after[3][8];memcpy(after,rows,sizeof(rows));memcpy(after[2],rows[0],sizeof(rows[0]));
    X265State a={.ledger={rows,2}},b={.ledger={after,2}};
    assert(x274_context_match(&a,&b));checks++;
    for(unsigned i=0;i<2;i++)for(unsigned j=0;j<8;j++) {
        after[i][j]^=1;assert(!x274_context_match(&a,&b));checks++;after[i][j]^=1;
    }
    b.ledger.count=3;assert(!x274_context_match(&a,&b));checks++;
    b.ledger.count=1;assert(!x274_context_match(&a,&b));checks++;
    b.ledger.count=2;rows[0][7]=0;after[0][7]=0;assert(!x274_context_match(&a,&b));checks++;
    printf("PASS %u actual admission/context checks; no live queue/GL coverage\\n",checks);
}
'''
    (out/'test.c').write_text(source)
    base='/mnt/e/Codex-archive/xbox-windows-native/boundary274-host001'
    c=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=c11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/test.c','-o',base+'/test'],capture_output=True,timeout=60)
    result.update(compile_exit=c.returncode,compile_output=(c.stdout+c.stderr).decode(errors='replace'));assert c.returncode==0
    t=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60)
    result.update(test_exit=t.returncode,test_output=(t.stdout+t.stderr).decode(errors='replace'));assert t.returncode==0
    result.update(passed=True,actual_functions_sha256=hashlib.sha256(functions.encode()).hexdigest())
except BaseException as error:result['error']=repr(error)
result['files']={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}
dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({x:y for x,y in result.items() if x!='files'},indent=2));assert result['passed']
