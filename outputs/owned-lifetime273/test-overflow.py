"""Actual adapter overflow preserves reserved lifecycles but never qualifies."""
import hashlib,json,subprocess
from pathlib import Path
from decode import decode
k=Path(__file__).resolve().parent;out=Path('E:/Codex-archive/xbox-windows-native/lifetime273-host004');out.mkdir(exist_ok=False)
prior=Path('E:/Codex-archive/xbox-windows-native/lifetime273-host002');r=json.loads((k/'host-tests002.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['lifetime.h','wire.h','actual-test.c']:
    assert sha(prior/name)==r['files'][name];(out/name).write_bytes((prior/name).read_bytes())
source=(out/'actual-test.c').read_text().replace('int main(int argc,char **argv)','void prior_main(int argc,char **argv)')
source+='''
int main(int argc,char **argv) {
    assert(argc==2);setup();NV2AState d={0};
    for(unsigned i=0;i<140;i++)x269_destroying(&bindings[i%2]);
    assert(x269.accounting.run_count==128 && x269.accounting.error==L270_OVERFLOW);
    for(unsigned i=0;i<4;i++) {
        x269_bound(&d,i,&bindings[i],2);bindings[i].refcnt=1;
        x269_destroying(&bindings[i]);bindings[i].dead=1;
        assert(x269.accounting.watch[i].has_bind && x269.accounting.watch[i].has_free);
    }
    assert(x269.accounting.sequence==148);L270 old=x269.accounting;
    for(unsigned i=0;i<4;i++){x269_bound(&d,i,&bindings[i],1);x269_destroying(&bindings[i]);}
    assert(!memcmp(&old,&x269.accounting,sizeof(old)));
    uint8_t bytes[X273_CAPACITY];X273Meta m={0,0,1,2,0,1,15};
    for(unsigned n=0;n<X273_CAPACITY;n++) {
        memset(bytes,0xcc,sizeof(bytes));assert(!x273_encode(&old,&m,bytes,n));
        for(unsigned j=0;j<sizeof(bytes);j++)assert(bytes[j]==0xcc);
    }
    assert(x273_encode(&old,&m,bytes,sizeof(bytes))==X273_CAPACITY);
    output_file=argv[1];assert(pgraph_gl_reuse269_seal());assert(pgraph_gl_reuse269_error());
    assert(atomic_load(&x269.terminal)==2 && !l270_complete(&x269.accounting));
    puts("PASS actual overflow:128run cap,4reserved first/final lifecycles,148seq,tombstones,8960short buffers unchanged; terminal still FAILED");
    return 0;
}
'''
(out/'test.c').write_text(source)
base='/mnt/e/Codex-archive/xbox-windows-native/lifetime273-host004'
c=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/test.c','-o',base+'/test'],capture_output=True,timeout=60)
result=dict(passed=False,compile_exit=c.returncode,compile_output=(c.stdout+c.stderr).decode(errors='replace'),actual_adapter_from_host002=True,guest_executed=False)
if not c.returncode:
    t=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test',base+'/overflow.bin'],capture_output=True,timeout=60)
    result.update(test_exit=t.returncode,test_output=(t.stdout+t.stderr).decode(errors='replace'))
    if not t.returncode:
        try:decode((out/'overflow.bin').read_bytes())
        except AssertionError as e:result.update(passed=True,independent_parser_refused=repr(e))
result['files']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
dest=k/'host-tests004.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({n:v for n,v in result.items() if n!='files'},indent=2));assert result['passed']
