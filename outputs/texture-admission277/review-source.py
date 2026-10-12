"""Pin the actual lifecycle/scheduling closure; no shared-source writes."""
import hashlib,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'source-review.json';assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/admission277-source001');out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
owned=Path('E:/Codex-archive/xbox-windows-native/callback276-build003/source')
pins=json.loads((k.parent/'callback-inventory276/renderer-source-pins003.json').read_text())
source='/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet'
names=['system/physmem.c','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pgraph/gl/renderer.c',
       'hw/xbox/nv2a/pgraph/gl/texture.c','include/qemu/queue.h','include/hw/core/cpu.h',
       'cpu-common.c','hw/core/cpu-common.c','hw/xbox/nv2a/pgraph/vk/surface.c']
texts={};files={}
for name in names:
    p=owned/name
    if p.is_file():data=p.read_bytes();assert sha(p)==pins[name]
    else:
        result=subprocess.run(['wsl','-d','Ubuntu','--','cat',source+'/'+name],capture_output=True,timeout=20)
        assert result.returncode==0;data=result.stdout
        if name in pins:assert hashlib.sha256(data).hexdigest()==pins[name]
    q=out/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
    texts[name]=data.decode();files[name]=sha(q)
p=texts['system/physmem.c'];work=texts['cpu-common.c'];gl=texts['hw/xbox/nv2a/pgraph/gl/surface.c']
assert p.count('QTAILQ_INSERT_TAIL(&cpu->mem_access_callbacks, cb, entry)')==1
assert p.count('QTAILQ_REMOVE(&cpu->mem_access_callbacks, cb, entry)')==1
assert p.count('async_safe_run_on_cpu(cpu, do_mem_access_callback_')==2
assert 'wi->exclusive = true;' in work
assert re.search(r'start_exclusive\(\);\s*wi->func\(cpu, wi->data\);\s*end_exclusive\(\);',work)
assert work.index('QSIMPLEQ_REMOVE_HEAD(&cpu->work_list, node);',work.index('void process_queued_cpu_work'))<work.index('wi->func(cpu, wi->data);',work.index('void process_queued_cpu_work'))
assert 'qemu_get_cpu(0), d->vram, surface->vram_addr, surface->size,' in gl
assert '&surface_access_callback, d);' in gl
assert texts['hw/core/cpu-common.c'].count('QTAILQ_INIT(&cpu->mem_access_callbacks);')==1
for test in ['host001.json','host002.json']:
    r=json.loads((k/test).read_text());assert r['passed']
    for name,digest in r['files'].items():assert sha(Path(name))==digest,name
assert sha(k/'admission.h')==sha(Path('E:/Codex-archive/xbox-windows-native/admission277-host002/admission.h'))
assert sha(k/'clock.c')==sha(Path('E:/Codex-archive/xbox-windows-native/admission277-host002/clock.c'))
r=dict(passed=True,scope='Proposed host-only texture admission, no actual adapter or renderer installed',
    source_files=files,private_source_root=str(out),
    exact_actual_insert_unlink_bodies_tested=True,exclusive_job_source_confirmed=True,
    queue_removed_before_execution=True,original_function_behavior_preserved=True,
    cpu_context_and_GL_acknowledgments_modeled_only=True,physical_changed=False,
    missing_runtime=['actual clock capture in CPU audit','paired locked surface graphs','attested request and actual texture keys','actual worker adapter and failure sequencing','immutable transport and independent decoder','fresh no-release guest reuse control'],
    unresolved_native_surface_provenance=2,old276_requalified=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='source_files'},indent=2))
