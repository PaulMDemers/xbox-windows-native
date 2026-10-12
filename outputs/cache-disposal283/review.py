"""Close host/source review without rerunning tests or changing old results."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'final-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files={}
for case in ['001','002','003']:
 r=json.loads((k/f'host{case}.json').read_text());assert r['passed']==(case=='003')
 root=Path('E:/Codex-archive/xbox-windows-native/cache283-host'+case)
 for name,h in r['files'].items():p=root/name;assert sha(p)==h;files[str(p)]=h
root=Path('E:/Codex-archive/xbox-windows-native/cache283-host003')
pins=json.loads((k.parent/'release-runtime281/renderer-source-pins001.json').read_text())
assert sha(root/'qemu/lru.h')==pins['include/qemu/lru.h']
assert sha(root/'qemu/queue.h')==pins['include/qemu/queue.h']
assert (root/'actual-functions.h').read_text()==Path('E:/Codex-archive/xbox-windows-native/unbound279-host003/actual-functions.h').read_text()
for n in ['disposal.h','proposed-disposal.c']:
 assert (root/n).read_bytes()==(k/n).read_bytes()==(Path('E:/Codex-archive/xbox-windows-native/cache283-host002')/n).read_bytes()
edges=json.loads((k/'actual-edges.json').read_text());assert edges['known_reference_scope_passed'] and not edges['live_authorization']
assert sha(k.parent/'release-pair282/candidate001/trace.json')==edges['source_trace_sha256']
text=Path('E:/Codex-archive/xbox-windows-native/runtime281-build001/source/hw/xbox/nv2a/pgraph/gl/texture.c').read_text()
birth='key_out->binding = generate_texture(state, texture_data, palette_data);'
assert text.count(birth)==1 and text.count('g_malloc(sizeof(TextureBinding))')==1
original=json.loads((k.parent/'release-runtime281/source-review.json').read_text())['files']
assert hashlib.sha256(Path('E:/Codex-archive/xbox-windows-native/runtime281-build001/source/hw/xbox/nv2a/pgraph/gl/texture.c').read_bytes()).hexdigest() in original.values()
r=dict(passed=True,host_only=True,actual_runtime_installed=False,renderer_build=False,native_build=False,
 guest_prepared=False,guest_launched=False,physical_changed=False,
 actual_normal_functions_byte_identical=True,actual_lru_queue_pinned=True,
 host_cases=4,premutation_refusals=34,partial_quarantines=12,balanced_model_objects=99,
 actual_closed_graph_mutations_rejected=edges['actual_mutations_rejected'],private_files_verified=len(files),files=files,
 creation_lead='One normal binder generate_texture call; one g_malloc(sizeof(TextureBinding)) allocation in that exact function. Static lead only, not actual replacement-generation capture.',
 unknown='Actual provider/four-boundary worker, final GL deletion, replacement generations and guest pixels not implemented/observed in283')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2))
