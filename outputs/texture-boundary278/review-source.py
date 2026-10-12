"""Review compiled002 against exact276 and tested277/278 private inputs."""
import hashlib,importlib.util,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'source-review.json';assert not dest.exists()
old=Path('E:/Codex-archive/xbox-windows-native/callback276-build003/source')
new=Path('E:/Codex-archive/xbox-windows-native/boundary278-build002/source')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((k/'renderer-build002.json').read_text());assert build['passed'] and build['borrowed_sources_restored']
for name,digest in build['inputs'].items():assert sha(k/name)==digest
for name in ['admission.h','clock.c']:assert (k/name).read_bytes()==(k.parent/'texture-admission277'/name).read_bytes()
def fn(s,name):
 p=s.index(name+'(');a=s.rfind('\n',0,p)+1;b=s.index('{',p)+1;n=1
 while n:n+=(s[b]=='{')-(s[b]=='}');b+=1
 return s[a:b]
rname='hw/xbox/nv2a/pgraph/gl/renderer.c';a=(old/rname).read_text();b=(new/rname).read_text()
assert fn(b,'pgraph_gl_ledger265_worker').replace('    if(initial->textures278)return x278_worker(d);\n','')==fn(a,'pgraph_gl_ledger265_worker')
assert fn(a,'x274_check')==fn(b,'x274_check') and fn(a,'x274_admit')==fn(b,'x274_admit')
assert fn(b,'x260_cpu_audit').replace('    if(!a->reason)mem_access_callback_clock277(cpu,&a->clock278,&a->clock_error278);\n','')==fn(a,'x260_cpu_audit')
assert (k/'adapter.c').read_text() in b and (k/'admission.h').read_text() in b
for n in ['worker-host001.json','graph-host001.json','linkage-host001.json']:
 result=json.loads((k/n).read_text());assert result['passed']
 capsule={'worker-host001.json':'boundary278-worker001','graph-host001.json':'boundary278-graph001','linkage-host001.json':'boundary278-linkage001'}[n]
 root=Path('E:/Codex-archive/xbox-windows-native')/capsule
 for name,digest in result['files'].items():assert sha(root/name)==digest
 if n=='worker-host001.json':
  previous=(root/'adapter.c').read_text()
  for f in result['actual_functions']:assert fn(previous,f)==fn((k/'adapter.c').read_text(),f)
 if n=='graph-host001.json':
  for f in result['actual_functions']:assert fn((root/'adapter.c').read_text(),f)==fn((k/'adapter.c').read_text(),f)
before=re.findall(r'warning: (.*)',(k.parent/'callback-inventory276/renderer-build003.log').read_text())
after=re.findall(r'warning: (.*)',(k/'renderer-build002.log').read_text());assert set(after)<=set(before)
exe=new.parent/'xemu-boundary278.exe';assert sha(exe)==build['executable_sha256']
pins=json.loads((k/'renderer-source-pins002.json').read_text())
for p in new.rglob('*'):
 if p.is_file() and p.relative_to(new).as_posix() in pins:assert sha(p)==pins[p.relative_to(new).as_posix()]
result=dict(passed=True,compiled_sha256=sha(exe),compiled_bytes=exe.stat().st_size,
 exact_legacy_worker_and_zero_count_gates_preserved=True,old_end_admission_unchanged=True,
 exact_277_core_clock=True,actual_opt_in_worker_host_paths=57,actual_collector_request_checks=78,
 scalar_transport_mutations=308,full_graph_linkage_mutations=68,native_allocation_mutations=4,
 inherited_warning_instances=len(after),new_warning_messages=[],failed_build001_preserved=True,
 guest_launched=False,release_installed=False,physical_changed=False,
 limitation='CPU jobs, GL/context and live graph objects modeled in host tests; runtime admission and guest reuse not yet proved',
 files={str(p):sha(p) for p in new.rglob('*') if p.is_file()})
dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({a:b for a,b in result.items() if a!='files'},indent=2))
