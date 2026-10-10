"""Review exact observer placement/locks and unchanged functional parser code."""
import ast,hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review002.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(k/'build002.json');pins=read(k/'candidate002-source-pins.json');old=read(k.parent/'xemu-backend-consume232/candidate001-source-pins.json')
assert b['passed'] and b['borrowed_sources_restored'] and len(b['original_sources'])==7
assert b['source_sha256']==sha(k/'build002.py') and b['patch_generator_sha256']==sha(k/'patch002.py')
assert b['source_manifest_sha256']==sha(k/'candidate002-source-pins.json')
assert b['executable_sha256']==sha(k/'artifacts/build002/xemu-preserve227.exe')
changed=sorted(n for n in pins if pins[n]!=old[n]);assert changed==sorted(b['changed_sources'])
assert changed==sorted(['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/pgraph.c'])
for p in (k/'artifacts/build002/source').rglob('*'):
    if p.is_file():assert sha(p)==pins[p.relative_to(k/'artifacts/build002/source').as_posix()]
pg=(k/'artifacts/build002/source/hw/xbox/nv2a/pgraph/pgraph.c').read_text()
baseline=(k.parent/'xemu-backend-consume232/artifacts/wait-source001/pgraph.c').read_text()
a=pg.index('/*233 caller ALREADY');z=pg.index('uint64_t pgraph_read',a)
stripped=pg[:a]+pg[z:]
stripped=re.sub(r'^[ \t]*nv2a_wait233_record\([^\n]+\);\n','',stripped,flags=re.M)
assert stripped==baseline,'Observer must not alter ordinary PGRAPH operations'
nv=(k/'artifacts/build002/source/hw/xbox/nv2a/nv2a.c').read_text()
baseline=(k.parent/'xemu-backend-consume232/artifacts/build001/source/hw/xbox/nv2a/nv2a.c').read_text()
a=nv.index('/*233 read-only property');z=nv.index('static void nv2a_realize',a)
stripped=nv[:a]+nv[z:]
stripped=re.sub(r'^[ \t]*nv2a_wait233_record\([^\n]+\);\n','',stripped,flags=re.M)
stripped=stripped.replace('    object_property_add_str(OBJECT(d), "xwn-wait233-report", wait233_report, NULL);\n','')
assert stripped==baseline,'Observer must not alter original reset/preservation operations'
assert 'qemu_mutex_trylock(&d->pfifo.lock)' in nv and 'qemu_mutex_trylock(&d->pgraph.lock)' in nv
helper=pg[pg.index('void nv2a_wait233_fill'):pg.index('uint64_t pgraph_read')]
assert 'qemu_mutex_' not in helper and '& NV_PGRAPH_FIFO_ACCESS' in helper
assert 'if (fifo_valid)' in helper and 'UINT64_MAX' in helper
assert not read(k/'test001.json')['passed'] and read(k/'test002.json')['passed']
t=read(k/'test002.json');assert len(t['runs'])==2 and all(row['exit_code']==0 and not row['stderr'] for row in t['runs'])
assert t['source_sha256']==sha(k/'test-wait.py') and t['test_sha256']==sha(k/'test-wait.c')
assert read(k/'guard-test001.json')['passed']
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
f=read(k/'fixture-trace001.json');assert f['prepared'] and not f['inherited_null_policy']
assert sha(Path(f['fixture_path_windows']))==f['seed_sha256']
assert not (k/'trace001/runner-start.json').exists()
dest.write_text(json.dumps(dict(passed=True,changed_sources=changed,preliminary_mask_failure_preserved=True,ordinary_pgraph_reset_preservation_operations_unchanged=True,actual_parser_gl_and_atomic_headers_unchanged=True,record_helpers_acquire_no_locks=True,source_manifest_sha256=sha(k/'candidate002-source-pins.json'),executable_sha256=b['executable_sha256'],physical_access=False,guest_launch=False),indent=2)+'\n')
print('233 observer placement/lock/source review PASS')
