"""Exact inverse review and bounded observation-only admission checks."""
import hashlib,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'source-review.json';assert not dest.exists()
parent=Path('E:/Codex-archive/xbox-windows-native/boundary274-build002/source')
child=Path('E:/Codex-archive/xbox-windows-native/callback276-build003/source')
name='hw/xbox/nv2a/pgraph/gl/renderer.c';s=(child/name).read_text();original=(parent/name).read_text()
actual=(k/'inventory.c').read_text();assert s.endswith('\n'+actual);s=s[:-len(actual)-1]
pairs=[
('    uint64_t detail276[X260_CALLBACKS][3]; /* CPU-owned function,region,absolute RAM address */\n',''),
('        uint64_t *detail=a->detail276[a->count];\n        detail[0]=(uintptr_t)cb->func;detail[1]=(uintptr_t)cb->mr;detail[2]=cb->addr;\n',''),
('    bool observe276; /* Never arms texture lifetime observation. */\n',''),
('    if (s->observe276) {reason=27;goto finish;} /* no arm even if count unexpectedly zero */\n',''),
('    bool observe276=!strcmp(value,"observe276");\n',''),
('(!observe276 && strcmp(value,"capture,1"))','strcmp(value,"capture,1")'),
('    s->observe276=observe276;\n','')]
for a,b in pairs:assert s.count(a)==1;s=s.replace(a,b)
assert s==original,'Original full renderer must reconstruct exactly'
# Actual adjacent original refusal and new observation refusal must precede arm.
raw=(child/name).read_text();a=raw.index('    if (s->accounting_error || s->shader_jobs_unknown || v->cpu[0].count)');b=raw.index('    if (ending) {',a)
fragment=raw[a:b]
out=Path('E:/Codex-archive/xbox-windows-native/callback276-host004');out.mkdir(exist_ok=False)
c='''#include <assert.h>
#include <stdio.h>
typedef struct {unsigned accounting_error,shader_jobs_unknown,observe276;} S;
typedef struct {struct {unsigned count;} cpu[2];} V;
static unsigned check(S *s,V *v){unsigned reason=0;
'''+fragment+'''
return 0;finish:return reason;}
int main(void){unsigned tests=0;for(unsigned m=0;m<16;m++)for(unsigned n=0;n<258;n++){
 S s={m&1,(m>>1)&1,(m>>2)&1};V v={{{n},{0}}};
 unsigned r=check(&s,&v);assert(r==((s.accounting_error||s.shader_jobs_unknown||n)?14:s.observe276?27:0));tests++;
}printf("PASS %u actual no-arm branch cases\\n",tests);return 0;}
'''
(out/'test.c').write_text(c);base='/mnt/e/Codex-archive/xbox-windows-native/callback276-host004'
p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=c11','-Wall','-Wextra','-Werror','-O1','-fsanitize=address,undefined',base+'/test.c','-o',base+'/test'],capture_output=True,timeout=60);assert p.returncode==0,(p.stdout+p.stderr).decode()
p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60);assert p.returncode==0,(p.stdout+p.stderr).decode()
warning=lambda p:re.findall(r'warning: (.*)',p.read_text())
prior=warning(k.parent/'owner-boundary274/renderer-build002.log');now=warning(k/'renderer-build003.log')
assert set(now)<=set(prior)
build=json.loads((k/'renderer-build003.json').read_text());assert build['passed'] and build['borrowed_sources_restored']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(k/'inventory.c')==json.loads((k/'host-tests003.json').read_text())['files']['inventory.c']
files={str(p):sha(p) for p in child.rglob('*') if p.is_file()}
assert sha(child.parent/'xemu-callback276.exe')==build['executable_sha256']
for name,digest in build['inputs'].items():assert sha(k/name)==digest
r=dict(passed=True,original_renderer_reconstructed=True,actual_getter_host_tested=True,
    observation_no_arm_test_output=p.stdout.decode(),warning_instances=len(now),new_warning_messages=[],
    compiled_sha256=build['executable_sha256'],compiled_bytes=build['executable_bytes'],private_source_files=files,
    failed_build001_preserved=True,release_installed=False,guest_launched=False,
    limitations='Publication tests model persistent QEMU structs; no runtime CPU inventory, context fence or callback lifetime result yet')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='private_source_files'},indent=2))
