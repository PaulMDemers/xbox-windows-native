"""Exact worker lock ordering, copied publication and unchanged guest actions."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(k/'build001.json');pins=read(k/'candidate001-source-pins.json');old=k.parent/'xemu-wait-lifecycle233';baseline=read(old/'candidate002-source-pins.json')
assert b['passed'] and b['borrowed_sources_restored'] and len(b['original_sources'])==7
assert b['source_sha256']==sha(k/'build.py') and b['patch_generator_sha256']==sha(k/'patch.py')
assert b['source_manifest_sha256']==sha(k/'candidate001-source-pins.json') and b['patch_sha256']==sha(k/'snapshot234-build001.patch')
assert b['executable_sha256']==sha(k/'artifacts/build001/xemu-preserve227.exe')
changed=sorted(n for n in pins if pins[n]!=baseline[n]);assert changed==sorted(b['changed_sources'])
assert changed==sorted(['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/renderer.c'])
for p in (k/'artifacts/build001/source').rglob('*'):
 if p.is_file():assert sha(p)==pins[p.relative_to(k/'artifacts/build001/source').as_posix()]
src=k/'artifacts/build001/source';prior=old/'artifacts/build002/source'
nv=(src/'hw/xbox/nv2a/nv2a.c').read_text();base=(prior/'hw/xbox/nv2a/nv2a.c').read_text()
a=nv.index('/*234 ONE request');z=nv.index('static void nv2a_realize',a)
ab=base.index('/*233 read-only property');zb=base.index('static void nv2a_realize',ab)
s=nv[:a]+base[ab:zb]+nv[z:]
s=s.replace('    object_property_add_bool(OBJECT(d), "xwn-snapshot234",\n                             snapshot234_requested, snapshot234_request);\n    object_property_add_str(OBJECT(d), "xwn-snapshot234-report", snapshot234_report, NULL);','    object_property_add_str(OBJECT(d), "xwn-wait233-report", wait233_report, NULL);')
assert s==base,'Only replace observer, preserve reset/guest/preservation actions'
renderer=(src/'hw/xbox/nv2a/pgraph/gl/renderer.c').read_text();base=(prior/'hw/xbox/nv2a/pgraph/gl/renderer.c').read_text()
a=renderer.index('    /*234 worker enters');z=renderer.index('    /* Request is one-shot',a)
hook=renderer[a:z];assert renderer[:a]+renderer[z:]==base
assert hook.index('qemu_mutex_unlock(&d->pfifo.lock)')<hook.index('qemu_mutex_lock(&pg->lock)')<hook.index('nv2a_snapshot234_copy(d)')<hook.index('qemu_mutex_unlock(&pg->lock)')<hook.index('nv2a_snapshot234_publish(d)')<hook.index('qemu_mutex_lock(&d->pfifo.lock)')
assert 'bql_' not in hook
helper=nv[nv.index('/*234 ONE request'):nv.index('static void wait233_format')]
assert 'qemu_mutex_' not in helper and 'pfifo' not in helper
assert 'nv2a_wait233_fill(d, &d->snapshot234.current, 9, 0, false)' in helper
assert 'qatomic_store_release(&d->snapshot234.state, 3)' in helper and 'qatomic_cmpxchg(&d->snapshot234.state, 2, 7)' in helper
getter=nv[nv.index('static char *snapshot234_report'):nv.index('static void nv2a_realize')]
assert 'qemu_mutex_' not in getter and 'if (published)' in getter and 'bool published = state == 3' in getter
request=nv[nv.index('static void snapshot234_request'):nv.index('static bool snapshot234_requested')]
assert 'trylock' in request and 'qemu_mutex_lock(' not in request and 'halt' not in request
assert '!= 0' in request and 'qatomic_store_release(&d->snapshot234.state, 1)' in request
t=read(k/'test001.json');assert t['passed'] and len(t['runs'])==2 and all(row['exit_code']==0 and not row['stderr'] for row in t['runs'])
assert t['source_sha256']==sha(k/'test-snapshot.py') and t['test_sha256']==sha(k/'test-snapshot.c')
for n,digest in t['actual_helpers'].items():assert sha(k/'artifacts/test001'/n)==digest
assert read(k/'guard-test001.json')['passed'] and read(k/'powershell-syntax001.json')['passed']
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
f=read(k/'fixture-trace002.json');assert f['prepared'] and not f['inherited_null_policy'];assert sha(Path(f['fixture_path_windows']))==f['seed_sha256']
assert not (k/'trace002/runner-start.json').exists()
dest.write_text(json.dumps(dict(passed=True,changed_sources=changed,ordinary_guest_reset_parser_preservation_actions_unchanged=True,worker_fifo_released_before_pg=True,worker_current_fifo_valid=False,getter_touches_no_mutable_journal=True,one_shot_publication_timeout_hidden=True,actual_helpers_host_checked=True,source_manifest_sha256=sha(k/'candidate001-source-pins.json'),executable_sha256=b['executable_sha256'],physical_access=False,guest_launch=False),indent=2)+'\n')
print('234 worker lock/publication/source review PASS')
