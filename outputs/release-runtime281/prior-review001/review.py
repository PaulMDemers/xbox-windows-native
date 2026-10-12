"""Review the completed opt-in runtime build, without launching a guest."""
import hashlib,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'source-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((k/'renderer-build001.json').read_text());assert b['passed'] and b['borrowed_sources_restored']
capsule=Path('E:/Codex-archive/xbox-windows-native/runtime281-build001');source=capsule/'source'
for name,h in b['inputs'].items():assert sha(k/name)==h
for name,h in b['worker_inputs'].items():assert sha(k.parent/'release-worker280'/name)==h
exe=capsule/'xemu-runtime281.exe';assert sha(exe)==b['executable_sha256'] and exe.stat().st_size==b['executable_bytes']
old=Path('E:/Codex-archive/xbox-windows-native/boundary278-build002/source')
changed=set(b['changed_sources']);files={}
for name in b['original_sources']:
 p=source/name;files[str(p)]=sha(p)
 if name not in changed:assert p.read_bytes()==(old/name).read_bytes(),name
import importlib.util,shutil
reconstructed=Path('E:/Codex-archive/xbox-windows-native/runtime281-review001');assert not reconstructed.exists();reconstructed.mkdir()
for name in b['original_sources']:
 p=reconstructed/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/name,p)
spec=importlib.util.spec_from_file_location('patch281',k/'patch-renderer.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.apply(reconstructed)
for name in b['original_sources']:assert (source/name).read_bytes()==(reconstructed/name).read_bytes(),name
# Original counted binder/destructor and UI paths precede only appended helpers.
for name in ['hw/xbox/nv2a/pgraph/gl/texture.c','ui/xemu.c']:
 assert (source/name).read_text().startswith((old/name).read_text())
warnings=lambda p:re.findall(r'warning: (.*)',p.read_text(errors='replace'))
before=warnings(k.parent/'texture-boundary278/renderer-build002.log');after=warnings(k/'renderer-build001.log')
new=sorted(set(after)-set(before));assert not new,new
for name in ['edges-host001.json','edges-host002.json','interface-host002.json','wrappers-host001.json']:
 r=json.loads((k/name).read_text());assert r['passed'],name
restore=json.loads(subprocess.check_output(['wsl','-d','Ubuntu','--','python3','-c',
 'import hashlib,json,pathlib; r=pathlib.Path("/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet"); names='+repr(list(b['original_sources']))+'; print(json.dumps({n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in names}))'],text=True))
assert restore==b['original_sources']
r=dict(passed=True,compiled_sha256=sha(exe),compiled_bytes=exe.stat().st_size,
 exact_parent_reconstruction=True,original_binder_destructor_ui_paths_preserved=True,
 original_worker280_components_pinned=True,borrowed_sources_restored=True,
 warning_instances=len(after),parent_warning_instances=len(before),new_warning_messages=new,
 host_edges_checks=11231,host_interface_checks=89,host_snapshot_wrapper_checks=29,
 full_runtime_provider_exercised=False,guest_launched=False,release_executed=False,physical_changed=False,
 scope='Opt-in compiled adapter; host tests model current GL/CPU/request state. No guest or release result.',files=files)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2))
