import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;dest=K/'source-review.json';assert not dest.exists()
old=Path('/home/paul/xbox-windows-native/build/memory-warm357-build001/source/win32ss/drivers/displays/framebuf');new=Path('/home/paul/xbox-windows-native/build/bandwidth361-build001/source/win32ss/drivers/displays/framebuf')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=[p.name for p in old.iterdir() if p.is_file() and p.read_bytes()!=(new/p.name).read_bytes()]
assert set(changed)=={'CMakeLists.txt','framebuf.h','ownership.c','enable.c','shadow.c','memory_warm.c'},changed
assert (old/'memory_warm.c').read_bytes().replace(b'\r\n',b'\n')==(new/'memory_warm.c').read_bytes()
s=(new/'shadow.c').read_text()
s=s.replace('#include <pseh/pseh2.h>\n','').replace('LONGLONG begin,finish; B361_CONTEXT bandwidth;','LONGLONG begin;').replace(' XwnBandwidthBegin(p,r,&bandwidth);\n','').replace('begin=XwnProfileStart();finish=-1;\n _SEH2_TRY {','begin=XwnProfileStart();').replace(' finish=XwnProfileStart();\n } _SEH2_FINALLY {\n','').replace(' XwnBandwidthEnd(p,&bandwidth,begin,finish);\n } _SEH2_END;\n','')
assert s==(old/'shadow.c').read_text()
s=(new/'ownership.c').read_text();assert s[:s.index('BOOL XwnBandwidthReserve')].rstrip()==(old/'ownership.c').read_text().rstrip()
assert (new/'capture.h').read_bytes()==(old/'capture.h').read_bytes()==(K/'capture.h').read_bytes()
for name in ['primary_copy.c','primary_plan.h','row_store.h','memory_state.c']:assert sha(old/name)==sha(new/name)
assert (K/'probe/gdi-probe.c').read_text().replace('    if(!bandwidth_capture())++Failures;\n','')==(K.parent/'memory-warm357/probe/gdi-probe.c').read_text()
b=json.loads((K/'build001.json').read_text());assert all(sha(new/n.split('/')[-1])==h for n,h in b['source_files'].items())
r=dict(passed=True,changed_parent_files=changed,added_files=['bandwidth.h','bandwidth.c'],parent_upload_reconstructed_exact=True,inherited_memory_warm_crlf_only=dict(before=sha(old/'memory_warm.c'),after=sha(new/'memory_warm.c')),original_copy_upload_capture_helpers_unchanged=True,
 source_tree=b['source_tree'],files={p.name:sha(p) for p in new.iterdir() if p.is_file()},no_shared_source_modified=True,no_new_scanout_store=True,
 limits='Diagnostic RAM allocation/copy and read-only mapping scans add latency/cache warming. Alternating order is diagnostic, not ordinary-performance isolation. Four records per boot, no reset; allocation and faults explicit. Native SEH finally frees scratch if original upload unwinds.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Actual original upload, ownership prefix, probe and helpers reconstruct exactly')
