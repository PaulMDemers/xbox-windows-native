"""Required QOM parent remains first; detect original compiled244 mistake."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'layout-test001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bad=k.parent/'gpu-lifecycle244/artifacts/build004/source/hw/xbox/nv2a/nv2a_int.h'
good=k/'artifacts/build005/source/hw/xbox/nv2a/nv2a_int.h'
def parent_first(p):
 text=p.read_text();body=text[text.index('typedef struct NV2AState {')+len('typedef struct NV2AState {'):]
 first=re.sub(r'/\*.*?\*/','',body.split(';',1)[0],flags=re.S).strip()
 return first=='PCIDevice parent_obj'
assert not parent_first(bad) and parent_first(good)
assert 'G_STATIC_ASSERT(offsetof(NV2AState, parent_obj) == 0);' in good.read_text()
b=json.loads((k/'build005.json').read_text());assert b['passed'] and b['borrowed_sources_restored']
dest.write_text(json.dumps(dict(passed=True,checks=3,bad_source_sha256=sha(bad),actual_compiled_good_source_sha256=sha(good),actual_compile_assertion=True,source_sha256=sha(Path(__file__)),guest_launch=False,physical_access=False),indent=2)+'\n')
print('245 actual compiled QOM parent-offset guard PASS;244 bad layout detected')
