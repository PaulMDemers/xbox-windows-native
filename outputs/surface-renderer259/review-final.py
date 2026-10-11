"""Close259 compilation checkpoint. This cannot qualify a runtime pixel test."""
import hashlib,json,re,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(k/'build001.json');p=read(k/'probe-review001.json');a=read(k/'admission-review002.json');x=read(k/'renderer-build001.json')
assert all(v['passed'] for v in [b,p,a,x]) and x['borrowed_sources_restored']
for n,h in b['input_pins'].items():assert sha(k/n)==h,n
for n,h in a['inputs'].items():assert sha(k/n)==h,n
for n,h in x['inputs'].items():assert sha(k/n)==h,n
for n,h in read(k/'admission-review001.json')['inputs'].items():assert sha(k/'prior-admission001'/n)==h,n
assert sha(k/'artifacts/build001/probe.exe')==b['native_sha256']==p['native_sha256']
art=Path('E:/Codex-archive/xbox-windows-native/renderer259-build001')
assert sha(art/'xemu-renderer259.exe')==x['executable_sha256']
pins=read(k/'renderer-source-pins001.json');parent=k.parent/'surface-invalidation257/artifacts/build002/source'
changed=[]
for name in x['original_sources']:
    here=art/'source'/name;assert sha(here)==pins[name]
    if here.read_bytes()!=(parent/name).read_bytes():changed.append(name)
assert changed==x['changed_sources']
surface=Path('hw/xbox/nv2a/pgraph/gl/surface.c');header=Path('hw/xbox/nv2a/pgraph/gl/renderer.h')
assert (art/'source'/surface).read_bytes().startswith((parent/surface).read_bytes())
assert (art/'source'/header).read_text().startswith((parent/header).read_text()[:-len('#endif\n')])
occurrences=[]
for file in (art/'source').rglob('*'):
    if file.is_file():
        for line,text in enumerate(file.read_text().splitlines(),1):
            if re.search(r'\bpgraph_gl_pattern259_stage\s*\(',text):occurrences.append(dict(file=file.relative_to(art).as_posix(),line=line,text=text.strip()))
assert len(occurrences)==2 and all(v['text'].startswith('unsigned pgraph_gl_pattern259_stage') for v in occurrences)
capture=read(k/'source-review001.json');assert capture['passed']
for n,v in capture['files'].items():assert sha(k/'source'/n)==v['sha256']
log=(k/'renderer-build001.log').read_text();warnings=[v for v in log.splitlines() if 'warning:' in v]
parent_warnings={v.split('warning:',1)[1] for v in (k.parent/'surface-invalidation257/build002.log').read_text().splitlines() if 'warning:' in v}
new_warnings=[v for v in warnings if v.split('warning:',1)[1] not in parent_warnings]
assert not new_warnings,new_warnings
r=dict(passed=True,physical_access=False,guest_prepared=False,guest_launched=False,gl_executed=False,
    cpu_callback_coverage=False,pixel_preservation_proved=False,renderer_command_hook_installed=False,
    ordinary_qualified=False,native_gpu_ownership=False,
    source_sha256=sha(Path(__file__)),native_probe_sha256=b['native_sha256'],renderer_sha256=x['executable_sha256'],
    changed_renderer_sources=changed,internal_declaration_and_definition_only=occurrences,
    prior_admission001_inputs_preserved=True,source_closure_files=len(capture['files']),
    sanitizer_result=a['result'],independent_expected_bytes=p['exact_independent_bytes'],
    negative_controls=len(p['negative_controls']),inherited_warning_instances=len(warnings),new_warning_instances=len(new_warnings),
    all_owned_sessions_closed=[44179],next='Implement coherent CPU/renderer reference collector and bounded sequential bridge before preparing a unique runtime child.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('259 compilation checkpoint reviewed; no guest launch/GL/callback/preservation claim')
